Voici le `backup.md` complet pour ton dossier `backup/` :

# Procédure de sauvegarde

## Objectif

Sauvegarder quotidiennement les données critiques de MineHost sur la VM locale et synchroniser vers la VM Azure dédiée.

---

## Étapes

### 1. Dump PostgreSQL

```bash
pg_dump minehost | gzip > /opt/backups/postgres_$(date +%F).sql.gz
````

### 2. Archive des volumes Minecraft

```bash
tar -czf /opt/backups/minecraft_$(date +%F).tar.gz /opt/minehost/data
```

### 3. Archive configuration plateforme

```bash
tar -czf /opt/backups/config_$(date +%F).tar.gz \
/opt/minehost/.env \
/opt/minehost/docker-compose.yml \
/opt/minehost/scripts \
/etc/openvpn \
/etc/iptables
```

### 4. Synchronisation vers VM Azure

```bash
rsync -avz /opt/backups/ backupuser@azure-vm:/data/minehost-backups/
```

### 5. Rotation des archives

**Local (7 jours) :**

```bash
find /opt/backups -type f -mtime +7 -delete
```

**Azure (14 jours) :**

```bash
ssh backupuser@azure-vm "find /data/minehost-backups -type f -mtime +14 -delete"
```

---

## Optionnel – automatisation cron

Créer un script `/usr/local/bin/minehost-backup.sh` avec toutes les commandes ci-dessus et ajouter à la crontab :

```bash
0 4 * * * /usr/local/bin/minehost-backup.sh
```

Cette configuration déclenche automatiquement la sauvegarde tous les jours à 4h du matin.
