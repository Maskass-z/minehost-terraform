Voici la version **sans aucun emoji**, contenu et structure conservés.

---

# MineHost - Plateforme d'Hébergement Minecraft Sécurisée

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com)
[![Security](https://img.shields.io/badge/Security-Zero%20Trust%20VPN-blue)](https://github.com)
[![Azure](https://img.shields.io/badge/Cloud-Azure-0078D4)](https://azure.microsoft.com)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED)](https://www.docker.com)

**Plateforme SaaS d'hébergement de serveurs Minecraft** avec architecture cloud-native Azure, isolation Docker et sécurité Zero Trust via VPN obligatoire.

---

## Sommaire

* Vue d'ensemble
* Architecture
* Démarrage rapide
* Guide utilisateur
* Administration
* Sécurité
* Performance et monitoring
* Documentation complète
* Équipe

---

## Vue d'ensemble

### Problème résolu

Les hébergeurs Minecraft actuels souffrent de :

* Insécurité : attaques DDoS, accès non autorisés
* Complexité : configuration technique requise (SSH, CLI)
* Performance instable : mutualisation anarchique (Noisy Neighbor Effect)

### Solution proposée

* Sécurité maximale : Zero Trust + VPN obligatoire (infrastructure non exposée à Internet)
* Simplicité : interface web, provisioning en moins de 2 minutes
* Isolation garantie : Docker + NSG + Azure Files dédiés
* Tarification juste : facturation à la seconde d'utilisation réelle

### Indicateurs clés

* Provisioning : < 2 minutes
* Sécurité : aucune IP publique exposée, accès 100 % via VPN
* Coût : 9,99 €/mois (2 Go RAM) avec arrêt automatique
* Scalabilité : 10 à 15 serveurs par VM, ajout automatique de VMs

---

## Architecture

### Stack technique

```
INTERNET
   |
Azure VPN Gateway (OpenVPN, certificats X.509)
   |
VNet Azure 10.0.0.0/16
   |
Subnet VMs (10.0.2.0/24)
- VM-01 Docker (10–15 conteneurs)
- VM-02 Docker (10–15 conteneurs)
- VM-03 Docker (10–15 conteneurs)
   |
Subnet Data (10.0.3.0/24)
- PostgreSQL
- Azure Files
```

### Composants principaux

| Composant       | Technologie                    | Rôle                                |
| --------------- | ------------------------------ | ----------------------------------- |
| Frontend        | Vue.js 3, Tailwind CSS         | Interface utilisateur               |
| Backend API     | Python 3.11, Flask, SQLAlchemy | Orchestration Docker                |
| Base de données | PostgreSQL 15                  | Utilisateurs, serveurs, facturation |
| Compute         | Azure VM D4s_v3                | Hébergement conteneurs              |
| Isolation       | Docker Engine 24               | Namespaces et cgroups               |
| Stockage        | Azure Files Premium            | Persistance des données             |
| Sécurité        | OpenVPN, NSG, Key Vault        | Zero Trust                          |
| Monitoring      | Azure Monitor, Grafana         | Supervision                         |
| IaC             | Terraform 1.6                  | Déploiement infrastructure          |

### Isolation multi-niveaux

**Niveau réseau**

* NSG bloquant tout accès Internet vers les VMs
* VPN obligatoire avec certificats X.509
* Aucune IP publique

**Niveau VM**

* Ubuntu 24.04
* Hardening OS
* Accès admin via Azure Bastion

**Niveau Docker**

* Namespaces PID, NET, MNT, IPC
* Limites CPU, mémoire, PID
* Exécution non-root
* RootFS en lecture seule

**Niveau stockage**

* Azure Files par serveur
* Chiffrement AES-256
* Snapshots quotidiens

---

## Démarrage rapide

### Prérequis

* Compte Azure actif
* Terraform >= 1.6
* Azure CLI >= 2.50
* Docker >= 24

### Déploiement infrastructure

```bash
git clone https://github.com/votre-org/minehost.git
cd minehost

az login
az account set --subscription "<SUBSCRIPTION_ID>"

cd terraform/environments/prod
terraform init
terraform apply -auto-approve

terraform output -json > ../../../config/azure-outputs.json
```

### Déploiement application

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
flask db upgrade

gunicorn --bind 0.0.0.0:5000 app:app --workers 4
```

---

## Guide utilisateur

### Création d’un serveur

1. Connexion au dashboard
2. Création du serveur
3. Choix des ressources (RAM, version Minecraft)
4. Provisioning automatique
5. Téléchargement du fichier VPN
6. Connexion via IP privée

### Gestion

* Démarrage et arrêt du serveur
* Logs temps réel
* Suppression sécurisée

### Facturation

* Facturation à la seconde
* Arrêt automatique après inactivité
* Suivi en temps réel

---

## Administration

### Accès SSH (administrateurs)

Via Azure Bastion uniquement.

### Supervision Docker

```bash
docker ps
docker stats
docker logs -f <container>
```

### Scalabilité

```bash
terraform apply -var="vm_count=4"
```

### Sauvegardes

* Snapshots Azure Files quotidiens
* Restauration manuelle possible

---

## Sécurité

### Conformité

| Standard             | Statut   |
| -------------------- | -------- |
| ISO 27001            | En cours |
| OWASP Top 10         | Conforme |
| CIS Docker Benchmark | Conforme |
| RGPD                 | Conforme |

### Sécurité applicative

* SAST : Bandit, SonarQube
* DAST : OWASP ZAP
* Scan images : Trivy

### Gestion des secrets

* Azure Key Vault
* Aucun secret en dur

### Politique de mises à jour

* Images Docker : hebdomadaire
* Dépendances Python : mensuelle
* OS : mises à jour automatiques

---

## Performance et monitoring

### KPIs

* Provisioning < 60 s
* Latence API < 200 ms
* Disponibilité > 90 %

### Alerting

* API indisponible
* Surcharge CPU
* Anomalie de coûts

### Tests de charge

* 100 utilisateurs simultanés
* Latence P95 < 500 ms
* Taux d’erreur < 1 %

---

## Documentation complète

* Cahier des charges
* Architecture détaillée
* Sécurité et risques
* FinOps et budget
* Roadmap projet
* Documentation API
* Guides développeur

---

## Équipe

Projet Fil Rouge – MSc Expert Cybersécurité
Efrei Campus Bordeaux – 2025–2026

| Rôle                 | Nom            |
| -------------------- | -------------- |
| Lead Dev / DevSecOps | Aydemir Alper  |
| SRE / FinOps         | El Mensi Mehdi |

---

## Support

* Email : [support@minehost.com](mailto:support@minehost.com)
* Discord communautaire
* Documentation en ligne
* Suivi des issues GitHub

---

## Licence

Propriété intellectuelle : Aydemir Alper, El Mensi Mehdi
Usage académique : Efrei Campus Bordeaux – Projet Fil Rouge 2025–2026

---

MineHost – Hébergement Minecraft sécurisé et performant
