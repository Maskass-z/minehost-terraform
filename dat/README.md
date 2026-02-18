# DOSSIER D'ARCHITECTURE TECHNIQUE -- DAT
**PROJET MINEHOST**

**Auteurs** : Aydemir Alper, El Mensi Mehdi  
---

## VUE D'ENSEMBLE

On héberge des serveurs Minecraft sur notre propre machine Debian avec Docker. Les joueurs se connectent via VPN uniquement (pas d'accès direct depuis Internet). L'API Flask orchestre tout.

**Architecture en 1 schéma** :

```
Internet → [OpenVPN:1194] → Serveur Debian (8GB RAM)
                                    ↓
                          [Docker Network 172.20.0.0/16]
                                    ↓
        ┌──────────────┬────────────┬──────────────┬──────────────┐
        │              │            │              │              │
    API Flask     PostgreSQL    Nginx       15-20 conteneurs
    (5000)          (5432)      (80/443)    Minecraft (25565)
```

**Workflow utilisateur** :
1. Utilisateur crée un compte → API Flask
2. Commande un serveur → API appelle Docker SDK → Conteneur démarre en ~120s max
3. Télécharge config VPN (.ovpn) → Se connecte au VPN → Accède au serveur via IP privée

**Chiffres clés** :
- Serveur : 8 vCPU, 8GB RAM, 512GB SSD
- Capacité : 15-20 serveurs Minecraft simultanés
- Coût : 30€/mois (électricité)
- Marge : 85% (vs 48% sur Azure)

---

## POURQUOI CES CHOIX ?

### Self-hosting vs Cloud

On a hésité entre louer un serveur Azure et self-host sur notre PC.

**Azure** :
- Avantages : Scalabilité auto, monitoring intégré, support Microsoft
- Inconvénients : 520€/mois, vendor lock-in, moins de contrôle

**Self-hosting (notre choix)** :
- Avantages : 30€/mois (électricité), contrôle total (root access), pas de vendor lock-in
- Inconvénients : Responsabilité maintenance, pas de SLA garanti, IP dynamique

**Décision** : Self-hosting. Économie de 490€/mois (94%). On accepte la complexité opérationnelle car on apprend et on maîtrise tout... fin presque.

### Docker vs VMs complètes

**VMs** (KVM/QEMU) :
- Isolation forte (hyperviseur)
- Mais : 512MB-1GB RAM par VM → max 8 serveurs sur 8GB
- Démarrage : 30-60 secondes

**Docker (notre choix)** :
- Isolation suffisante (namespaces + cgroups)
- 50-100MB RAM par conteneur → 15-20 serveurs sur 8GB
- Démarrage : 2-5 secondes

**Décision** : Docker. On veut de la densité. L'isolation est suffisante pour des serveurs de jeu (pas de données ultra-sensibles).

### PostgreSQL vs MySQL vs MongoDB

**PostgreSQL** :
- JSONB natif performant (on stocke des metadata de serveurs)
- Meilleur respect des standards SQL
- On connaît mieux

**MySQL** :
- Meilleur sur les lectures simples
- Mais pas de JSONB optimisé

**MongoDB** :
- Bien pour du non-structuré
- Mais notre modèle est relationnel et simple (Users → Servers → Billing)

**Décision** : PostgreSQL. On a besoin de JSONB et de relations one-to-many (marketing de masse).

---

# INFRASTRUCTURE

## Le serveur physique

**Config** :
- **CPU** : AMD Ryzen 7 (8 cœurs)
- **RAM** : 8GB DDR4
- **Disque** : 512GB SSD NVMe
- **Réseau** : Ethernet 1 Gbps
- **Alim** : 750W

**Dimensionnement** :

La RAM c'est notre goulot d'étranglement. Calcul :
- 8GB total
- -2GB pour l'OS + services système
- = 6GB utilisables
- Un serveur Minecraft = 512MB minimum
- 6GB / 512MB = 12 serveurs théoriques
- En pratique, on vise 15 max (avec des serveurs à 400-500MB)

**Consommation électrique** :
- Idle : 50W
- Charge normale : 100W
- Charge max : 150W
- Moyenne : 120W × 24h × 30j = 86 kWh/mois × 0.23€ = 20€/mois

**Refroidissement** : Ventilateurs CPU + boîtier. Température cible < 70°C. Monitoring via `sensors`.

**Pourquoi pas un serveur dédié OVH ?**  
Un Kimsufi coûte 15€/mois. Mais notre PC consomme 20€/mois d'électricité et on l'a déjà. Différence : 5€/mois. Pas assez significatif pour justifier la migration. On réévaluera si on dépasse 20 serveurs.

## Système d'exploitation : Debian 12

**Pourquoi Debian et pas Ubuntu ?**

Debian c'est plus stable et minimaliste. Ubuntu préinstalle Snap, Netplan, cloud-init... Nous on veut du minimal. Et puis on connaît mieux Debian.

**Partitionnement** :
```
/dev/sda1    512MB    /boot    
/dev/sda2    20GB     /        (OS)
/dev/sda3    2GB      swap     
/dev/sda4    490GB    /home    (données Minecraft)
```

Le `/home` c'est 95% du disque parce que c'est là qu'on stocke les données Minecraft.

**Hardening OS** :

1. **SSH sur port 2222** (au lieu de 22)  
   Réduit de 99% les bots de brute-force.

2. **Fail2ban**  
   Ban les IPs après 5 échecs SSH en 10 minutes.

3. **Firewall iptables** (détails plus bas)

4. **Updates automatiques**  
   ```bash
   apt install unattended-upgrades
   ```
   Applique les mises à jour de sécurité tous les jours à 6h. Reboot si nécessaire (dimanche 4h).

5. **Désactivation services inutiles**  
   ```bash
   systemctl disable bluetooth cups avahi-daemon
   ```
   Si on l'utilise pas, on le désactive.

## Docker

**Installation** :
```bash
curl -fsSL https://get.docker.com | sh
apt install docker-compose-plugin
```

**Configuration daemon** (`/etc/docker/daemon.json`) :
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "default-address-pools": [
    {"base": "172.20.0.0/16", "size": 24}
  ]
}
```

Limite les logs à 30MB par conteneur (3 fichiers × 10MB) pour éviter de remplir le disque.

**Hardening Docker (CIS Benchmark)** :

1. **Conteneurs non-root (UID 1000)**
   ```yaml
   user: "1000:1000"
   ```
   Si un attaquant exploit le conteneur, il est pas root.

2. **Limites cgroups**
   ```yaml
   mem_limit: 2g
   cpus: "1.5"
   pids_limit: 100
   ```
   Évite qu'un conteneur abuse des ressources.

3. **Capabilities drop**
   ```yaml
   cap_drop:
     - ALL
   cap_add:
     - NET_BIND_SERVICE
   ```
   On enlève toutes les capabilities sauf celle pour bind le port 25565.

4. **No new privileges**
   ```yaml
   security_opt:
     - no-new-privileges:true
   ```
   Empêche l'escalade de privilèges.

5. **Scan CVE quotidien**
   ```bash
   trivy image itzg/minecraft-server:latest
   ```
   Si CVE critique (score >9.0) détectée, on rebuild.

---

# RÉSEAU

## Plan d'adressage

**Réseaux utilisés** :

```
192.168.1.0/24       → LAN domestique (box Internet)
10.8.0.0/24          → VPN OpenVPN (clients)
172.20.0.0/16        → Docker network (conteneurs)
```

**Adresses fixes** :

```
Serveur Debian       → 192.168.1.50 (LAN)
OpenVPN Server       → 10.8.0.1
API Flask            → 172.20.0.10
PostgreSQL           → 172.20.0.2
Nginx                → 172.20.0.3
Conteneurs Minecraft → 172.20.1.10-254 (pool dynamique)
```

## Firewall iptables

**Philosophie** : DROP tout par défaut, ACCEPT uniquement ce qui est nécessaire.

**Règles principales** :

```bash
iptables -P INPUT DROP
iptables -P FORWARD DROP

