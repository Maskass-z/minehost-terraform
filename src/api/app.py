from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import shutil
import database as db
import docker
import random
import psycopg2
import os
import re
import secrets
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps

app = Flask(__name__)


SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
if not SECRET_KEY:
    print("❌ ERREUR: FLASK_SECRET_KEY non définie!")
    print("Exécutez: export FLASK_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')")
    exit(1)

app.secret_key = SECRET_KEY

app.config.update(
    SESSION_COOKIE_SECURE=False,  
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600  
)

MAX_SERVERS_PER_USER = 5
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)
SERVER_IP = os.environ.get('SERVER_IP', '10.8.0.2')

try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Erreur lors de la connexion au démon Docker: {e}")
    docker_client = None


login_attempts = defaultdict(list)

def is_rate_limited(identifier):
    """Vérifie si l'identifiant est rate-limited."""
    now = datetime.now()
    login_attempts[identifier] = [
        attempt for attempt in login_attempts[identifier]
        if now - attempt < LOCKOUT_DURATION
    ]
    
    return len(login_attempts[identifier]) >= MAX_LOGIN_ATTEMPTS

def record_failed_attempt(identifier):
    """Enregistre une tentative échouée."""
    login_attempts[identifier].append(datetime.now())


def validate_server_name(server_name):
    """Valide que le nom du serveur est sûr."""
    if not server_name:
        return False, "Le nom du serveur ne peut pas être vide"
    
    if not isinstance(server_name, str):
        return False, "Le nom du serveur doit être une chaîne de caractères"
    
    if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', server_name):
        return False, "Nom invalide. Utilisez 3-50 caractères: lettres, chiffres, - ou _"
    
    if '..' in server_name or '/' in server_name or '\\' in server_name:
        return False, "Caractères interdits détectés"
    
    return True, "OK"

def validate_version(version):
    """Valide que la version Minecraft est autorisée."""
    ALLOWED_VERSIONS = ['1.21', '1.20.1', '1.19.4', '1.18.2', '1.17.1', '1.16.5', 'LATEST']
    if version not in ALLOWED_VERSIONS:
        return False, f"Version non autorisée. Versions disponibles: {', '.join(ALLOWED_VERSIONS)}"
    return True, "OK"

def validate_memory(memory):
    """Valide la configuration mémoire."""
    if not re.match(r'^\d+[MG]$', memory):
        return False, "Format mémoire invalide (ex: 512M ou 2G)"
    
    value = int(memory[:-1])
    unit = memory[-1]
    
    value_mb = value if unit == 'M' else value * 1024
    
    if value_mb < 256:
        return False, "Mémoire minimale: 256M"
    if value_mb > 4096:
        return False, "Mémoire maximale: 4G"
    
    return True, "OK"

def validate_command(command):
    """Autorise toutes les commandes Minecraft mais protège le système hôte."""
    if not command or len(command) > 500:
        return False, "Commande vide ou trop longue (max 500 caractères)"

    
    dangerous_chars = [';', '&&', '||', '`', '$', '(', ')', '<', '>']
    if any(char in command for char in dangerous_chars):
        return False, "Caractères système interdits détectés pour la sécurité de l'hôte"

    return True, "OK"

def verify_server_ownership(user_id, server_name):
    """Vérifie que le serveur appartient bien à l'utilisateur."""
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM minecraft_servers WHERE user_id = %s AND server_name = %s",
        (user_id, server_name)
    )
    result = cur.fetchone()
    conn.close()
    return result is not None


def login_required(f):
    """Décorateur pour protéger les routes nécessitant une authentification."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Veuillez vous connecter pour accéder à cette page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Décorateur pour protéger les routes admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin', False):
            flash("Accès refusé. Droits administrateur requis.", 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_all_servers():
    """Récupère la liste de TOUS les serveurs."""
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            s.server_name,
            s.version,
            s.public_port,
            s.status,
            u.username,
            s.docker_container_id
        FROM minecraft_servers s
        JOIN users u ON s.user_id = u.id
    """)
    servers = cur.fetchall()
    conn.close()
    return servers

