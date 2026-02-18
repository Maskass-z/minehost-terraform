# Procédure de sauvegarde – MineHost

## Objectif

Assurer la sauvegarde complète et sécurisée des serveurs Minecraft, de la base PostgreSQL et des fichiers de configuration critiques sur le serveur Debian, avec réplication sur une VM Azure dédiée.

---

## Étapes de sauvegarde

### PostgreSQL

```bash
pg_dump minehost | gzip > /opt/backups/postgres_$(date +%F).sql.gz
````

* Contient : utilisateurs, mapping serveurs, facturation, ports
* Dump compressé pour gagner de la place et faciliter la synchronisation

---

###volumes Minecraft

```bash
tar -czf /opt/backups/minecraft_$(date +%F).tar.gz \
/home/maskass/minecraft-automation/servers/
```

* Contient : `world/`, `playerdata/`, `plugins/`, `server.properties`, logs pertinents
* Chaque serveur est stocké dans un sous-dossier `{server_name}`

---

### configuration

```bash
tar -czf /opt/backups/config_$(date +%F).tar.gz \
/opt/minehost/.env \
/opt/minehost/docker-compose.yml \
/home/maskass/minecraft-automation/scripts/ \
/etc/openvpn/ \
/etc/iptables
```

* Contient les secrets, la configuration Docker et VPN, scripts d’automatisation, règles firewall

---

### Synchronisation azur

```bash
rsync -avz /opt/backups/ backupuser@azure-vm:/data/minehost-backups/
```

* Flux sortant SSH uniquement → respecte l’architecture Zero Trust
* Toutes les archives locales sont copiées vers Azure pour redondance

---

### Rotation des archives

**Local (7 jours)** :

```bash
find /opt/backups -type f -mtime +7 -delete
```

**Distante Azure (14 jours)** :

```bash
ssh backupuser@azure-vm "find /data/minehost-backups -type f -mtime +14 -delete"
```

* Permet de conserver un historique récent et limiter l’espace disque
* Conserve au minimum une copie externe en cas de panne totale du serveur principal

---


### Notes

* Les archives sont **séparées** : Data, PostgreSQL, Config → restauration ciblée possible
* Flux **chiffré via SSH**, aucun port entrant nécessaire
* RTO estimé : <10 minutes pour restauration complète
* RPO : 24h → une sauvegarde quotidienne suffit pour les mondes Minecraft

