import psycopg2
import time
import os
from werkzeug.security import generate_password_hash

DB_HOST = os.environ.get('DB_HOST', 'api-database')
DB_NAME = os.environ.get('DB_NAME', 'server_manager_db')
DB_USER = os.environ.get('DB_USER', 'api_user')
DB_PASS = os.environ.get('DB_PASS', 'secret_password')

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
            return conn
        except psycopg2.OperationalError:
            print("Base de données pas encore prête, attente...")
            time.sleep(2)
            retries -= 1
    raise Exception("Impossible de se connecter à la BDD après plusieurs essais.")

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """)
        
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("✅ Base de données initialisée.")
    except Exception as e:
        print(f"❌ Erreur Init DB: {e}")
    finally:
        if conn: conn.close()