iptables -A INPUT -i lo -j ACCEPT

iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

iptables -A INPUT -p tcp --dport 2222 -j ACCEPT

iptables -A INPUT -p udp --dport 1194 -j ACCEPT

iptables -A INPUT -p tcp --dport 443 -j ACCEPT

iptables -A FORWARD -i eth0 -o docker0 -j DROP

iptables -A FORWARD -i tun0 -o docker0 -j ACCEPT

iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
```

**Point clé** : La ligne `FORWARD -i eth0 -o docker0 -j DROP` empêche Internet de joindre directement les conteneurs. Seul le VPN peut y accéder.

**Test de sécurité** :

Depuis Internet (4G/5G) :
```bash
nmap -p5000,25565 VOTRE_IP_PUBLIQUE
# le résultat attendu c'est : filtered (c'est a dire bloqué)
```

Depuis le VPN :
```bash
curl http://172.20.0.10:5000/health
# le résultat attendu c'est : 200 OK
```

## OpenVPN

**Installation** :
```bash
apt install openvpn
```

**Config serveur** (`/etc/openvpn/server.conf`) :
```conf
port 1194
proto udp
dev tun
server 10.8.0.0 255.255.255.0

push "route 172.20.0.0 255.255.0.0"

cipher AES-256-GCM
auth SHA256