def deploy_minecraft_server(user_id, server_name, version, memory="512M"):
    """Déploie un nouveau conteneur Minecraft de façon sécurisée."""
    if not docker_client:
        return None, "Docker client non disponible."

    is_valid, error_msg = validate_server_name(server_name)
    if not is_valid:
        return None, error_msg

    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM minecraft_servers WHERE server_name = %s", (server_name,))
    if cur.fetchone()[0] > 0:
        conn.close()
        return None, f"Le nom '{server_name}' est déjà utilisé par un autre serveur."

    cur.execute("SELECT COUNT(*) FROM minecraft_servers WHERE user_id = %s", (user_id,))
    if cur.fetchone()[0] >= MAX_SERVERS_PER_USER:
        conn.close()
        return None, f"Limite de {MAX_SERVERS_PER_USER} serveurs atteinte."
    conn.close()

    max_retries = 10
    public_port = None
    for _ in range(max_retries):
        temp_port = random.randint(25566, 26000)
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM minecraft_servers WHERE public_port = %s", (temp_port,))
        if cur.fetchone()[0] == 0:
            public_port = temp_port
            conn.close()
            break
        conn.close()

    if not public_port:
        return None, "Impossible de trouver un port libre."

    container_name = f"mc-{server_name}-{user_id}"
    base_path = '/home/maskass/minecraft-automation/servers'
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
                'TYPE': 'VANILLA',
                'VERSION': version,
                'MEMORY': memory,
                'MOTD': f"Serveur {server_name}",
            },
            volumes={
                host_volume_path: {'bind': '/data', 'mode': 'rw'}
            },
            restart_policy={'Name': 'unless-stopped'}
        )

        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO minecraft_servers (user_id, server_name, docker_container_id, public_port, version, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, server_name, container.id, public_port, version, 'running')
        )
        conn.commit()
        conn.close()
        return container.id, public_port

    except Exception as e:
        return None, f"Erreur critique: {str(e)[:100]}"

def stop_minecraft_server(user_id, server_name):
    """Arrête un conteneur de façon sécurisée."""
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT docker_container_id FROM minecraft_servers WHERE user_id = %s AND server_name = %s AND status = 'running'",
        (user_id, server_name)
    )
    record = cur.fetchone()
    if not record:
        conn.close()
        return False, "Serveur non trouvé ou déjà arrêté."

    container_id = record[0]
    try:
        container = docker_client.containers.get(container_id)
        container.stop(timeout=10)
        cur.execute("UPDATE minecraft_servers SET status = 'stopped' WHERE docker_container_id = %s", (container_id,))
        conn.commit()
        conn.close()
        return True, "Serveur arrêté."
    except Exception as e:
        conn.close()
        return False, str(e)

def start_minecraft_server(user_id, server_name):
    """Démarre un conteneur arrêté."""
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT docker_container_id FROM minecraft_servers WHERE user_id = %s AND server_name = %s AND status = 'stopped'",
        (user_id, server_name)
    )
    record = cur.fetchone()
    if not record:
        conn.close()
        return False, "Serveur non trouvé ou déjà démarré."

    container_id = record[0]
    try:
        container = docker_client.containers.get(container_id)
        container.start()
        cur.execute("UPDATE minecraft_servers SET status = 'running' WHERE docker_container_id = %s", (container_id,))
        conn.commit()
        conn.close()
        return True, "Serveur démarré."
    except Exception as e:
        conn.close()
        return False, str(e)

def delete_minecraft_server(user_id, server_name):
    """Supprime le conteneur ET les fichiers."""
    stop_minecraft_server(user_id, server_name)
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT docker_container_id FROM minecraft_servers WHERE user_id = %s AND server_name = %s", (user_id, server_name))
    record = cur.fetchone()

    if record:
        container_id = record[0]
        try:
            container = docker_client.containers.get(container_id)
            container.remove(force=True)
        except: pass

        base_path = '/home/maskass/minecraft-automation/servers'
        host_volume_path = os.path.join(base_path, server_name)
        if os.path.exists(host_volume_path):
            shutil.rmtree(host_volume_path)

        cur.execute("DELETE FROM minecraft_servers WHERE docker_container_id = %s", (container_id,))
        conn.commit()
        conn.close()
        return True, "Serveur supprimé."
    conn.close()
    return False, "Serveur non trouvé."

def get_server_logs(user_id, server_name, tail=100):
    """Logs du conteneur."""
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT docker_container_id, public_port FROM minecraft_servers WHERE user_id = %s AND server_name = %s", (user_id, server_name))
    record = cur.fetchone()
    conn.close()
    if not record: return "Serveur non trouvé.", False

    try:
        container = docker_client.containers.get(record[0])
        logs = container.logs(tail=tail).decode('utf-8')
        return f"--- Logs de {server_name} --- IP: {SERVER_IP}:{record[1]} ---\n\n" + logs, True
    except: return "Erreur logs.", False

