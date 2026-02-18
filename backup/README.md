# Plan de sauvegarde – MineHost

## 1. Description globale de la sauvegarde

MineHost utilise une stratégie de sauvegarde multi-niveaux pour sécuriser toutes les données critiques de la plateforme et des serveurs Minecraft.

Les éléments sauvegardés sont :

- **Volumes Minecraft** : mondes, plugins, playerdata de chaque serveur  
  Chemin : `/home/maskass/minecraft-automation/servers/{server_name}`
- **Base PostgreSQL locale** : comptes utilisateurs, mapping serveurs, facturation  
  DB : `minehost` → dump via `pg_dump`
- **Configuration et scripts critiques** : fichiers `.env`, `docker-compose.yml`, scripts d’automatisation, configuration OpenVPN, règles iptables

Chaque jour à 4h du matin, trois archives séparées sont créées et horodatées dans `/opt/backups/`.  
Elles sont ensuite synchronisées de manière sécurisée vers une **VM Azure dédiée** via rsync sur SSH.

Cette méthode permet une **restauration complète en moins de 10 minutes** et protège contre les pertes accidentelles, erreurs humaines ou crash serveur.

---

## 2. Indicateurs de sauvegarde (liste exhaustive théorique)

- **Infrastructure / Projet**
  - `.env`  
  - `docker-compose.yml`  
  - Scripts d’automatisation (`/home/maskass/minecraft-automation/scripts/`)  
  - Configuration OpenVPN (`/etc/openvpn`)  
  - Règles iptables custom (`/etc/iptables`)  

- **Données applicatives**
  - Volumes Minecraft par serveur : `/home/maskass/minecraft-automation/servers/{server_name}`  
  - Plugins, world, playerdata, server.properties, logs

- **Base de données**
  - PostgreSQL locale (DB `minehost`)  

---

## 3. Éléments réellement sauvegardés actuellement

- Volumes Minecraft (`/home/maskass/minecraft-automation/servers/`)  
- Base PostgreSQL (dump compressé via `pg_dump`)  
- Configuration et scripts critiques (`.env`, docker-compose.yml, scripts, OpenVPN, iptables)  
- Rotation locale : 7 jours  
- Rotation distante sur VM Azure : 14 jours  

---

## 4. Documentation détaillée

- [Procédure de sauvegarde](backup.md)  
- [Procédure de restauration](restore.md)  
- [Exemple complet](example.md)
