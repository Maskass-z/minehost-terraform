# Utiliser l'image de base Python officielle
FROM python:3.11-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /home/app

# Copier les fichiers de dépendances et installer
# requirements.txt sera créé à l'étape suivante.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'API (app.py, database.py, templates)
COPY . .

# Exposer le port par défaut de Flask
EXPOSE 5000

# Commande pour démarrer l'API Flask (elle initialise aussi la BDD au démarrage)
CMD ["python", "app.py"]

