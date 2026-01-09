# MineHost - Plateforme d'Hébergement Minecraft Sécurisée

[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com)
[![Security](https://img.shields.io/badge/Security-Zero%20Trust%20VPN-blue)](https://github.com)
[![Self-Hosted](https://img.shields.io/badge/Infrastructure-Self--Hosted-orange)](https://github.com)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED)](https://www.docker.com)

**Plateforme SaaS d'hébergement de serveurs Minecraft** avec architecture self-hosted sur serveur Debian, isolation Docker et sécurité Zero Trust via VPN obligatoire.

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

## Vue d'ensemble

### Problème résolu

Les hébergeurs Minecraft actuels souffrent de :

* Insécurité : attaques DDoS, accès non autorisés
* Complexité : configuration technique requise (SSH, CLI)
* Performance instable : mutualisation anarchique (Noisy Neighbor Effect)

### Solution proposée

* Sécurité maximale : Zero Trust + VPN obligatoire (infrastructure non exposée à Internet)
* Simplicité : interface web, provisioning en moins de 2 minutes
* Isolation garantie : Docker + iptables + volumes dédiés
* Tarification juste : facturation à la seconde d'utilisation réelle

### Indicateurs clés

* Provisioning : < 2 minutes
* Sécurité : aucune IP publique exposée, accès 100 % via VPN
* Coût : 9,99 €/mois (2 Go RAM)
* Scalabilité : 15-20 serveurs simultanés par machine

## Architecture

### Stack technique

```
INTERNET
   |
OpenVPN Server (mot de passe)
   |
Serveur Debian 12 (8 vCPU, 8GB RAM)
   |
Docker Network "minecraft-net" (172.20.0.0/16)
   |
- Conteneurs Minecraft (15-20 simultanés)
- PostgreSQL (172.20.0.2)
```

### Composants principaux

| Composant       | Technologie                    | Rôle                                |
| --------------- | ------------------------------ | ----------------------------------- |
| Backend API     | Python 3.11, Flask, Psycopg2   | Orchestration Docker SDK            |
| Base de données | PostgreSQL 15 (Alpine)         | Gestion utilisateurs, serveurs      |
| Compute         | Serveur Debian 12 (Self-Host)  | Hébergement conteneurs              |
| Isolation       | Docker Engine 24 (cgroups)     | Isolation ressources et processus    |
| Stockage        | Volumes Locaux + rsync         | Persistance et Backups              |

**Niveau stockage**
* Volume Docker par serveur (`~/minecraft-automation/servers/{server_name}`)
* Persistance indépendante du cycle de vie conteneur
* Backups quotidiens (rsync) à 4h00 vers stockage externe

### Isolation multi-niveaux

**Niveau réseau**

* iptables bloquant tout accès Internet vers le serveur (sauf SSH custom + OpenVPN)
* VPN obligatoire avec mots de passe
* Pas d'IP publique sur les conteneurs

**Niveau serveur**

* Debian 12
* Hardening OS
* Fail2ban

**Niveau Docker**

* Limites CPU, mémoire via cgroups
* Exécution non-root (UID 1000)
* Isolation namespaces (PID, NET, MNT)

**Niveau stockage**

* Volume Docker par serveur (`/opt/minehost/data/{user}/{server}`)
* Persistance indépendante du cycle de vie conteneur
* Backups quotidiens (rsync)

## Démarrage rapide

### Prérequis

* Serveur Debian 12
* Docker >= 24
* Docker Compose >= 2.20
* OpenVPN configuré

### Déploiement infrastructure

```bash
git clone https://github.com/Maskass-z/minehost-terraform.git
cd minehost-terraform

cp .env.example .env

docker-compose up -d

docker ps
docker logs api
```

---

## Guide utilisateur

### Création d'un serveur

1. Connexion au dashboard
2. Création du serveur
3. Choix des ressources (RAM : 512MB/1GB/2GB/4GB/8GB, version Minecraft)
4. Provisioning automatique (~120 secondes)
5. Téléchargement du fichier VPN (.ovpn)
6. Connexion via IP privée (10.8.0.2:port)

### Gestion

* Démarrage et arrêt du serveur
* Logs temps réel (Docker SDK)
* Suppression sécurisée

### Facturation

* Facturation à la seconde
* Suivi en temps réel

## Administration

### Accès SSH (administrateurs)

```bash
ssh -p 2222 maskass@votre-serveur
```

### Supervision Docker

```bash
docker ps
docker stats
docker logs -f mc-<server>-<user>
```

### Scalabilité

Pour augmenter la capacité :
1. Upgrade RAM/CPU du serveur
2. Ou ajouter un second serveur + load balancer

### Sauvegardes

* Script rsync quotidien (4h du matin)
* Stockage externe
* Rétention : 7 jours

## Sécurité

### Conformité

| Standard             | Statut   |
| -------------------- | -------- |
| OWASP Top 10         | Conforme |
| CIS Docker Benchmark | Partiel  |
| RGPD                 | Conforme |

### Sécurité applicative

* SAST : Bandit
* Scan images : Trivy
* Rate limiting : Flask-Limiter

### Gestion des secrets

* Fichier .env (gitignored)
* Aucun secret en dur dans le code

### Firewall

```bash
iptables -P INPUT DROP
iptables -A INPUT -p tcp --dport 2222 -j ACCEPT  
iptables -A INPUT -p udp --dport 1194 -j ACCEPT 
iptables -A FORWARD -i eth0 -o docker0 -j DROP   
iptables -A FORWARD -i tun0 -o docker0 -j ACCEPT 
```

## Performance et monitoring

### KPIs

* Provisioning < 120 s
* Latence API < 200 ms
* Disponibilité > 90 %
* Densité : 15-20 serveurs/machine

### Tests de charge

* 50 créations simultanées
* Latence P95 < 500 ms
* Taux d'erreur < 1 %

## Documentation complète

* [Cahier des charges](./docs/CDC_MineHost_v2.6_Simple_Humain.md)
* Architecture détaillée
* Sécurité et risques
* Budget et ROI
* Documentation API
* Guides développeur

## Équipe

Projet Fil Rouge – MSc Expert Cybersécurité  
Efrei Campus Bordeaux – 2025–2026

| Rôle                 | Nom            |
| -------------------- | -------------- |
| Lead Dev / DevSecOps | Aydemir Alper  |
| SRE / FinOps         | El Mensi Mehdi |

## Support

* Email : support@minehost.com
* Discord communautaire (à venir)
* Documentation en ligne
* Suivi des issues GitHub

## Licence

Propriété intellectuelle : Aydemir Alper, El Mensi Mehdi  
Usage académique : Efrei Campus Bordeaux – Projet Fil Rouge 2025–2026

---

