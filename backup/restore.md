# Procédure de restauration – MineHost

## Objectif

Restaurer complètement les serveurs Minecraft, la base PostgreSQL et les fichiers de configuration depuis les sauvegardes locales ou distantes sur la VM Azure.

---

## Étapes de restauration

### Archives Azure

```bash
rsync -avz backupuser@azure-vm:/data/minehost-backups/ /opt/backups/
````

* Permet de rapatrier les archives distantes sur le serveur principal
* Flux SSH sortant sécurisé

---

### PostgreSQL

```bash
gunzip -c /opt/backups/postgres_YYYY-MM-DD.sql.gz | psql minehost
```

* Remplace la base `minehost` existante
* Contient utilisateurs, mapping serveurs, facturation et ports

---

### volumes Minecraft

```bash
tar -xzf /opt/backups/minecraft_YYYY-MM-DD.tar.gz -C /
```

* Remplace les données des serveurs Minecraft
* Chemin cible : `/home/maskass/minecraft-automation/servers/`
* Inclut mondes, plugins, playerdata et fichiers de configuration serveur

---

### configuration

```bash
tar -xzf /opt/backups/config_YYYY-MM-DD.tar.gz -C /
```

* Inclut `.env`, `docker-compose.yml`, scripts d’automatisation, OpenVPN, iptables

---

### Redémarrer les serveurs Minecraft

```bash
docker-compose -f /opt/minehost/docker-compose.yml up -d
```

* Redémarre tous les conteneurs de manière propre
* Vérifier le statut des serveurs avec :

```bash
docker ps
```

---

### Vérifications post-restauration

* Les mondes Minecraft sont accessibles et intacts
* La base PostgreSQL fonctionne correctement
* Les scripts et configurations sont présents
* Les conteneurs Docker démarrent sans erreur

---

### Notes

* Restaurer dans l’ordre : **PostgreSQL → Volumes → Config**
* Utiliser les archives horodatées pour correspondre à une date précise si besoin
* Le RTO prévu : <10 minutes pour un serveur Minecraft typique
* Flux sécurisé : aucune ouverture entrante, connexion sortante uniquement
