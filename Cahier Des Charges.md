# CAHIER DES CHARGES TECHNIQUE  
**PROJET MINEHOST**

**Auteurs** : Aydemir Alper, El Mensi Mehdi | **Date** : 07 Janvier 2026

---

## RÉSUMÉ EXÉCUTIF

On crée une plateforme d'hébergement Minecraft sécurisée, self-hosted sur serveur Debian avec Docker. Le but : provisioning en moins de 2 minutes, accès via VPN uniquement (pas d'IP publique exposée), et facturation à la seconde.

**Les chiffres** : Pour 100 clients, on dépense 55€/mois et on fait 999€ de CA. Ça fait 94% de marge. Break-even à 6 clients.

---

# PARTIE 1 : ANALYSE DES BESOINS

## 1. COMMENT ON A COLLECTÉ LES BESOINS

On a fait 4 phases sur 4 semaines :

**Phase 1 - Étude documentaire**  
On a analysé 15 hébergeurs concurrents et lu 250 avis clients. Résultat : 78% des gens sont insatisfaits de la sécurité. Les hébergeurs low-cost c'est du VPS mutualisé sans vraie isolation.

**Phase 2 - Interviews**  
On a interviewé 20 utilisateurs : 8 joueurs occasionnels, 7 gérants de communautés moyennes, 5 admins experts. Ce qui ressort :
- *"J'ai eu 3 DDoS ce mois-ci, l'hébergeur n'a rien fait"* - Admin avec 50 joueurs
- *"Je paie 15€/mois mais j'ai des lags quand un voisin abuse du CPU"* - Admin expérimenté

**Phase 3 - Questionnaire**  
31 réponses (68% de taux de réponse). Les insights :
- 82% trouvent la config actuelle trop compliquée
- 91% sont intéressés par une tarification à l'usage
- 87% acceptent d'utiliser un VPN si ça améliore la sécurité

**Phase 4 - Audit technique**  
On a audité 5 hébergeurs. 3 sur 5 sont vulnérables aux injections SQL, 4 sur 5 utilisent du FTP en clair.

### Les besoins qu'on a identifiés

**Côté business** :
- BUS-001 : Être plus sécurisé que les concurrents
- BUS-002 : Avoir minimum 85% de marge
- BUS-003 : Pouvoir scaler jusqu'à 1000 serveurs par an

**Côté utilisateur** :
- USR-001 : Une interface web simple, pas de ligne de commande
- USR-002 : Se connecter en moins de 2 minutes
- USR-003 : 99% de disponibilité minimum

**Côté technique** :
- TEC-001 : Infrastructure basée sur Docker
- TEC-002 : Isolation stricte entre les serveurs
- TEC-003 : Sauvegardes automatiques

**Côté sécurité** :
- SEC-001 : Protection contre les DDoS
- SEC-002 : Chiffrement bout en bout
- SEC-003 : Serveurs invisibles depuis Internet (cloaking via VPN)

---

## 2. BESOINS FONCTIONNELS

### User Stories (exemples)

**US-001 - Créer un compte**  
Un visiteur arrive sur le site, entre son email et un mot de passe (minimum 12 caractères), reçoit un email de confirmation sous 5 secondes, et son compte est activé sous 24h.

**US-002 - Commander un serveur**  
L'utilisateur choisit un nom (lettres minuscules et chiffres uniquement), sélectionne la RAM (2, 4 ou 8GB), et clique sur "Créer". Le provisioning prend environ 45 secondes. Il reçoit un fichier .ovpn pour se connecter au VPN, et une IP privée du type 10.0.2.x:25565 pour accéder à son serveur.

**US-003 - Arrêter le serveur**  
L'utilisateur clique sur "Arrêter". Le système fait une sauvegarde automatique, stoppe le conteneur Docker en 10 secondes, et la facturation s'arrête immédiatement.

### Les exigences principales

**Authentification** :
- EXI-001 : Créer un compte avec email + mot de passe
- EXI-002 : Les mots de passe sont hachés avec Scrypt (pas de plaintext en base)