def send_minecraft_command(user_id, server_name, command):
    """RCON command."""
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT docker_container_id FROM minecraft_servers WHERE user_id = %s AND server_name = %s AND status = 'running'", (user_id, server_name))
    record = cur.fetchone()
    conn.close()
    if not record: return "Serveur arrêté.", False

    try:
        container = docker_client.containers.get(record[0])
        exit_code, output = container.exec_run(['rcon-cli', command], user='1000')
        return output.decode('utf-8').strip(), (exit_code == 0)
    except: return "Erreur RCON.", False

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion avec rate limiting."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Veuillez remplir tous les champs.', 'danger')
            return render_template('login.html')
        
        if is_rate_limited(username):
            flash('Trop de tentatives. Réessayez dans 15 minutes.', 'danger')
            return render_template('login.html')
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, password, is_admin FROM users WHERE username = %s", (username,))
        user_record = cur.fetchone()
        conn.close()
        
        if user_record and check_password_hash(user_record[1], password):
            session['user_id'] = user_record[0]
            session['username'] = username
            session['is_admin'] = user_record[2]
            session.permanent = True
            flash('Connexion réussie!', 'success')
            return redirect(url_for('index'))
        else:
            record_failed_attempt(username)
            flash('Identifiants invalides.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion."""
    session.clear()
    flash('Vous êtes déconnecté.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Veuillez remplir tous les champs.', 'danger')
            return render_template('register.html')
        
        if len(username) < 3 or len(username) > 50:
            flash('Le nom d\'utilisateur doit contenir 3-50 caractères.', 'danger')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères.', 'danger')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password, method='scrypt')
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            flash('Inscription réussie ! Vous pouvez vous connecter.', 'success')
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            flash('Nom d\'utilisateur déjà pris.', 'danger')
            return render_template('register.html')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/create_server', methods=['POST'])
@login_required
def create_server():
    """Crée un serveur avec toutes les validations."""
    server_name = request.form.get('server_name', '').strip()
    version = request.form.get('version', '').strip()
    memory = request.form.get('memory', '512M')
    
    is_valid, error_msg = validate_server_name(server_name)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    is_valid, error_msg = validate_version(version)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    is_valid, error_msg = validate_memory(memory)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    container_id, port_or_error = deploy_minecraft_server(
        session['user_id'], server_name, version, memory
    )
    
    if container_id:
        flash(f'Serveur "{server_name}" créé sur le port {port_or_error}! (IP: {SERVER_IP})', 'success')
    else:
        flash(f'Échec: {port_or_error}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/stop_server/<server_name>')
@login_required
def stop_server(server_name):
    """Arrête un serveur après vérifications."""
    is_valid, error_msg = validate_server_name(server_name)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    if not verify_server_ownership(session['user_id'], server_name):
        flash("Accès refusé. Ce serveur ne vous appartient pas.", 'danger')
        return redirect(url_for('index'))
    
    success, message = stop_minecraft_server(session['user_id'], server_name)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('index'))

@app.route('/start_server/<server_name>')
@login_required
def start_server(server_name):
    """Démarre un serveur après vérifications."""
    is_valid, error_msg = validate_server_name(server_name)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    if not verify_server_ownership(session['user_id'], server_name):
        flash("Accès refusé. Ce serveur ne vous appartient pas.", 'danger')
        return redirect(url_for('index'))
    
    success, message = start_minecraft_server(session['user_id'], server_name)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('index'))

@app.route('/delete_server/<server_name>')
@login_required
def delete_server(server_name):
    """Supprime un serveur après vérifications."""
    is_valid, error_msg = validate_server_name(server_name)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    if not verify_server_ownership(session['user_id'], server_name):
        flash("Accès refusé. Ce serveur ne vous appartient pas.", 'danger')
        return redirect(url_for('index'))
    
    success, message = delete_minecraft_server(session['user_id'], server_name)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('index'))

@app.route('/logs/<server_name>')
@login_required
def show_logs(server_name):
    """Affiche les logs après vérifications."""
    is_valid, error_msg = validate_server_name(server_name)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    if not verify_server_ownership(session['user_id'], server_name):
        flash("Accès refusé. Ce serveur ne vous appartient pas.", 'danger')
        return redirect(url_for('index'))
    
    logs_content, success = get_server_logs(session['user_id'], server_name)
    return render_template('logs.html', server_name=server_name, logs_content=logs_content, success=success)

@app.route('/command/<server_name>', methods=['POST'])
@login_required
@admin_required
def send_command(server_name):
    """Envoie une commande après toutes les validations."""
    is_valid, error_msg = validate_server_name(server_name)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('index'))
    
    if not verify_server_ownership(session['user_id'], server_name):
        flash("Accès refusé. Ce serveur ne vous appartient pas.", 'danger')
        return redirect(url_for('index'))
    
    command = request.form.get('command', '').strip()
    
    is_valid, error_msg = validate_command(command)
    if not is_valid:
        flash(error_msg, 'danger')
        return redirect(url_for('show_logs', server_name=server_name))
    
    message, success = send_minecraft_command(session['user_id'], server_name, command)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('show_logs', server_name=server_name))

@app.route('/admin_panel')
@login_required
@admin_required
def admin_panel():
    """Panneau admin."""
    all_servers = get_all_servers()
    return render_template('admin_panel.html', all_servers=all_servers, username=session['username'])

@app.route('/')
@login_required
def index():
    """Page d'accueil."""
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT server_name, public_port, version, status FROM minecraft_servers WHERE user_id = %s",
        (session['user_id'],)
    )
    servers = cur.fetchall()
    conn.close()
    
    return render_template('index.html', username=session['username'], servers=servers, server_ip=SERVER_IP)


if __name__ == '__main__':
    db.init_db()
    print("✅ Application démarrée en mode sécurisé")
    print(f"📊 Limite de serveurs par utilisateur: {MAX_SERVERS_PER_USER}")
    print(f"🔒 Rate limiting activé: {MAX_LOGIN_ATTEMPTS} tentatives max")
    app.run(debug=True, host='0.0.0.0', port=5000)