plugin /usr/lib/x86_64-linux-gnu/openvpn/plugins/openvpn-plugin-auth-pam.so login

user nobody
group nogroup
```

**Pourquoi password et pas certificats X.509 ?**  
Pour le MVP, c'est plus simple. On crée des users Unix :

```bash
useradd -m -s /bin/false vpnuser1
echo "vpnuser1:PASSWORD" | chpasswd
```

L'utilisateur se connecte avec ce login/password. Plus tard, on pourra migrer vers des certificats.

**Fichier client (.ovpn)** :
```conf
client
dev tun
proto udp
remote minehost.duckdns.org 1194
cipher AES-256-GCM
auth SHA256
auth-user-pass
```

## Réseau domestique

**FAI** : Orange
**Débit** : 400/1000 Mbps (Fibre)  
**IP publique** : Dynamique (change tous les 7-30 jours)

**Solution IP dynamique** : DynDNS (No-IP ou DuckDNS).

Script sur le serveur ping No-IP toutes les 5 minutes avec la nouvelle IP. Le domaine `minehost.duckdns.org` pointe toujours vers notre IP actuelle.

**Port forwarding sur la box** :
```
1194/UDP → 192.168.1.50:1194 (OpenVPN)
2222/TCP → 192.168.1.50:22   (SSH)
443/TCP  → 192.168.1.50:443  (HTTPS)
```

---

# APPLICATION

## Stack technique

**Backend** : Python 3.11 + Flask 3.0  
**BDD** : PostgreSQL 15  
**Frontend** : Jinja2 (templates HTML)  
**Orchestration** : Docker SDK Python (`docker-py`)

**Pourquoi Flask et pas FastAPI ?**  
On connaît mieux Flask. FastAPI serait mieux pour les perfs (async) mais on n'a pas besoin d'async pour notre use case.

## Structure du code

```
/home/maskass/minecraft-automation/
├── app.py                  
├── docker-compose.yml      
├── .env                    
├── models/
│   ├── user.py            
│   ├── server.py          
│   └── billing.py         
├── routes/
│   ├── auth.py            
│   ├── servers.py         
│   └── billing.py         
└── services/
    └── docker_orchestrator.py  # Logique création conteneurs
```

## Orchestration Docker (extrait)

```python
import docker
import os
import random

client = docker.from_env()

def create_minecraft_server(user_id, name, ram="2G"):
    if not re.match(r'^[a-zA-Z0-9_-]{3,50}$', name):
        raise ValueError("Nom invalide")
    
    if get_user_server_count(user_id) >= 5:
        raise ValueError("Max 5 serveurs")
    
    port = random.randint(25566, 26000)
    
    volume_path = f"/home/maskass/minecraft-automation/servers/{user_id}_{name}"
    os.makedirs(volume_path, exist_ok=True)
    
    container = client.containers.run(
        image='itzg/minecraft-server:latest',
        detach=True,
        name=f"mc-{name}-{user_id}",
        ports={'25565/tcp': port},
        environment={
            'EULA': 'TRUE',
            'VERSION': '1.20.4',
            'MEMORY': ram
        },
        volumes={volume_path: {'bind': '/data'}},
        user="1000:1000",  # Non-root
        mem_limit=ram,
        network='minecraft-net',
        restart_policy={'Name': 'unless-stopped'}
    )
    
    new_server = Server(
        owner_id=user_id,
        name=name,
        container_id=container.id,
        port=port,
        status='running'
    )
    db.session.add(new_server)
    db.session.commit()
    
    return {"status": "running", "ip": f"172.20.1.x:{port}"}