**Gestion des serveurs** :
- EXI-006 : Provisioning en moins de 60 secondes
- EXI-007 : Choix de RAM : 2GB, 4GB ou 8GB
- EXI-009 : Start/Stop à volonté, autant de fois qu'on veut
- EXI-010 : Sauvegarde automatique à chaque arrêt

**Facturation** :
- EXI-014 : Facturation à la seconde (1 heure = 60 × prix par seconde)
- EXI-016 : Paiement via Stripe (PCI-DSS compliant)

**Sécurité** :
- EXI-018 : Les serveurs sont accessibles UNIQUEMENT via VPN
- EXI-019 : VPN avec certificats X.509 (pas de mots de passe)
- EXI-020 : Les conteneurs tournent en non-root (UID 1000)

---

## 3. CONTRAINTES TECHNIQUES

### Sécurité (conforme OWASP Top 10, CIS Docker)

**SEC-C01** : Pas de secrets en dur dans le code  
→ Solution : Fichier .env avec variables d'environnement

**SEC-C02** : Chiffrement AES-256 au repos  
→ Solution : LUKS pour chiffrer les disques

**SEC-C03** : TLS 1.3 obligatoire  
→ Solution : Nginx avec Let's Encrypt

**SEC-C04** : Protection contre les injections SQL  
→ Solution : SQLAlchemy avec requêtes paramétrées (ORM)

**SEC-C05** : Rate limiting de 10 requêtes par seconde par IP  
→ Solution : Flask-Limiter + Redis

### Performance

**PERF-C01** : Provisioning en moins de 60 secondes (percentile 95)  
Si on dépasse, on perd notre avantage compétitif.

**PERF-C02** : Latence API sous 200ms (percentile 95)  
Si on dépasse, l'expérience utilisateur devient mauvaise.

**PERF-C04** : Disponibilité de 99% minimum  
Si on descend en dessous, on a des pénalités SLA.

### RGPD

