# Axe d'amélioration – Redondance (C5)

Ce document détaille les stratégies de haute disponibilité (HA) envisagées pour la plateforme **MineHost**. L'objectif est d'éliminer les points de défaillance uniques (*Single Points of Failure*) afin de garantir un service ininterrompu aux joueurs et aux administrateurs.

---

## 1. Redondance de l'Infrastructure d'Hébergement

### Cible
Garantir que les serveurs Minecraft restent accessibles même en cas de panne matérielle ou logicielle d'un nœud d'hébergement.

### Statut actuel
Actuellement, MineHost repose sur une architecture monolithique :
* Un unique serveur **Debian** supporte l'intégralité des conteneurs Docker Minecraft.
* L'arrêt de ce serveur (mise à jour noyau, panne Azure, saturation CPU/RAM) entraîne l'interruption immédiate de tous les services de jeu.

### Problématique et Risques
* **Indisponibilité totale :** Le "SPOF" (Single Point of Failure) est critique.
* **Perte de données :** En cas de corruption du disque système unique, la récupération des mondes Minecraft dépend uniquement des backups (RTO/RPO élevés).
* **Scalabilité limitée :** Un seul serveur limite le nombre de joueurs simultanés aux ressources d'une seule machine.

### Améliorations proposées

#### A. Cluster de Nodes Docker
L'ajout d'un **second serveur Debian** permet de passer d'une instance isolée à un cluster. 
* **Orchestration :** Utilisation de **Docker Swarm** ou **Kubernetes (K3s)** pour gérer le cycle de vie des conteneurs sur plusieurs nœuds.
* **Réplication :** Déploiement de plusieurs réplicas des services critiques (API, base de données).

#### B. Équilibrage de charge (Load Balancing)
Mise en place d'un répartiteur de charge en amont :
* **Technologie :** HAProxy ou Nginx configuré en mode *Failover*.
* **Mécanisme :** Le répartiteur vérifie la santé (*Health Check*) des serveurs Debian. Si le "Nœud A" ne répond plus, le trafic est instantanément redirigé vers le "Nœud B".

---

## 2. Redondance de l'Accès Réseau (VPN)

### Cible
Sécuriser l'accès des utilisateurs à leurs instances privées sans interruption.

### Statut actuel
L'accès sécurisé repose sur une seule instance **OpenVPN**. 

### Problématique et Risques
* **Coupure d'accès :** Si le service OpenVPN crash, les utilisateurs ne peuvent plus administrer leurs serveurs, même si les serveurs de jeu fonctionnent encore.
* **Saturation :** Le chiffrement VPN est gourmand en CPU ; un seul serveur peut devenir un goulot d'étranglement lors de pics de connexion.

### Améliorations proposées

#### A. Cluster OpenVPN avec Failover
* Déploiement d'une **seconde instance OpenVPN** synchronisée avec la première (partage des certificats et de la base d'utilisateurs).
* Utilisation du protocole **Keepalived** (IP flottante/VIP) : une seule adresse IP publique est exposée. Elle bascule automatiquement d'un serveur VPN à l'autre en moins d'une seconde en cas de défaillance.

#### B. Redondance Géographique (Optionnel)
* Placer le second serveur VPN dans une zone de disponibilité Azure différente pour prévenir une panne majeure du centre de données.

---

## 3. Redondance des Données (Stockage)

### Cible
Éviter la perte des mondes Minecraft et des configurations utilisateurs.

### Statut actuel
Les volumes Docker sont stockés localement sur le disque du serveur Debian unique.

### Améliorations proposées
* **Stockage Distribué :** Mise en œuvre de **GlusterFS** ou **Longhorn** pour répliquer les données des volumes en temps réel sur les deux serveurs Debian.
* **Base de données HA :** Passage d'une instance PostgreSQL simple à un mode **Master-Slave** (Réplication asynchrone) pour garantir l'intégrité des logs et des comptes utilisateurs.

---

## Synthèse de l'impact

| Composant | Risque actuel | Solution cible | Bénéfice |
| :--- | :--- | :--- | :--- |
| **Serveur de Jeu** | Arrêt total si crash VM | Cluster multi-nœuds | Disponibilité > 95% |
| **Accès VPN** | Perte de contrôle distante | Failover Keepalived | Accès permanent |
| **Données** | Perte de fichiers locale | Réplication GlusterFS | Résilience des données |

##  Conclusion
La mise en œuvre de ces mécanismes de redondance transforme MineHost en une solution de classe "Entreprise". Bien que cela augmente les coûts d'infrastructure, c'est une étape indispensable pour garantir la confiance des utilisateurs et la pérennité du service face aux aléas techniques inévitables.