```

**Sécurité du code** :
- Regex validation sur le nom (anti-injection)
- Vérification `owner_id` (anti-BOLA)
- Quota enforcement (max 5 serveurs)
- Conteneur non-root
- Mem limit (évite OOM)

## Base de données

**Schéma** :

```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Servers
CREATE TABLE servers (
    id SERIAL PRIMARY KEY,
    owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    container_id VARCHAR(64) UNIQUE NOT NULL,
    port INTEGER NOT NULL,
    ram VARCHAR(10) NOT NULL,
    version VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'running',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index (performance)
CREATE INDEX idx_servers_owner ON servers(owner_id);
CREATE INDEX idx_users_email ON users(email);
```

**Sécurité BDD** :

1. **User dédié** (pas de superuser) :
   ```sql
   CREATE USER minehost_user WITH PASSWORD 'MOT_DE_PASSE';
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES TO minehost_user;
   ```

2. **SQLAlchemy ORM** : Toutes les requêtes sont paramétrées (anti-injection).

3. **TLS** : Connexions chiffrées entre API et PostgreSQL.

4. **Backup chiffré** :
   ```bash
   pg_dump minehost | gzip | gpg --encrypt > backup.sql.gz.gpg
   ```

**Optimisation** :

- Index sur les colonnes fréquentes (email, owner_id)
- Connection pooling (10 connexions permanentes)
- Slow query logging (>1s)

## Stockage

**Volumes Docker** :

Chaque serveur a son dossier sur l'hôte :
```
/home/maskass/minecraft-automation/servers/
├── 1_survival/
│   ├── world/
│   └── server.properties
├── 1_creative/
└── 2_skyblock/
```

**Mapping Docker** :
```yaml
volumes:
  - /home/maskass/minecraft-automation/servers/1_survival:/data
```

**Avantages** :
- Persistance (survit au conteneur)
- Backup facile (`rsync`)
- Performance (accès direct au filesystem)

**Sizing** :
- Monde vide : ~100MB
- Monde joué 1 mois : ~500MB
- Monde joué 1 an : ~5GB
- 15 serveurs × 1GB = 15GB utilisés / 490GB dispos

**Backups** :

Script quotidien (4h du matin) :
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
rsync -avz /home/maskass/minecraft-automation/servers/ \
  /mnt/backup/minecraft-$DATE/
tar -czf /mnt/backup/minecraft-$DATE.tar.gz /mnt/backup/minecraft-$DATE/
rm -rf /mnt/backup/minecraft-$DATE/
find /mnt/backup/ -name "*.tar.gz" -mtime +7 -delete
```

Stockage : Disque USB externe 2TB (100€).

---

# SÉCURITÉ

## Stratégie Zero Trust

**Principe** : "Ne jamais faire confiance, toujours vérifier."

**Implémentation** :
1. Aucun service exposé en public (sauf SSH, VPN, HTTPS)
2. API, BDD, Minecraft accessibles uniquement via VPN
3. Authentification forte (VPN + JWT)

**Test** :

Depuis Internet :
```bash
nmap -p- VOTRE_IP_PUBLIQUE
# le résultat attendu: Seuls 2222, 1194, 443 sont ouverts
```

## Protection attaques courantes

**1. DDoS sur OpenVPN**

Mitigation :
- Fail2ban (ban après 50 paquets/s)
- Rate limiting iptables :
  ```bash
  iptables -A INPUT -p udp --dport 1194 -m limit --limit 25/s -j ACCEPT
  iptables -A INPUT -p udp --dport 1194 -j DROP
  ```

**2. Brute-force SSH**

Mitigation :
- SSH sur port 2222 (réduit 99% des bots)
- Password disabled (clés SSH uniquement)
- Fail2ban (ban après 5 échecs)

**3. Injection SQL**

Mitigation :
- SQLAlchemy ORM (requêtes paramétrées)
- Validation regex sur les inputs

**4. XSS**

Mitigation :
- Jinja2 auto-escape
- CSP header :
  ```python
  response.headers['Content-Security-Policy'] = "default-src 'self'"
  ```

## Scan de vulnérabilités

**Scan Docker** :
```bash
trivy image itzg/minecraft-server:latest
```

## Authentification

 **Méthode** : Sessions Flask (cookie sécurisé)
   
   **Flux** :
   1. User envoie username + password → `POST /login`
   2. Serveur vérifie hash Scrypt
   3. Si OK, crée session Flask
   4. Cookie HttpOnly + Secure stocké

---

# EXPLOITATION

## Déploiement

**Prérequis** :
- Debian 12 installé
- Docker + Docker Compose
- OpenVPN configuré
- DynDNS configuré
- SSL Let's Encrypt généré

**Procédure** :

```bash
# 1. Clone
git clone https://github.com/maskass-z/minehost-terraform.git
cd minehost-terraform

# 2. Config
cp .env.example .env
nano .env  # Remplir DB_PASSWORD, SECRET_KEY

# 3. SSL
certbot certonly --standalone -d minehost.duckdns.org

# 4. Démarrage
docker compose up -d

# 5. Init BDD
docker exec -it minehost_api flask db upgrade

# 6. Firewall
iptables-restore < /etc/iptables/rules.v4

# 7. Vérification
docker ps
curl http://localhost:5000/health
```

**Mise à jour** :
```bash
git pull
docker compose up -d --build api_server
docker logs -f minehost_api
```

## Monitoring

**Stack** : Prometheus + Grafana + Loki

```yaml
# docker-compose.yml (extrait)
services:
  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
  
  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
  
  loki:
    image: grafana/loki:latest
    ports: ["3100:3100"]
```

**Dashboards** :
- CPU/RAM/Disk (système)
- Conteneurs actifs (Docker)
- Requêtes/seconde API (Flask)
- Logs erreurs (Loki)

**Alerting** : Discord webhook

Alertes si :
- CPU > 80% pendant 5min
- RAM > 90%
- Disk < 10%
- API down

## Maintenance

**Quotidienne** :
- Backup automatique (4h)
- Scan Trivy images
- Purge logs >30j

**Hebdomadaire** :
- Review logs erreurs
- Vérification espace disque

**Mensuelle** :
- Updates Debian (`apt update && apt upgrade`)
- Renouvellement SSL (auto certbot)
- Scan DAST (OWASP ZAP)

**Mises à jour Docker** :
```bash
docker pull itzg/minecraft-server:latest
# Si nouvelle version, redémarrer conteneurs
```

**Rollback si problème** :
```bash
git log --oneline
git checkout VERSION_STABLE
docker compose up -d --build
```

## Plan de continuité

**Objectifs** :
- RTO (temps de récupération) : 1 heure
- RPO (perte de données max) : 24 heures

**Scénario 1 : Panne électrique**

RTO : 10 minutes  
RPO : 0 (aucune perte)

Procédure :
1. Attendre retour courant
2. BIOS redémarre auto (option "Restore on AC Power Loss")
3. Debian boot
4. Docker redémarre conteneurs (restart policy)

**Scénario 2 : Crash disque**

RTO : 24 heures (délai achat SSD)  
RPO : 24 heures (dernier backup)

Procédure :
1. Acheter nouveau SSD
2. Réinstaller Debian (1h)
3. Réinstaller Docker (30min)
4. Restore backup :
   ```bash
   rsync -avz /mnt/backup/latest/ /home/maskass/minecraft-automation/servers/
   ```
5. Redémarrer : `docker compose up -d`

**Amélioration** : Backup off-site (Backblaze B2 à 0.10€/mois).

---

# ANNEXES

## Matrice des flux (simplifié)

| Source | Destination | Port | Autorisé ? |
|--------|-------------|------|-----------|
| Internet | Serveur | 2222 |   oui SSH admin |
| Internet | Serveur | 1194 |  oui OpenVPN |
| Internet | Serveur | 443 | oui HTTPS |
| Internet | API | 5000 |  non Protégé |
| Internet | Minecraft | 25565 |  non Protégé |
| VPN | API | 5000 |  OK |
| VPN | Minecraft | 25565 |  OK |
| API | PostgreSQL | 5432 |  OK |

## Docker Compose (complet)

```yaml
version: '3.8'

services:
  api_server:
    build: ./backend
    ports: ["5000:5000"]
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./servers:/home/maskass/minecraft-automation/servers
    environment:
      - DB_HOST=postgres
      - DB_PASSWORD=${DB_PASSWORD}
      - SECRET_KEY=${FLASK_SECRET_KEY}
    depends_on:
      - postgres
    restart: unless-stopped
    networks:
      - minecraft-net

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - minecraft-net

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - api_server
    restart: unless-stopped
    networks:
      - minecraft-net

networks:
  minecraft-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  pgdata:
```

---

## CONCLUSION

Ce DAT décrit l'architecture technique de MineHost. On self-host sur un PC Debian avec Docker. Tous les choix sont justifiés (coûts, sécurité, simplicité).

**Chiffres clés** :
- Infrastructure : 30€/mois (électricité)
- Capacité : 15-20 serveurs Minecraft
- Marge : 85%
- RTO : 1h, RPO : 24h

**Points forts** :
- Sécurité Zero Trust (VPN obligatoire)
- Coûts optimisés (94% moins cher qu'Azure)
- Contrôle total (root access)

**Améliorations futures** :
- Backup off-site automatique
- Haute disponibilité (2+ serveurs)
- Auto-scaling

---

**Auteurs** : Aydemir Alper, El Mensi Mehdi
