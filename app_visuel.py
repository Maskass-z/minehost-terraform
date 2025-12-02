import sqlite3
import os
import random
import time
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- CONFIGURATION ---
app = Flask(__name__)
app.secret_key = 'CLE_DE_TEST_LOCALE'

# Anti-Spam (Mocké en mémoire)
limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")

# --- 1. SIMULATION DE LA BDD (SQLite) ---
DB_FILE = "test_local.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # Création des tables version SQLite
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS minecraft_servers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            server_name TEXT NOT NULL,
            docker_container_id TEXT NOT NULL,
            public_port INTEGER NOT NULL,
            version TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running',
            memory TEXT DEFAULT '512M'
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Base de données locale (SQLite) initialisée.")

# --- 2. SIMULATION DE DOCKER ---
# On fait croire au site que Docker répond
class FakeContainer:
    def __init__(self, id): self.id = id
    def stop(self, timeout=0): pass
    def start(self): pass
    def remove(self, force=False): pass
    def logs(self, tail=100): return b"[SIMULATION] Serveur Minecraft demarre...\n[INFO] Loading libraries, please wait...\n[INFO] Done (3.456s)!"

def deploy_fake_server(user_id, server_name, version, memory):
    time.sleep(1) # On simule le temps de chargement
    fake_id = f"fake_container_{random.randint(1000,9999)}"
    fake_port = random.randint(25566, 26000)
    return fake_id, fake_port

# --- ROUTES DU SITE WEB (Identiques à la version Prod) ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        cur = conn.cursor()
        # Note: SQLite utilise ? au lieu de %s
        cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user_record = cur.fetchone()
        conn.close()
        
        if user_record and check_password_hash(user_record[1], password):
            session['user_id'] = user_record[0]
            session['username'] = username
            flash('Connexion réussie (Mode Test)!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Identifiants invalides.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed = generate_password_hash(password, method='scrypt')
        
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            conn.commit()
            flash('Compte créé ! Connectez-vous.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Ce pseudo est déjà pris.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/create_server', methods=['POST'])
def create_server():
    if 'user_id' not in session: return redirect(url_for('login'))

    server_name = request.form['server_name']
    version = request.form['version']
    memory = request.form.get('memory', '512M')

    # Simulation déploiement
    cid, port = deploy_fake_server(session['user_id'], server_name, version, memory)
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO minecraft_servers (user_id, server_name, docker_container_id, public_port, version, status, memory) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (session['user_id'], server_name, cid, port, version, 'running', memory)
    )
    conn.commit()
    conn.close()
    
    flash(f'Serveur "{server_name}" créé (SIMULATION) sur le port {port} !', 'success')
    return redirect(url_for('index'))

@app.route('/action/<action_type>/<server_name>', methods=['POST'])
def server_action(action_type, server_name):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT docker_container_id FROM minecraft_servers WHERE user_id = ? AND server_name = ?", 
                (session['user_id'], server_name))
    record = cur.fetchone()
    
    if not record:
        flash("Serveur introuvable.", "danger")
    else:
        # On met juste à jour la BDD pour faire semblant
        if action_type == 'stop':
            cur.execute("UPDATE minecraft_servers SET status='stopped' WHERE docker_container_id=?", (record[0],))
            flash("Serveur arrêté (Simulation).", 'success')
        elif action_type == 'start':
            cur.execute("UPDATE minecraft_servers SET status='running' WHERE docker_container_id=?", (record[0],))
            flash("Serveur démarré (Simulation).", 'success')
        elif action_type == 'delete':
            cur.execute("DELETE FROM minecraft_servers WHERE docker_container_id=?", (record[0],))
            flash("Serveur supprimé (Simulation).", 'success')
        conn.commit()
    
    conn.close()
    return redirect(url_for('index'))

@app.route('/logs/<server_name>')
def show_logs(server_name):
    if 'user_id' not in session: return redirect(url_for('login'))
    # Logs factices
    fake_logs = f"""[10:00:00] [Server thread/INFO]: Starting minecraft server version 1.20.1
[10:00:01] [Server thread/INFO]: Loading properties
[10:00:02] [Server thread/INFO]: Default game type: SURVIVAL
[10:00:03] [Server thread/INFO]: Generating keypair
[10:00:05] [Server thread/INFO]: Starting Minecraft server on *:25565
[10:00:10] [Server thread/INFO]: Done (5.203s)! For help, type "help"
--- CECI EST UNE SIMULATION POUR TEST VISUEL ---
    """
    return render_template('logs.html', server_name=server_name, logs_content=fake_logs, success=True)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT server_name, public_port, version, status, memory FROM minecraft_servers WHERE user_id = ?", (session['user_id'],))
    servers = cur.fetchall()
    conn.close()
    
    return render_template('index.html', username=session['username'], servers=servers)

if __name__ == '__main__':
    init_db()
    print("🚀 MODE SIMULATION ACTIVÉ : Ouvre ton navigateur sur http://127.0.0.1:5000")
    app.run(debug=True, port=5000)