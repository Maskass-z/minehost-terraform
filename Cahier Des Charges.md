# CAHIER DES CHARGES TECHNIQUE  
**PROJET MINEHOST : Infrastructure Cloud-Native Azure & Sécurité Offensive**

**Projet** : Plateforme SaaS d'Hébergement de Serveurs de Jeux  
**Date** : 07 Janvier 2026  
**Version** : 2.1 (Architecture Finale)  
**Cible** : Direction Technique, Équipe DevOps, Audit de Sécurité  
**Classification** : CONFIDENTIEL

## SOMMAIRE

1. [PRÉSENTATION DU PROJET & OBJECTIFS](#1-présentation-du-projet--objectifs)  
   1.1. Vision et Proposition de Valeur  
   1.2. Périmètre Fonctionnel (SaaS)  
   1.3. Contraintes de Sécurité et Performance  

2. [ARCHITECTURE LOGICIELLE (BACKEND & API)](#2-architecture-logicielle-backend--api)  
   2.1. Stack Technologique (Python/Flask)  
   2.2. Logique d'Orchestration  
   2.3. Sécurisation du Code (AppSec)  

3. [INFRASTRUCTURE CLOUD (AZURE NATIVE)](#3-infrastructure-cloud-azure-native)  
   3.1. Choix du Compute : Azure Container Instances (ACI)  
   3.2. Stratégie de Stockage : Azure Files (Persistance)  
   3.3. Réseau et Isolation : VNet & Private Link  

4. [STRATÉGIE DE SÉCURITÉ (DEFENSE IN DEPTH)](#4-stratégie-de-sécurité-defense-in-depth)  
   4.1. Approche "Zero Trust" & Cloaking VPN  
   4.2. Durcissement des Conteneurs (Docker Hardening)  
   4.3. Gestion des Secrets et Identités  

5. [MODÈLE ÉCONOMIQUE & FINOPS](#5-modèle-économique--finops)  
   5.1. Utilisation des Instances Spot  
   5.2. Algorithme d'Auto-Shutdown  

6. [ADMINISTRATION & MAINTENABILITÉ](#6-administration--maintenabilité)  
   6.1. Infrastructure as Code (Terraform)  
   6.2. Monitoring et Observabilité  

---

## 1. PRÉSENTATION DU PROJET & OBJECTIFS

### 1.1. Vision et Proposition de Valeur

MineHost est une plateforme d'hébergement automatisée (PaaS/SaaS) dédiée aux serveurs Minecraft. Le projet répond à une double problématique du marché actuel :

- L'insécurité des hébergeurs low-cost : Souvent basés sur des VPS mutualisés mal isolés.
- La complexité technique : La difficulté pour un utilisateur lambda de gérer Linux et Docker.

**Notre promesse** : Fournir une instance de jeu isolée, performante et sécurisée en moins de 60 secondes, avec une tarification à la seconde d'utilisation.

### 1.2. Périmètre Fonctionnel (SaaS)

La plateforme permet à l'utilisateur final de :

- Créer un compte et s'authentifier de manière sécurisée
- Commander un serveur en choisissant ses spécifications (RAM, Version Minecraft)
- Démarrer, Arrêter et Supprimer son serveur via une interface Web
- Accéder à la console de logs en temps réel
- Se connecter au jeu via un tunnel sécurisé

### 1.3. Contraintes de Sécurité et Performance

Le cahier des charges impose des contraintes strictes issues de l'audit initial :

- **Isolation stricte** : Aucun client ne doit pouvoir impacter les ressources d'un autre (Noisy Neighbor Effect)
- **Surface d'attaque minimale** : L'infrastructure doit être invisible depuis l'internet public (Cloaking)
- **Robustesse API** : Protection contre les injections de commandes et le Brute-Force

## 2. ARCHITECTURE LOGICIELLE (BACKEND & API)

Le cœur logique de MineHost repose sur une API RESTful développée en interne, assurant l'interface entre le client Web et l'infrastructure Azure.

### 2.1. Stack Technologique (Python/Flask)

Le choix s'est porté sur **Python 3.11** avec le framework **Flask** pour sa légèreté et sa capacité à s'interfacer nativement avec les SDK Cloud.

- **API Gateway** : Flask gère les routes HTTP (`/create`, `/start`, `/stop`)
- **Base de Données** : PostgreSQL (Hébergé sur Azure Database for PostgreSQL). Elle stocke :
  - Les utilisateurs (Mots de passe hachés via Scrypt)
  - L'inventaire des serveurs (UUID, Ports, État)
  - Les logs d'audit
- **Frontend** : Interface HTML5/JS rendue via le moteur de template Jinja2, incluant une protection automatique contre les failles XSS

### 2.2. Logique d'Orchestration

L'API agit comme un "Chef d'Orchestre". Elle ne fait pas tourner le jeu elle-même, mais pilote Azure.

**Workflow de Création** :

1. Réception de la requête POST validée
2. Appel au SDK azure-mgmt-resource pour créer un Groupe de Ressources
3. Appel au SDK azure-storage-file pour créer le volume persistant
4. Appel au SDK azure-mgmt-containerinstance pour lancer le conteneur Docker

### 2.3. Sécurisation du Code (AppSec)

Mesures intégrées nativement :

- **Input Sanitization (Regex)** : Validation stricte des noms de serveur (`^[a-z0-9-]{3,20}$`)
- **Rate Limiting** : Flask-Limiter → blocage après 5 tentatives de connexion échouées / minute
- **Contrôle de Propriété** : Middleware vérifiant l'ownership avant toute action (Start/Stop/Delete)

## 3. INFRASTRUCTURE CLOUD (AZURE NATIVE)

Abandon du modèle "VM Permanente" au profit d'une architecture **Serverless Container**.

### 3.1. Choix du Compute : Azure Container Instances (ACI)

- Chaque serveur Minecraft = un **Container Group** indépendant
- Isolation au niveau hyperviseur (micro-VM légère)
- Image : `itzg/minecraft-server`
- Ressources : allocation dynamique (ex. 2 vCPU, 4GB RAM)

### 3.2. Stratégie de Stockage : Azure Files (Persistance)

- File Share unique par serveur (ex: `user12-srv01-data`)
- Monté dans le conteneur sur `/data`
- Stockage redondant (LRS)

### 3.3. Réseau et Isolation : VNet & Private Link

- Déploiement dans un sous-réseau privé (`10.0.2.0/24`)
- NSG stricts : seul le port 25565 autorisé (et uniquement via VPN)

## 4. STRATÉGIE DE SÉCURITÉ (DEFENSE IN DEPTH)

### 4.1. Approche "Zero Trust" & Cloaking VPN

- Aucune IP publique exposée
- Connexion via tunnel **OpenVPN** obligatoire (certificats clients)
- Infrastructure invisible pour Shodan / Botnets

### 4.2. Durcissement des Conteneurs (Docker Hardening)

- User non-root (UID 1000)
- Capabilities drop (CAP_NET_ADMIN, CAP_SYS_ADMIN révoqués)
- Base Alpine Linux → surface d'attaque réduite

### 4.3. Gestion des Secrets et Identités

- Secrets injectés via variables d'environnement
- Azure Key Vault en production (rotation automatique)

## 5. MODÈLE ÉCONOMIQUE & FINOPS

### 5.1. Utilisation des Instances Spot

- Jusqu'à -70% sur le coût d'infrastructure
- Redéploiement automatique en < 30s en cas d'éviction

### 5.2. Algorithme d'Auto-Shutdown

- Watchdog RCON toutes les 5 min
- Arrêt après 15 min sans joueur → coût = 0€

## 6. ADMINISTRATION & MAINTENABILITÉ

### 6.1. Infrastructure as Code (Terraform)

- Déploiement reproductible
- Disaster Recovery rapide (changement de région en 1 commande)

### 6.2. Monitoring et Observabilité

- Logs → Azure Log Analytics
- Alerting sur CPU anormal, tentatives d'intrusion, etc.

## ANNEXE : EXEMPLE DE DÉFINITION TECHNIQUE (Pseudocode API)

```python
# Exemple de logique de création sécurisée (Backend Python)
def create_server_instance(user_id, server_name, ram_size):
    # 1. Validation de sécurité (Regex)
    if not re.match(r"^[a-z0-9-]{3,20}$", server_name):
        raise SecurityException("Nom de serveur invalide (Risque Injection)")

    # 2. Vérification Quota
    if get_user_server_count(user_id) >= 5:
        raise QuotaExceededException("Limite de serveurs atteinte")

    # 3. Appel Azure (Création Volume Persistant)
    volume_name = f"vol-{user_id}-{uuid.uuid4().hex[:8]}"
    azure_client.storage.create_share(share_name=volume_name)

    # 4. Appel Azure (Déploiement ACI en mode Spot)
    container_group = ContainerGroup(
        location="francecentral",
        containers=[
            Container(
                name="minecraft",
                image="itzg/minecraft-server",
                resources=ResourceRequests(memory_in_gb=ram_size, cpu=2.0),
                environment_variables=[
                    EnvironmentVariable(name="EULA", value="TRUE"),
                    EnvironmentVariable(name="VERSION", value="LATEST")
                ],
                volume_mounts=[VolumeMount(name="data", mount_path="/data")]
            )
        ],
        restart_policy="OnFailure",
        priority="Spot" # Optimisation FinOps
    )
    
    azure_client.container_instance.create_or_update(resource_group, server_name, container_group)
    return {"status": "creating", "ip": "VPN Required"}
