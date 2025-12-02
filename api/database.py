import psycopg2
from werkzeug.security import generate_password_hash

DB_HOST = "api-database" # Nom du service Docker Compose
DB_NAME = "server_manager_db"
DB_USER = "api_user"
DB_PASS = "secret_password"

# Cette fonction essaie de se connecter à la BDD
def get_db_connection():
    # Remarque : Le script va attendre la disponibilité de la BDD.
    # Dans un environnement de production, on utiliserait une boucle de tentative.
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

# Initialise les tables
def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Table des Utilisateurs
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            );
        """)
        
        # 2. Table des Serveurs Minecraft créés
        cur.execute("""
            CREATE TABLE IF NOT EXISTS minecraft_servers (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                server_name VARCHAR(80) UNIQUE NOT NULL,
                docker_container_id VARCHAR(255) NOT NULL,
                public_port INTEGER UNIQUE NOT NULL,
                version VARCHAR(10) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'running'
            );
        """)

        # Créer un utilisateur Admin par défaut si la table est vide
        cur.execute("SELECT COUNT(*) FROM users;")
        if cur.fetchone()[0] == 0:
            # Mot de passe par défaut sera 'admin'
            hashed_password = generate_password_hash('admin', method='scrypt') 
            cur.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
                ('admin', hashed_password, True)
            )

        conn.commit()
        print("Base de données initialisée (tables créées et utilisateur admin créé).")

    except Exception as e:
        # Nous allons voir cette erreur si la BDD n'est pas prête lors de l'exécution
        print(f"Erreur d'initialisation de la BDD: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Ceci est exécuté par le Dockerfile lors du lancement du conteneur API
    init_db()
