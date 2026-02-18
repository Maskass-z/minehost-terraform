# Exemple complet – Sauvegarde puis restauration

## Création des sauvegardes

### Dump PostgreSQL

```bash
pg_dump minehost | gzip > /opt/backups/postgres_2026-02-18.sql.gz
````

### Archive des volumes Minecraft

```bash
tar -czf /opt/backups/minecraft_2026-02-18.tar.gz \
/home/maskass/minecraft-automation/servers/
```

### Archive de la configuration

```bash
tar -czf /opt/backups/config_2026-02-18.tar.gz \
/opt/minehost/.env \
/opt/minehost/docker-compose.yml \
/home/maskass/minecraft-automation/scripts/ \
/etc/openvpn/ \
/etc/iptables
```

### Synchronisation vers VM Azure

```bash
rsync -avz /opt/backups/ backupuser@azure-vm:/data/minehost-backups/
```

---

## Simulation d’incident

Pour illustrer la restauration, on supprime temporairement les données locales :

```bash
rm -rf /home/maskass/minecraft-automation/servers/*
psql minehost -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
rm /opt/minehost/.env
rm /opt/minehost/docker-compose.yml
```

---

## Restauration depuis les sauvegardes

### Récupérer les archives depuis Azure

```bash
rsync -avz backupuser@azure-vm:/data/minehost-backups/ /opt/backups/
```

### Restaurer PostgreSQL

```bash
gunzip -c /opt/backups/postgres_2026-02-18.sql.gz | psql minehost
```

### Restaurer les volumes Minecraft

```bash
tar -xzf /opt/backups/minecraft_2026-02-18.tar.gz -C /
```

### Restaurer configuration et scripts

```bash
tar -xzf /opt/backups/config_2026-02-18.tar.gz -C /
```

### Redémarrer les serveurs

```bash
docker-compose -f /opt/minehost/docker-compose.yml up -d
```

---

## 4️⃣ Vérification

* Les mondes Minecraft sont restaurés et fonctionnels
* La base PostgreSQL contient tous les utilisateurs et serveurs
* La configuration et les scripts sont présents
* Les conteneurs Docker démarrent correctement

