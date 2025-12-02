from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import database as db
import docker
import random 
import psycopg2
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'CLEF_DEV_1234')

# --- SÉCURITÉ : Rate Limiting (Anti-Spam) ---
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1000 per day", "100 per hour"],
    storage_uri="memory://"
)

# --- SÉCURITÉ : Whitelists (Listes Blanches) ---
ALLOWED_MEMORY = ['512M', '1G', '2G']
ALLOWED_VERSIONS = ['1.21.8', '1.20.1', '1.19.4']

# --- Initialisation Docker ---
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"ERREUR CRITIQUE: Impossible de contacter Docker. {e}")
    docker_client = None

# --- Fonctions Utilitaires ---

def is_valid_server_name(name):
    """SÉCURITÉ: Regex pour empêcher les injections de commandes"""
    pattern = re.compile(r"^[a-z0-9-]{3,20}$")
    return bool(pattern.match(name))

def deploy_minecraft_server(user_id, server_name, version, memory="512M"):
    if not docker_client: return None, "Docker indisponible."

    # 1. Validation des entrées
    if not is_valid_server_name(server_name):
        return None, "Nom invalide (3-20 chars, a-z, 0-9, - uniquement)."
    if version not in ALLOWED_VERSIONS:
        return None, "Version non autorisée."
    if memory not in ALLOWED_MEMORY:
        return None, "RAM non autorisée."

    conn = db.get_db_connection()
    cur = conn.cursor()

    # 2. SÉCURITÉ : Vérification du Quota (Max 2 serveurs)
    cur.execute("SELECT COUNT(*) FROM minecraft_servers WHERE user_id = %s AND status = 'running'", (user_id,))
    if cur.fetchone()[0] >= 2:
        conn.close()
        return None, "Quota atteint (Max 2 serveurs actifs)."

    # 3. Vérification unicité nom
    cur.execute("SELECT COUNT(*) FROM minecraft_servers WHERE server_name = %s", (server_name,))
    if cur.fetchone()[0] > 0:
        conn.close()
        return None, "Ce nom de serveur est déjà pris."

    # 4. Déploiement
    public_port = random.randint(25566, 26000) # Idéalement, vérifier si le port est libre
    container_name = f"mc-{server_name}-{user_id}"
    
    # Chemin dynamique compatible Docker Compose
    base_path = os.environ.get('MINECRAFT_BASE_PATH', '/app/minecraft_data')
    host_volume_path = os.path.join(base_path, server_name)

    try:
        os.makedirs(host_volume_path, exist_ok=True)
        
        container = docker_client.containers.run(
            image='itzg/minecraft-server',
            detach=True,
            name=container_name,
            ports={'25565/tcp': public_port},
            environment={
                'EULA': 'TRUE',
                'TYPE': 'PAPER',
                'VERSION': version,
                'MEMORY': memory,
                'MOTD': f"Serveur de {server_name}"
            },
            volumes={
                host_volume_path: {'bind': '/data', 'mode': 'rw'}
            },
            restart_policy={'Name': 'unless-stopped'}
        )
        
        cur.execute(
            "INSERT INTO minecraft_servers (user_id, server_name, docker_container_id, public_port, version, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, server_name, container.id, public_port, version, 'running')
        )
        conn.commit()
        return container.id, public_port

    except Exception as e:
        return None, f"Erreur technique: {e}"
    finally:
        conn.close()

# --- Routes Flask ---

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute") # Anti Brute-force
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user_record = cur.fetchone()
        conn.close()
        
        if user_record and check_password_hash(user_record[1], password):
            session['user_id'] = user_record[0]
            session['username'] = username
            flash('Connexion réussie!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Identifiants invalides.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour") # Anti Spam de comptes
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password, method='scrypt')
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
            conn.commit()
            flash('Compte créé ! Connectez-vous.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Ce pseudo est déjà pris.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/create_server', methods=['POST'])
@limiter.limit("5 per hour")
def create_server():
    if 'user_id' not in session: return redirect(url_for('login'))

    # Nettoyage et validation basique
    server_name = request.form['server_name'].strip().lower()
    version = request.form['version']
    memory = request.form.get('memory', '512M')

    cid, msg = deploy_minecraft_server(session['user_id'], server_name, version, memory)
    
    if cid:
        flash(f'Serveur "{server_name}" en cours de création sur le port {msg} !', 'success')
    else:
        flash(f'Erreur : {msg}', 'danger')
        
    return redirect(url_for('index'))

# SÉCURITÉ : Actions critiques en POST uniquement (pas de GET)
@app.route('/action/<action_type>/<server_name>', methods=['POST'])
def server_action(action_type, server_name):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT docker_container_id FROM minecraft_servers WHERE user_id = %s AND server_name = %s", 
                (session['user_id'], server_name))
    record = cur.fetchone()
    
    if not record:
        flash("Serveur introuvable.", "danger")
        return redirect(url_for('index'))

    container_id = record[0]
    msg = ""

    try:
        container = docker_client.containers.get(container_id)
        
        if action_type == 'stop':
            container.stop(timeout=5)
            cur.execute("UPDATE minecraft_servers SET status='stopped' WHERE docker_container_id=%s", (container_id,))
            msg = "Serveur arrêté."
            
        elif action_type == 'start':
            container.start()
            cur.execute("UPDATE minecraft_servers SET status='running' WHERE docker_container_id=%s", (container_id,))
            msg = "Serveur démarré."
            
        elif action_type == 'delete':
            try: container.remove(force=True)
            except: pass
            cur.execute("DELETE FROM minecraft_servers WHERE docker_container_id=%s", (container_id,))
            msg = "Serveur supprimé définitivement."
            
        conn.commit()
        flash(msg, 'success')

    except Exception as e:
        flash(f"Erreur Docker: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('index'))

@app.route('/logs/<server_name>')
def show_logs(server_name):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT docker_container_id FROM minecraft_servers WHERE user_id = %s AND server_name = %s", 
                (session['user_id'], server_name))
    record = cur.fetchone()
    conn.close()

    if not record: return redirect(url_for('index'))
    
    try:
        container = docker_client.containers.get(record[0])
        logs = container.logs(tail=100).decode('utf-8')
    except:
        logs = "Serveur arrêté ou introuvable."

    return render_template('logs.html', server_name=server_name, logs_content=logs, success=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT server_name, public_port, version, status, memory FROM minecraft_servers WHERE user_id = %s", (session['user_id'],))
    servers = cur.fetchall() # Note: J'ai ajouté memory dans la requête pour info si besoin
    conn.close()
    
    return render_template('index.html', username=session['username'], servers=servers)

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)