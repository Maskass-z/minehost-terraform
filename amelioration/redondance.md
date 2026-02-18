# Axe d'amélioration – Monitoring (C6)

Ce document définit la stratégie de surveillance et de métrologie pour la plateforme **MineHost**. L'objectif est de passer d'une gestion réactive à une maintenance proactive en assurant une visibilité totale sur la santé du système, des conteneurs et du réseau.

## 1. Monitoring Système et Infrastructure

### Cible
Assurer la disponibilité des ressources matérielles et virtuelles (CPU, RAM, Disque) supportant les instances de jeu.

### Statut actuel
L'analyse des performances est rudimentaire :
* Utilisation de commandes manuelles telles que `top`, `htop` ou `df -h` lors des sessions d'administration.
* Surveillance des ressources Docker via `docker stats` en ligne de commande.
* Aucune conservation historique des données de performance.

### Problématique et Risques
* **Indisponibilité silencieuse** : Un service peut être arrêté sans que l'administrateur n'en soit informé avant la plainte d'un utilisateur.
* **Saturation des ressources** : Risque de crash brutal (Out Of Memory Kill) si une instance Minecraft consomme plus que prévu, faute d'alertes de seuil.
* **Diagnostic difficile** : Sans historique, il est impossible d'identifier la cause d'un ralentissement survenu dans le passé (ex: pic de charge à 3h du matin).

### Améliorations proposées

**A. Collecte de métriques centralisée**
* Mise en place de **Prometheus** comme base de données temporelle pour stocker les métriques.
* Déploiement de **Node Exporter** sur chaque serveur Debian pour remonter l'état de l'hôte (CPU, Température, I/O Disque).
* Utilisation de **cAdvisor** pour surveiller spécifiquement la consommation de chaque conteneur Docker en temps réel.

**B. Visualisation et Tableaux de Bord**
* Déploiement de **Grafana** pour centraliser les données dans des dashboards visuels.
* Création d'une vue "NOC" (Network Operations Center) permettant de visualiser d'un coup d'œil la charge globale de la flotte MineHost.

---

## 2. Monitoring Applicatif et Métrologie Minecraft

### Cible
Surveiller la qualité de l'expérience de jeu (Lag, accès réseau) et la disponibilité des services web.

### Statut actuel
* Le statut des serveurs Minecraft est vérifié visuellement dans le client de jeu ou via les logs Docker.
* Aucune mesure de la latence réseau (Ping) ou de la fluidité du moteur de jeu (TPS).

### Problématique et Risques
* **Dégradation de l'expérience** : Un serveur peut être "allumé" mais injouable (TPS trop bas).
* **Faille d'accès** : La dashboard peut être en ligne mais incapable de communiquer avec l'API, rendant le service inutilisable pour le client.

### Améliorations proposées

**A. Sondes de disponibilité (Blackbox)**
* Utilisation de **Prometheus Blackbox Exporter** pour tester périodiquement les ports de jeu (25565) et les points d'entrée HTTP.
* Vérification automatique des codes de retour (HTTP 200) pour la dashboard et l'API.

**B. Indicateurs métier Minecraft**
* Intégration de plugins d'exportation (type *Prometheus Exporter*) directement dans les instances Minecraft pour remonter :
    * Le nombre de joueurs connectés.
    * Les **TPS (Ticks Per Second)** : indicateur réel de la fluidité du serveur.
    * L'utilisation de la mémoire Java (Heap Usage).

---

## 3. Système d'Alerting et Logs

### Cible
Alerter en temps réel les administrateurs en cas d'anomalie critique.

### Statut actuel
* Les erreurs sont consignées localement dans les fichiers logs de chaque conteneur.
* La détection d'incident dépend de la surveillance humaine.

### Améliorations proposées

**A. Centralisation des Logs (Logging)**
* Mise en œuvre d'une stack **Loki + Promtail** pour agréger tous les logs Docker dans une interface unique.
* Possibilité de rechercher des erreurs spécifiques (ex: "Can't keep up!") sur l'ensemble des serveurs simultanément.

**B. Alerting Automatisé**
* Configuration de **Alertmanager** pour envoyer des notifications critiques :
    * **Canaux** : Discord, Slack ou Email.
    * **Critères** : Serveur Down, CPU > 90%, ou perte de connexion VPN.

---

## Synthèse de l'impact

| Composant | Risque actuel | Solution cible | Bénéfice |
| :--- | :--- | :--- | :--- |
| **Ressources Hôte** | Saturation invisible | Prometheus + Grafana | Anticipation des besoins en scalabilité |
| **Instances de jeu** | Lag non détecté | Minecraft Exporter (TPS) | Garantie d'une expérience de jeu fluide |
| **Disponibilité** | Alerte par l'utilisateur | Alertmanager (Discord/Mail) | Réduction drastique du temps de réaction |
| **Logs** | Perte au redémarrage | Stack Loki | Analyse post-mortem facilitée |

## Conclusion
Le passage à une infrastructure monitorée transforme MineHost en une plateforme **professionnelle et fiable**. Cette visibilité accrue permet non seulement de résoudre les incidents plus rapidement, mais aussi d'optimiser les coûts en ajustant les ressources au plus près des besoins réels des joueurs.
