# Projet – MineHost : Plateforme d'Hébergement Automatisé de Serveurs Minecraft
 But du projet
Développer une plateforme d'hébergement (Hosting Provider) clé en main permettant à des clients de louer des serveurs Minecraft. Le système génère automatiquement l'infrastructure technique (conteneur Docker) dès la commande, sans intervention humaine, offrant un service disponible 24/7.

 Technologies Principales
L’ensemble repose sur une stack technique optimisée pour la vente de services :

Python / Flask → Backend API qui gère les commandes, la facturation (simulée) et l'orchestration des ressources.

Docker → Moteur de virtualisation légère permettant de générer instantanément les serveurs loués.

PostgreSQL → Base de données pour le suivi des clients, des abonnements et des instances actives.

VPN → Infrastructure réseau privée pour garantir la sécurité et l'exclusivité de l'accès aux locataires.

 Fonctionnement Global (Workflow de Location)
Commande Client : L'utilisateur s'inscrit, choisit une offre (ex: Serveur "Survie" 2Go RAM) et valide sa demande.

Provisionning Automatique :

L'API vérifie la disponibilité des ressources et le quota du client.

Elle pilote le socket Docker pour instancier un nouveau conteneur isolé.

Elle configure les limites de ressources (CPU/RAM) correspondant à l'offre louée.

Livraison du Service :

Le serveur démarre avec un port dédié et un volume de stockage persistant.

Le client reçoit ses accès et peut gérer son serveur (Start/Stop/Logs) via son panel client web.

Accès Sécurisé : Le client se connecte au réseau VPN privé pour accéder à son serveur loué, garantissant une protection totale contre les attaques externes (DDoS).

 Architecture Technique


MINEHOST_CLEAN/
├── app.py                → API de Gestion (Logique métier, quotas location, sécurité)
├── database.py           → Base de données Clients & Inventaire Serveurs
├── docker-compose.yaml   → Infrastructure de l'hébergeur
├── .env                  → Gestion sécurisée des secrets de l'infrastructure
├── Dockerfile            → Image du Panel de Gestion Web
└── templates/            → Espace Client (Dashboard de gestion des locations)
 Objectifs Techniques
Automatisation Totale : Supprimer toute intervention manuelle entre la commande du client et la livraison du serveur.

Rentabilité des Ressources (Docker) : Utiliser des conteneurs plutôt que des VM pour maximiser le nombre de serveurs clients hébergés sur une même machine physique (Densification).

Isolation Multi-locataire : Garantir qu'un client ne puisse jamais impacter ou accéder aux données d'un autre client (Isolation stricte via Docker & PostgreSQL).

Sécurité Commerciale : Protéger l'infrastructure de l'hébergeur (VPN, Firewall Azure) pour garantir la qualité de service (SLA).

 Compétences Visées
Architecture Hébergeur (ISP) : Conception d'une infrastructure capable de délivrer des services à la demande.

DevSecOps : Sécurisation d'une plateforme exposée (Gestion des secrets, Hachage mots de passe, Isolation réseau).

Développement Backend : Création d'une API RESTful Python capable de piloter le système d'exploitation (Docker SDK).

Gestion de Données : Modélisation d'une base de données relationnelle (Clients / Produits / Instances).

 Résultat Attendu
À la fin du projet, la plateforme doit permettre :

 La location instantanée : Un utilisateur clique sur "Créer", le serveur est prêt en quelques secondes.

 La gestion autonome : Le client peut démarrer, arrêter ou supprimer son serveur loué depuis son espace personnel.

 La sécurité de l'hébergeur : L'infrastructure est protégée par un VPN et des règles strictes (Quotas, Validation API).

 L'isolation des clients : Chaque serveur loué est étanche et possède ses propres ressources et fichiers.
