# Axe d'amélioration – Gestion d’incidents (C7)

Ce document définit la stratégie de structuration et de réponse aux anomalies pour la plateforme **MineHost**. L'objectif est de passer d'une correction artisanale à un cycle de vie d'incident industrialisé, garantissant une résolution rapide et une communication transparente.

## 1. Structuration du Support et Remontée d'Incidents

### Cible
Centraliser toutes les anomalies (bugs, crashs serveurs, problèmes VPN) dans un système de suivi unique pour éviter la perte d'informations.

### Statut actuel
Actuellement, la gestion est **informelle** :
* Les erreurs sont repérées via les logs Docker en cas de plainte.
* Il n'existe pas de canal dédié pour qu'un utilisateur signale une panne.
* Le suivi de la résolution se fait de mémoire ou via des notes éparpillées.

### Problématique et Risques
* **Oubli d'incidents** : Sans centralisation, certains tickets "mineurs" peuvent être oubliés.
* **Absence d'historique** : Impossible de repérer si un serveur Minecraft crash de manière récurrente (problème de pattern).
* **Frustration utilisateur** : L'absence de visibilité sur la prise en compte d'un problème réduit la confiance envers MineHost.

### Améliorations proposées
* **Ticketing unifié** : Mise en place d'un outil de gestion des tickets.
    * *Option "Dev"* : Utilisation des **GitHub/GitLab Issues** avec des *templates* précis (Description, Étapes pour reproduire, Comportement attendu).
    * *Option "Service"* : Installation d'un outil léger comme **GLPI** ou **Zammad** pour séparer les demandes de support des bugs de code.
* **Canal d'urgence** : Création d'un Webhook automatisé qui poste une alerte sur un canal **Discord** dédié dès qu'une erreur critique est détectée par le monitoring.

---

## 2. Communication et Transparence (Status Page)

### Cible
Informer les utilisateurs en temps réel de l'état de santé des services MineHost.

### Statut actuel
* Aucun moyen de savoir si la plateforme est en maintenance ou subit une panne généralisée sans tester soi-même les services.

### Problématique et Risques
* **Surcharge du support** : En cas de panne majeure, tous les utilisateurs posent la même question au même moment.
* **Image de marque** : Une communication inexistante lors d'une panne donne une image de service non professionnel.

### Améliorations proposées
* **Page de statut publique** : Déploiement d'une solution type **Cachet** ou **Statping**.
    * Cette page affiche l'état opérationnel de chaque composant (VPN, API, Serveurs de jeu).
    * Elle permet d'annoncer les **maintenances planifiées** à l'avance.
* **Automatisation** : Couplage avec le monitoring (Prometheus) pour que la page de statut passe automatiquement en "Incident partiel" si un nœud Debian tombe.

---

## 3. Procédures de Résolution et Post-Mortem

### Cible
Standardiser la manière dont les incidents sont traités pour gagner en efficacité.

### Statut actuel
* Résolution "au cas par cas" sans procédure établie.

### Améliorations proposées
* **Création d'un Runbook** : Rédaction d'un guide technique (Wiki) listant les commandes de secours pour les incidents fréquents (ex: "Comment redémarrer proprement le cluster VPN sans perdre les sessions").
* **Processus de Post-Mortem** : Pour chaque incident majeur (coupure > 1h), rédaction d'un document simple :
    1. **Cause racine** (Pourquoi c'est arrivé ?)
    2. **Actions immédiates** (Comment on a réparé ?)
    3. **Actions préventives** (Comment éviter que cela recommence ?)

---

## Synthèse de l'impact

| Composant | Risque actuel | Solution cible | Bénéfice |
| :--- | :--- | :--- | :--- |
| **Signalement** | Perte d'infos / Oubli | Ticketing (GitHub/Jira) | Traçabilité totale des bugs |
| **Information** | Utilisateur aveugle | Status Page publique | Réduction des plaintes support |
| **Réparation** | Dépendance humaine | Runbooks & Post-mortem | Capitalisation du savoir technique |

## Conclusion
La gestion d'incidents ne se limite pas à "réparer ce qui est cassé". En industrialisant ces processus, MineHost s'assure que chaque erreur devient une opportunité d'amélioration. C'est le complément indispensable du monitoring : le monitoring voit l'erreur, la gestion d'incidents la traite.
