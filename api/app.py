from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import database as db
import docker
import random 
import psycopg2
import os

app = Flask(__name__)
# IMPORTANT: Changez cette clé secrète! Elle est utilisée pour sécuriser les sessions utilisateur.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'CLEF_SECRETE_PAR_DEFAUT_A_CHANGER') 

# --- Initialisation du client Docker ---
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"Erreur lors de la connexion au démon Docker: {e}")
    docker_client = None

# --- Fonctions d'Aide Docker (Contrôle) ---
def deploy_minecraft_server(user_id, server_name, version, memory="512M"):
    """Déploie un nouveau conteneur Minecraft et enregistre son état en BDD."""
    if not docker_client: return None, "Docker client non disponible."
    
    # 1. Vérifier l'unicité du nom du serveur pour cet utilisateur
    try:
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM minecraft_servers WHERE server_name = %s AND user_id = %s", (server_name, user_id))
        if cur.fetchone()[0] > 0:
            conn.close()
            return None, "Un serveur portant ce nom existe déjà pour cet utilisateur."
    except Exception as e:
        return None, f"Erreur de BDD lors de la vérification : {e}"

    # 2. Trouver un port public libre (de 25566 à 26000)
    public_port = random.randint(25566, 26000)
    
    # 3. Lancer le conteneur
    container_name = f"mc-{server_name}-{user_id}"
    host_volume_path = f'/home/maskass/minecraft-automation/servers/{server_name}'

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
                'MOTD': f"Serveur de {server_name} ({version})",
            },
            volumes={
                host_volume_path: {'bind': '/data', 'mode': 'rw'}
            },
            restart_policy={'Name': 'unless-stopped'}
        )
        
        # 4. Enregistrer dans la BDD
        cur.execute(
            "INSERT INTO minecraft_servers (user_id, server_name, docker_container_id, public_port, version, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, server_name, container.id, public_port, version, 'running')
        )
        conn.commit()
        conn.close()
        
        return container.id, public_port
    except docker.errors.APIError as e:
        conn.close()
        return None, f"Erreur Docker lors du déploiement: {e}"
    except Exception as e:
        conn.close()
        return None, f"Erreur générale : {e}"

def stop_minecraft_server(user_id, server_name):
    """Arrête un conteneur et met à jour le statut dans la BDD."""
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
        
        cur.execute(
            "UPDATE minecraft_servers SET status = 'stopped' WHERE docker_container_id = %s",
            (container_id,)
        )
        conn.commit()
        conn.close()
        return True, "Serveur arrêté avec succès."
    except docker.errors.NotFound:
        conn.close()
        return False, "Conteneur Docker non trouvé."
    except Exception as e:
        conn.close()
        return False, f"Erreur lors de l'arrêt Docker/BDD: {e}"

def start_minecraft_server(user_id, server_name):
    """Démarre un conteneur arrêté et met à jour le statut dans la BDD."""
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
        
        cur.execute(
            "UPDATE minecraft_servers SET status = 'running' WHERE docker_container_id = %s",
            (container_id,)
        )
        conn.commit()
        conn.close()
        return True, "Serveur démarré avec succès."
    except docker.errors.NotFound:
        conn.close()
        return False, "Conteneur Docker non trouvé."
    except Exception as e:
        conn.close()
        return False, f"Erreur lors du démarrage Docker/BDD: {e}"


def delete_minecraft_server(user_id, server_name):
    """Arrête et supprime un conteneur et l'enregistrement de la BDD."""
    
    stop_success, stop_message = stop_minecraft_server(user_id, server_name)
    
    if not stop_success and "déjà arrêté" not in stop_message and "Conteneur Docker non trouvé" not in stop_message:
        return False, f"Impossible de supprimer: {stop_message}"

    conn = db.get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT docker_container_id FROM minecraft_servers WHERE user_id = %s AND server_name = %s",
        (user_id, server_name)
    )
    record = cur.fetchone()
    
    if record:
        container_id = record[0]
        
        try:
            container = docker_client.containers.get(container_id)
            container.remove(force=True) 
        except docker.errors.NotFound:
            pass 
            
        cur.execute(
            "DELETE FROM minecraft_servers WHERE docker_container_id = %s",
            (container_id,)
        )
        conn.commit()
        conn.close()
        
        return True, "Serveur supprimé avec succès."

    conn.close()
    return False, "Serveur non trouvé."
    
# --- Routes Flask (Définies dans l'ordre pour éviter BuildError) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Gère la connexion de l'utilisateur."""
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
            flash('Nom d\'utilisateur ou mot de passe invalide.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Gère la déconnexion de l'utilisateur."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Vous êtes déconnecté.', 'success')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Gère l'inscription de l'utilisateur."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash('Veuillez remplir tous les champs.', 'danger')
            return render_template('register.html')
            
        hashed_password = generate_password_hash(password, method='scrypt')
        
        conn = db.get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
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
def create_server():
    """Crée un nouveau serveur Minecraft via Docker."""
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour créer un serveur.', 'danger')
        return redirect(url_for('login'))

    server_name = request.form['server_name']
    version = request.form['version']
    memory = request.form.get('memory', '384M') # Utilise 384M par défaut pour la VM 1GiO
    
    container_id, port_or_error = deploy_minecraft_server(
        session['user_id'], server_name, version, memory
    )
    
    if container_id:
        flash(f'Serveur "{server_name}" créé sur le port {port_or_error} ! (IP: 20.199.43.125)', 'success')
    else:
        flash(f'Échec de la création du serveur : {port_or_error}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/stop_server/<server_name>')
def stop_server(server_name):
    """Arrête le conteneur d'un serveur spécifique."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    success, message = stop_minecraft_server(session['user_id'], server_name)
    
    if success:
        flash(f'Serveur "{server_name}" arrêté.', 'success')
    else:
        flash(f'Échec de l\'arrêt du serveur : {message}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/start_server/<server_name>')
def start_server(server_name):
    """Démarre le conteneur d'un serveur spécifique."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    success, message = start_minecraft_server(session['user_id'], server_name)
    
    if success:
        flash(f'Serveur "{server_name}" démarré.', 'success')
    else:
        flash(f'Échec du démarrage du serveur : {message}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/delete_server/<server_name>')
def delete_server(server_name):
    """Supprime le conteneur et l'enregistrement du serveur."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    success, message = delete_minecraft_server(session['user_id'], server_name)
    
    if success:
        flash(f'Serveur "{server_name}" supprimé et retiré de la liste.', 'success')
    else:
        flash(f'Échec de la suppression du serveur : {message}', 'danger')
        
    return redirect(url_for('index'))

@app.route('/')
def index():
    """Page d'accueil et tableau de bord des serveurs."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = db.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT server_name, public_port, version, status FROM minecraft_servers WHERE user_id = %s", (session['user_id'],))
    servers = cur.fetchall()
    conn.close()
    
    return render_template('index.html', username=session['username'], servers=servers)


if __name__ == '__main__':
    db.init_db() 
    app.run(debug=True, host='0.0.0.0', port=5000)