Article 5 (minimisation des données) : On ne stocke que l'email et le mot de passe.  
Article 15 (droit d'accès) : `GET /api/user/data` renvoie toutes les données de l'utilisateur.  
Article 17 (droit à l'oubli) : `DELETE /api/account` supprime tout.

### Traçabilité : Besoin → Solution

- **BUS-001** (Sécurité) → VPN OpenVPN + Zero Trust → Validé par pentest
- **BUS-002** (Marge 85%) → Mutualisation Docker → Suivi FinOps
- **USR-002** (Connexion <2min) → VPN auto-configuré + provisioning rapide → Test end-to-end
- **TEC-002** (Isolation) → Docker namespaces + iptables → Test "noisy neighbor"
- **SEC-003** (Cloaking) → VPN seul accès, pas d'IP publique → Test connexion directe

---

# PARTIE 2 : SPÉCIFICATIONS TECHNIQUES

## 4. ARCHITECTURE LOGICIELLE

### La stack

- **Backend** : Python 3.11 + Flask 3.0
- **Base de données** : PostgreSQL 15
- **Frontend** : Vue.js 3
- **Orchestration** : Docker SDK Python
- **Logs temps réel** : Flask-SocketIO

### Comment ça marche (code simplifié)

```python
import docker
import subprocess
import re

client = docker.from_env()

def create_server(user_id, name, ram):
    if not re.match(r"^[a-z0-9-]{3,20}$", name):
        raise SecurityException("Nom invalide")
    
    if get_user_server_count(user_id) >= 5:
        raise QuotaExceededException("Limite atteinte")
    
    compose_yaml = f"""
version: '3.8'
services:
  minecraft-{user_id}-{name}:
    image: itzg/minecraft-server:latest
    environment:
      EULA: "TRUE"
      VERSION: "1.20.4"
      MEMORY: "{ram}G"
    volumes:
      - ./data/{user_id}/{name}:/data
    mem_limit: {ram}g
    user: "1000:1000"
    security_opt:
      - no-new-privileges
"""
    
    os.makedirs(f"/opt/minehost/servers/{user_id}-{name}", exist_ok=True)
    with open(f"/opt/minehost/servers/{user_id}-{name}/docker-compose.yml", "w") as f:
        f.write(compose_yaml)
    
    subprocess.run([
        "docker-compose",
        "-f", f"/opt/minehost/servers/{user_id}-{name}/docker-compose.yml",
        "up", "-d"
    ])
    
    container = client.containers.get(f"minecraft-{user_id}-{name}")
    ip = container.attrs['NetworkSettings']['Networks']['minecraft-net']['IPAddress']
    
    return {"status": "running", "ip": f"{ip}:25565"}
```

### Sécurisation du code

- **Validation des inputs** : Regex `^[a-z0-9-]{3,20}$` pour les noms
- **Protection CSRF** : Jetons anti-CSRF sur tous les POST/PUT/DELETE
- **Protection BOLA/IDOR** : Vérification `if server.owner_id != current_user.id: abort(403)`
- **Rate limiting** : 10 requêtes par seconde par IP

---

## 5. INFRASTRUCTURE SELF-HOSTED

### Le serveur

On a un serveur Debian 12 (bare metal ou VPS) :
- **CPU** : 12 vCPU
- **RAM** : 32GB
- **Disque** : 512GB SSD
- **Docker** : Engine 24.0 + Docker Compose 2.20

Capacité : 15-20 serveurs Minecraft simultanés.

L'isolation est faite par Docker : namespaces Linux (PID, NET, MNT) + cgroups pour limiter CPU et RAM + iptables pour le réseau.

### Le stockage

Les données sont stockées dans des volumes Docker locaux : `/opt/minehost/data/{user_id}/{server_name}`

Ça persiste même si le conteneur est arrêté ou supprimé.

**Backups automatiques** : Un script rsync tourne tous les jours à 4h du matin et copie tout vers un stockage externe.

```bash
rsync -avz /opt/minehost/data/ /backup/daily/$(date +%Y%m%d)/
```

### Le réseau

**Architecture** :
```
Internet 
    ↓
[OpenVPN Server]
    ↓
Réseau Docker "minecraft-net" (172.20.0.0/16)
    ↓
Conteneurs Minecraft (172.20.0.x) + PostgreSQL (172.20.0.2)
```

**Règles firewall (iptables)** :

On bloque TOUT par défaut :
```bash
iptables -P INPUT DROP
iptables -A INPUT -i lo -j ACCEPT  
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT  
iptables -A INPUT -p tcp --dport 2222 -j ACCEPT 
iptables -A INPUT -p udp --dport 1194 -j ACCEPT  
```

Pas d'accès direct aux conteneurs depuis Internet :
```bash
iptables -A FORWARD -i eth0 -o docker0 -j DROP  
iptables -A FORWARD -i tun0 -o docker0 -j ACCEPT  
```

**OpenVPN** :
```conf
port 1194
proto udp
dev tun
server 10.8.0.0 255.255.255.0
push "route 172.20.0.0 255.255.0.0"  
cipher AES-256-GCM
user nobody
group nogroup
```

---

## 6. SÉCURITÉ

### Zero Trust & VPN

On a un serveur OpenVPN qui tourne sur le serveur principal. L'authentification se fait uniquement par certificats X.509 (pas de mots de passe). Les certificats sont générés avec EasyRSA.

Le workflow :
1. L'utilisateur commande un serveur
2. L'API génère un certificat client unique
3. L'utilisateur télécharge le fichier .ovpn
4. Il se connecte au VPN
5. Il peut accéder à son serveur via l'IP privée Docker

### Durcissement Docker (CIS Benchmark)

- **User non-root** : Les conteneurs tournent avec UID 1000
- **Capabilities drop** : On enlève toutes les capabilities sauf NET_BIND_SERVICE
- **Read-only rootfs** : Le système de fichiers root est en lecture seule (sauf /data et /tmp)
- **no-new-privileges** : Empêche l'escalade de privilèges

### Gestion des secrets

On utilise un fichier `.env` (qui est dans .gitignore) :

```python
DB_PASSWORD=mon_super_mot_de_passe
SECRET_KEY=ma_cle_secrete
STRIPE_API_KEY=sk_test_...

from dotenv import load_dotenv
import os

load_dotenv()
db_password = os.getenv('DB_PASSWORD')
```

---

## 7. FINOPS (optimisation des coûts)

### Mutualisation

On a 1 serveur qui héberge 15-20 conteneurs Minecraft simultanés. Coût du serveur :
- VPS : environ 50€/mois
- Dédié : environ 150€/mois

### Auto-Shutdown (économie de ressources)

On a un watchdog qui tourne toutes les 5 minutes. Il check via RCON combien il y a de joueurs sur chaque serveur. Si un serveur a 0 joueur pendant 15 minutes, on le stoppe automatiquement avec `docker-compose stop`. La facturation s'arrête.

```python
import mcrcon

for server in active_servers:
    try:
        with mcrcon.MCRcon(server.ip, "password") as mc:
            response = mc.command("list")
            players = int(response.split()[2])
        
        if players == 0:
            server.idle_time += 5
            if server.idle_time >= 15:
                subprocess.run(["docker-compose", "stop", server.compose_path])
                server.status = "stopped"
    except:
        pass
```

---

## 8. POURQUOI CES CHOIX

On a comparé plusieurs solutions :

**Self-Hosting vs Cloud Azure vs Kubernetes**

Self-Hosting (notre choix) :
- Coûts : 55€/mois (VPS) ou 150€/mois (dédié)
- Contrôle total (accès root, on fait ce qu'on veut)
- Simple (pas de complexité Kubernetes)
- Score : 9.5/10

Cloud Azure :
- Coûts : 520€/mois
- Géré par Microsoft (moins de contrôle)
- Interface graphique simple
- Score : 7/10

Kubernetes :
- Coûts : Élevés (overhead du cluster)
- Très complexe
- Sur-dimensionné pour notre besoin
- Score : 5.3/10

**Pourquoi Docker Compose ?**  
Simple, déclaratif, reproductible. On évite la complexité de Kubernetes.

**Pourquoi une API Python directe ?**  
Contrôle total sur l'orchestration Docker. On utilise le Docker SDK Python.

**Pourquoi self-hosting ?**  
Coûts 71% inférieurs à Azure (55€ vs 520€). Contrôle total. Pas de vendor lock-in.

---

## 9. RISQUES & OPPORTUNITÉS

### Les risques

**DDoS sur l'OpenVPN**  
Probabilité : Élevée | Impact : Élevé  
Mitigation : Fail2ban + rate limiting iptables + avoir un serveur VPN de backup

**Panne du serveur unique**  
Probabilité : Moyenne | Impact : Élevé  
Mitigation : Backups quotidiens + plan de disaster recovery (voir section 15)

**Container escape (évasion du conteneur Docker)**  
Probabilité : Faible | Impact : Élevé  
Mitigation : Hardening CIS + conteneurs en non-root + scans de sécurité quotidiens

### Les opportunités

**Extension à d'autres jeux (Rust, ARK, Valheim)**  
Impact : Marché multiplié par 3 à 5  
Investissement : 2-3 semaines de dev par jeu  
ROI : +150% de CA en année 2

**API publique pour développeurs**  
Impact : +10% de clients "power users"  
Investissement : 1 semaine  
ROI : Trimestre 2

**Modèle Freemium (1 serveur gratuit limité)**  
Impact : Acquisition virale  
Investissement : 10-20€/mois de coûts  
ROI : -60% de coût d'acquisition client

---

## 10. LES KPIs

**Provisioning** : Moins de 2 minutes (percentile 95)  
Mesure : `time docker-compose up -d`

**Latence API** : Moins de 200ms (percentile 95)  
Mesure : Prometheus Flask exporter

**Disponibilité** : 99% minimum  
Mesure : Uptime Kuma (self-hosted)

**Marge brute** : Plus de 85%  
Calcul : (CA - OPEX) / CA

---

## 11. PLANNING 

**MVP**  
On fait l'API Flask, le système de déploiement Docker Compose, la base PostgreSQL, et l'authentification.  
Critère de succès : On peut créer un serveur en moins de 60 secondes.

**Hardening (sécurité)**  
On configure l'OpenVPN, on met en place le rate limiting, on passe en HTTPS.  
Critère de succès : Scan OWASP ZAP avec 0 vulnérabilité critique, VPN fonctionnel.

**FinOps**  
On code l'auto-shutdown et on intègre Stripe pour la facturation.  
Critère de succès : Auto-shutdown testé, facturation précise à la seconde.

**Production**  
Tests de charge, pentest externe, documentation.  
Critère de succès : 1000 requêtes/seconde, 0 CVE critique.

---

## 12. RGPD

**Où sont les données** : En France (hébergement en France)

**Droits des utilisateurs** :
- Droit d'accès : `GET /api/user/data` renvoie toutes les données au format JSON
- Droit à l'oubli : `DELETE /api/account` supprime tout (serveurs + données + compte)
- Portabilité : Export JSON + ZIP


---

## 13. BUDGET & ROI

### Les coûts mensuels

**Serveur Debian VPS** (8 vCPU, 16GB RAM) : 50€/mois  
**Stockage backup externe** : 5€/mois  
**Total** : 55€/mois

(Si on prend un serveur dédié : environ 150€/mois)

### Le retour sur investissement

**Offre Starter 2GB** : Prix 9.99€/mois | Coût 0.55€ | Marge 9.44€ (94%)

**Avec 100 clients** :
- Chiffre d'affaires : 999€/mois
- Coûts : 55€/mois
- Marge : 944€/mois (94%)
- Break-even : 6 clients

**Comparaison** :
- Azure : 520€/mois de coûts → Marge de seulement 48% → Break-even à 53 clients
- Nous : 55€/mois → Marge de 94% → Break-even à 6 clients

---

## 14. LES TESTS

### Tests de sécurité

**SAST (analyse statique)** : Bandit sur le code Python, intégré dans CI/CD  
**DAST (analyse dynamique)** : OWASP ZAP toutes les semaines sur l'environnement de staging  
**Scans des conteneurs** : Trivy quotidiennement pour détecter les CVE  
**Pentest externe** : En semaine 9, budget 5000€

### Tests de charge

Locust avec 1000 utilisateurs simultanés. Objectif :
- 1000 requêtes par seconde soutenues
- Taux d'erreur < 1%
- Latence percentile 95 < 500ms

### Tests de chaos

On simule des pannes :
- Kill de 20% des conteneurs → Doivent redémarrer en moins de 30 secondes
- Saturation CPU → Les autres conteneurs doivent continuer de fonctionner

---

## 15. MAINTENANCE ET SUPPORT

### Mises à jour

**Docker** : Scan Trivy hebdomadaire, rebuild des images si CVE critique  
**Python** : Dependabot sur GitHub, review par 2 devs avant merge  
**OS Debian** : apt unattended-upgrades pour les mises à jour automatiques

### Support client

**P1 (service down)** : Réponse en moins de 30 minutes  
**P2 (service dégradé)** : Réponse en moins de 4 heures  
**P3 (question)** : Réponse en moins de 24 heures

### Disaster Recovery

**Objectifs** : RTO (temps de récupération) de 1 heure, RPO (perte de données) de 24 heures

**Procédure en cas de panne serveur** :
1. Détection (T+0) : Alerte automatique
2. Commander un nouveau serveur (T+5min)
3. Restaurer les backups (T+15min)
4. Redéployer avec docker-compose (T+30min)
5. Validation (T+45min)
6. Communication aux clients (T+60min)

---

## 16. ADMINISTRATION

### Infrastructure as Code

On utilise Docker Compose pour tout :

```yaml
version: '3.8'
services:
  api:
    build: ./backend
    ports: ["5000:5000"]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  
    environment:
      - DB_HOST=postgres
      - DB_PASSWORD=${DB_PASSWORD}
  
  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
  
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt

networks:
  minecraft-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  pgdata:
```

**Déploiement** : `docker-compose up -d`

---

## ANNEXES

### Glossaire 

**Docker Compose** : Outil pour gérer plusieurs conteneurs en même temps avec un fichier YAML  
**iptables** : Le firewall de Linux  
**RCON** : Remote Console pour administrer un serveur Minecraft à distance  
**Percentile 95 (P95)** : 95% des requêtes sont plus rapides que ce seuil

### Références

- Docker : docs.docker.com
- Flask : flask.palletsprojects.com
- OpenVPN : openvpn.net
- Minecraft : github.com/itzg/docker-minecraft-server


---
