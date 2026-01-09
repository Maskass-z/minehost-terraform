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
- USR-003 : 90% de disponibilité minimum

**Côté technique** :
- TEC-001 : Infrastructure basée sur Docker
- TEC-002 : Isolation stricte des serveurs
- TEC-003 : Sauvegardes automatiques

**Côté sécurité** :
- SEC-001 : Protection contre les DDoS
- SEC-002 : Chiffrement bout en bout
- SEC-003 : Serveurs invisibles depuis Internet (cloaking via VPN)

---

## 2. BESOINS FONCTIONNELS

### User Stories (exemples)

**US-001 - Créer un compte**  
Un visiteur arrive sur le site, entre son email et un mot de passe (minimum 8 caractères et son compte est activé.

**US-002 - Commander un serveur**  
L'utilisateur choisit un nom (lettres minuscules et chiffres uniquement), sélectionne la RAM (2, 4 ou 8GB), et clique sur "Créer". Le provisioning prend environ 120 secondes. Il reçoit un fichier .ovpn pour se connecter au VPN, et une IP privée du type 10.8.x.x:xxxxx pour accéder à son serveur.

**US-003 - Arrêter le serveur**  
L'utilisateur clique sur "Arrêter". Le système fait une sauvegarde automatique, stoppe le conteneur Docker en 10 secondes, et la facturation s'arrête immédiatement.

### Les exigences principales

**Authentification** :
- EXI-001 : Créer un compte avec email + mot de passe
- EXI-002 : Les mots de passe sont hachés avec Scrypt (pas de plaintext en base)

**Gestion des serveurs** :
- EXI-006 : Provisioning en moins de 120 secondes
- EXI-007 : Choix de RAM : 2GB, 4GB ou 8GB
- EXI-009 : Start/Stop à volonté, autant de fois qu'on veut

**Sécurité** :
- EXI-011 : Les serveurs sont accessibles UNIQUEMENT via VPN
- EXI-012 : VPN avec mots de passe

---

## 3. CONTRAINTES TECHNIQUES

### Sécurité

**SEC-C01** : Pas de secrets en dur dans le code  
→ Solution : Fichier .env avec variables d'environnement

**SEC-C02** : Protection contre les injections SQL  
→ Solution : SQLAlchemy avec requêtes paramétrées (ORM)

**SEC-C03** : Rate limiting de 10 requêtes par seconde par IP  
→ Solution : Flask-Limiter + Redis

### Performance

**PERF-C01** : Provisioning en moins de 120 secondes (percentile 90)  
Si on dépasse, on perd notre avantage compétitif.

**PERF-C02** : Latence API sous 200ms (percentile 95)  
Si on dépasse, l'expérience utilisateur devient mauvaise.

**PERF-C04** : Disponibilité de 90% minimum  
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
- **Frontend** : Jinja2 (HTML/Flask)
- **Orchestration** : Docker SDK Python
- **Logs temps réel** : Docker SDK Tail

### Sécurisation du code

- **Validation des inputs** : Regex `^[a-z0-9-]{3,20}$` pour les noms
- **Protection BOLA/IDOR** : Vérification `if server.owner_id != current_user.id: abort(403)`
- **Rate limiting** : 10 requêtes par seconde par IP

---

## 5. INFRASTRUCTURE SELF-HOSTED

### Le serveur

On a un serveur Debian 12 :
- **CPU** : 8 vCPU
- **RAM** : 8GB
- **Disque** : 512GB SSD
- **Docker** : Engine 24.0 + Docker Compose 2.20

Capacité : 15-20 serveurs Minecraft simultanés.

L'isolation est faite par Docker.

### Le stockage

Les données sont stockées dans des volumes Docker locaux

Ça persiste même si le conteneur est arrêté ou supprimé.

**Backups automatiques** : Un script rsync tourne tous les jours à 4h du matin et copie tout vers un stockage externe.  /!\ a faire /!\

### Le réseau

**Architecture** :
```
Internet 
    ↓
[OpenVPN Server]
    ↓
Réseau Docker
    ↓
Conteneurs Minecraft
```

## 6. SÉCURITÉ

### Zero Trust & VPN

On a un serveur OpenVPN qui tourne sur le serveur principal. L'authentification se fait par mots de passe.

Le workflow :
1. L'utilisateur commande un serveur
2. L'utilisateur télécharge le fichier .ovpn
3. Il se connecte au VPN
4. Il peut accéder à son serveur via l'IP privée Docker

### Durcissement Docker (CIS Benchmark)

- **User non-root** : Les conteneurs tournent avec UID 1000

### Gestion des secrets

On utilise un fichier `.env` (qui est dans .gitignore) :

```python
FLASK_SECRET_KEY
```

---

## 7. FINOPS (optimisation des coûts)

### Mutualisation

L'utilisation de Docker permet une densité élevée. la mutualisation permet de diviser le coût fixe du serveur par le nombre de conteneurs.

Coût par serveur (si 15 serveurs) : ~1€ / mois.

Marge brute : En vendant l'accès 10€, la marge dépasse les 65%, atteignant les 85% visés sur des infrastructures plus denses.

## 8. POURQUOI CES CHOIX

On a comparé plusieurs solutions :

**Self-Hosting vs Cloud Azure vs Kubernetes**

Self-Hosting (notre choix) :
- Coûts : 55€/mois (VPS) ou 150€/mois (dédié) ou 1000€ Serveur privé
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
Mesure : Test IG

**Disponibilité** : 90% minimum  
Mesure : Mesure test sur 1 mois

---

## 11. PLANNING 

MVP	100%	Aucun, le moteur Docker SDK est stable.
Hardening	70%	La gestion du ReadOnly rootfs peut bloquer certains plugins Minecraft.
FinOps	40%	L'auto-shutdown nécessite une gestion fine des ports RCON.
Production	10%	La RAM (8Go) est le goulot d'étranglement principal.
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
Électricité : Un PC qui tourne 24h/24 consomme environ 100W à 150W en charge.

Calcul : ~0.15kWh × 24h × 30j × 0.23€ = 25€/mois.

Connexion Internet : Déjà payée

Maintenance & Amortissement : Provision pour remplacement de pièces (SSD/Ventilation) : 5€/mois.

Total OPEX (Coûts d'exploitation) : 30€/mois.

Le retour sur investissement (ROI)
Offre Starter 512MB/1GB : Prix 9.99€/mois | Coût marginal (Élec/Data) : ~0.20€ | Marge : 98%

Avec ton infrastructure actuelle (Capacité max 15-20 serveurs) :

Chiffre d'affaires (20 clients) : 199.80€/mois

Coûts (Élec + Maintenance) : 30€/mois

Marge Nette : 169.80€/mois (85% de marge)

Break-even : 3 clients seulement pour couvrir tes factures d'électricité.
---

## 14. LES TESTS

**Test "Noisy Neighbor" (Isolation)** : On sature le CPU d'un conteneur à 100% avec un script de calcul.

**Critère de succès** : L'API Flask et les autres serveurs Minecraft répondent toujours grâce aux limites cgroups (cpu_quota).

**Vérification OpenVPN** : Test de "Leak" pour vérifier qu'aucun port (5000 ou 5432) n'est exposé sur ton IP publique Orange/SFR/Free.

**Coupure Électrique** : Test de redémarrage automatique du PC et de tous les conteneurs au retour du courant (Bios : Restore on AC Power Loss).

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


---

## 16. ADMINISTRATION
**Déploiement et Maintenance**
**Commande de mise à jour flash : Pour mettre à jour ton code sans tout couper :**

docker compose up -d --build api_server

**Vérification de l'état :**

docker compose ps

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
