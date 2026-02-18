# Axe d'amélioration – Gestion d’incidents (C7)

Ce document présente la stratégie de gestion et de résolution des anomalies pour la plateforme **MineHost**. L'objectif est de structurer la remontée d'informations et de garantir un suivi rigoureux jusqu'à la résolution complète des problèmes.

---

## 1. Support Utilisateur et Ticketing

### Cible
Offrir un canal de communication structuré aux clients pour signaler des dysfonctionnements sur leurs instances Minecraft ou leur accès VPN.

### Statut actuel
La gestion est informelle et non centralisée :
* Les retours se font par message direct ou via l'analyse manuelle des logs.
* Aucun historique des problèmes récurrents n'est conservé.
* Pas de distinction entre une simple question de configuration et une panne majeure.

### Problématique et Risques
* **Perte d'information** : Un incident signalé peut être oublié s'il n'est pas consigné dans un registre.
* **Manque de visibilité** : L'utilisateur ne sait pas si son problème est en cours de traitement ou ignoré.
* **Difficulté de priorisation** : Sans outil, il est difficile de traiter en priorité une panne totale d'infrastructure par rapport à un bug mineur d'affichage.

### Améliorations proposées

**A. Ticketing léger via Discord (Bot Support)**
* Intégration d'un bot de ticketing sur le serveur Discord communautaire de MineHost.
* **Workflow** : L'utilisateur crée un "ticket" qui génère un salon privé temporaire, permettant de centraliser les échanges et les captures d'écran.
* **Clôture** : Une fois résolu, le salon est archivé, créant une base de connaissances pour l'équipe technique.

**B. Page de Statut (Status Page)**
* Mise en place d'une page publique (ex: via *Cachet* ou *Statuspage.io*) indiquant l'état en temps réel des services critiques (VPN, API, Serveurs de jeu).
* Permet de réduire le flux de tickets en informant les utilisateurs d'un incident global déjà identifié.

---

## 2. Gestion Interne et Suivi Technique

### Cible
Structurer le travail de l'équipe technique pour la résolution des bugs et des pannes d'infrastructure.

### Statut actuel
* Les tâches correctives sont gérées au fur et à mesure, sans vue d'ensemble.

### Améliorations proposées

**A. Utilisation des GitHub Issues**
* Pour chaque incident technique complexe, une **Issue** GitHub est ouverte.
* Utilisation de **Labels de sévérité** pour définir la priorité :
    * `P0 - Critical` : Infrastructure Down (Action immédiate).
    * `P1 - Major` : Service dégradé (Action sous 24h).
    * `P2 - Minor` : Bug cosmétique ou mineur.

**B. Mise en place de Post-Mortems**
* Pour chaque incident de niveau `P0`, rédaction d'un court document analysant :
    1. La cause racine (Root Cause Analysis).
    2. Les actions menées pour rétablir le service.
    3. Les mesures prises pour éviter que cela ne se reproduise.

---

## 3. Automatisation de la Réponse aux Incidents

### Cible
Réduire le temps moyen de rétablissement du service (MTTR).

### Améliorations proposées
* **Auto-healing** : Configurer Docker pour redémarrer automatiquement les conteneurs Minecraft en cas de crash (`restart: unless-stopped`).
* **Alertmanager** : Coupler le monitoring (C6) à la gestion d'incidents pour ouvrir automatiquement un ticket si un serveur ne répond plus pendant plus de 5 minutes.

---

## Synthèse de l'impact

| Composant | Risque actuel | Solution cible | Bénéfice |
| :--- | :--- | :--- | :--- |
| **Relation Client** | Sentiment d'abandon | Bot Ticketing Discord | Communication claire et rassurante |
| **Transparence** | Silence radio en panne | Status Page publique | Réduction des demandes de support |
| **Suivi Technique** | Oubli de correctifs | GitHub Issues + Labels | Traçabilité et priorisation |
| **Récurrence** | Erreur répétitive | Post-Mortem | Amélioration continue de l'infra |

## Conclusion
Bien que MineHost soit un projet en phase de prototype, l'adoption de ces outils de gestion d'incidents est primordiale pour passer à une phase de production. Cela garantit non seulement la satisfaction des utilisateurs, mais aussi une montée en compétence de l'équipe technique grâce à une organisation rigoureuse.
