import os
import time
import psycopg2
from werkzeug.security import generate_password_hash

# --- 1. RÉCUPÉRATION SÉCURISÉE DES VARIABLES ---
# Ces variables sont injectées par Docker Compose depuis le fichier .env
# Si une variable manque, le script s'arrête net (Fail Secure).

try:
    # Note: Dans docker-compose, on a mappé POSTGRES_USER vers DB_USER, etc.
    DB_HOST = os.environ.get('DB_HOST', 'api_db') # Par défaut le nom du service docker
    DB_NAME = os.environ['DB_NAME']
    DB_USER = os.environ['DB_USER']
    DB_PASS = os.environ['DB_PASS']
except KeyError as e:
    print(f"🔴 ERREUR CRITIQUE : La variable d'environnement {e} est manquante !")
    print("   Vérifiez que votre docker-compose.yaml passe bien les variables.")
    exit(1)

# --- 2. CONNEXION AVEC TENTATIVES (RETRY LOGIC) ---
def get_db_connection():
    """Tente de se connecter à la BDD. Réessaie 5 fois si elle n'est pas prête."""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            return conn
        except psycopg2.OperationalError:
            print(f"⏳ La Base de données n'est pas encore prête. Nouvelle tentative dans 3s... ({retries} essais restants)")
            time.sleep(3)
            retries -= 1
            
    raise Exception("❌ IMPOSSIBLE de se connecter à la base de données après plusieurs essais.")

# --- 3. INITIALISATION DES TABLES ---
def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Table UTILISATEURS
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Table SERVEURS MINECRAFT
        cur.execute("""
            CREATE TABLE IF NOT EXISTS minecraft_servers (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                server_name VARCHAR(80) NOT NULL,
                docker_container_id VARCHAR(255) NOT NULL,
                public_port INTEGER NOT NULL,
                version VARCHAR(20) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'running',
                memory VARCHAR(10) DEFAULT '512M',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(server_name)
            );
        """)

        conn.commit()
        print("✅ Base de données initialisée avec succès (Tables créées).")

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la BDD : {e}")
    finally:
        if conn:
            conn.close()

# Ce bloc permet de tester la connexion en lançant juste "python database.py"
if __name__ == '__main__':
    print("Test de connexion BDD...")
    # Note: Cela ne marchera que si lancé DANS le conteneur ou si localhost est configuré
    try:
        init_db()
    except:
        print("Test échoué (Normal si hors Docker).")