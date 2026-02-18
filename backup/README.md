# Plan de sauvegarde – MineHost

## 1. Description globale de la sauvegarde

Le projet MineHost utilise une stratégie de sauvegarde multi-niveaux pour sécuriser les données critiques :

- Données Minecraft (mondes, plugins, playerdata)  
- Base PostgreSQL locale  
- Configuration de la plateforme et scripts critiques  

Chaque jour à 4h, trois archives séparées sont créées, horodatées, et stockées localement dans `/opt/backups/`.  
Elles sont ensuite synchronisées de manière sécurisée vers une **VM Azure dédiée** via rsync sur SSH.  

Cette approche garantit une **restauration rapide (<10 minutes)** et une protection contre les pertes accidentelles, erreurs humaines ou crash serveur.

---

## 2. Indicateurs de sauvegarde (liste exhaustive théorique)

- **Infrastructure / Projet**
  - `.env`
  - `docker-compose.yml`
  - Scripts automation
  - Configuration OpenVPN
  - Règles iptables custom
- **Données applicatives**
  - Volumes Minecraft : `/opt/minehost/data/{user}/{server}`
  - Plugins
  - Playerdata
  - Server.properties
  - Logs pertinents
- **Base de données**
  - PostgreSQL locale (DB `minehost`)

---

## 3. Éléments réellement sauvegardés actuellement

- Volumes Minecraft (`/opt/minehost/data`)  
- Base PostgreSQL (dump gzip)  
- Configuration plateforme et scripts  
- Sauvegardes locales 7 jours  
- Sauvegardes distantes sur VM Azure 14 jours  

---

## 4. Documentation détaillée

- [Procédure de sauvegarde](backup.md)  
- [Procédure de restauration](restore.md)  
- [Exemple complet](example.md)
