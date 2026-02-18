# Axe d'amélioration – Automatisation (C8)

Ce document détaille la stratégie d'industrialisation de la plateforme **MineHost**. L'objectif est d'atteindre un déploiement "Zero-Touch", où l'intégralité de l'infrastructure et des services peut être recréée de manière identique en quelques minutes à partir de machines vierges.

---

## 1. Provisionnement de l'Infrastructure (IaC)

### Cible
Automatiser la création des ressources Cloud (VM, Réseaux, Sécurité) sur Azure.

### Statut actuel
* Le provisionnement des machines virtuelles Debian et la configuration des règles de pare-feu (NSG) sont effectués manuellement via le portail Azure.
* Cette méthode est chronophage et difficilement documentée, rendant la réplication de l'environnement complexe.

### Problématique et Risques
* **Erreur humaine** : Oubli d'une règle de port ou d'une extension de disque.
* **Incohérence** : Risque d'avoir des différences de configuration entre l'environnement de test et celui de production.

### Amélioration proposée : Terraform
L'utilisation de **Terraform** permet de définir l'infrastructure sous forme de code :
* **Déclaration** : Un fichier `.tf` décrit les VM, la taille des disques et les sous-réseaux.
* **Reproductibilité** : Une simple commande `terraform apply` permet de remonter toute l'architecture Azure à l'identique.
* **Versionnage** : Le code de l'infrastructure est stocké sur Git, permettant de suivre chaque modification.

---

## 2. Configuration et Déploiement Applicatif

### Cible
Installer les dépendances (Docker, VPN, API) et déployer les services de manière uniforme.

### Statut actuel
* L'installation des paquets et la configuration des fichiers système (OpenVPN, Docker) reposent sur des scripts shell partiellement manuels ou des exécutions unitaires.

### Amélioration proposée : Ansible & CI/CD
* **Ansible** : Mise en place de *Playbooks* pour automatiser la configuration post-provisionnement.
    * Installation automatique de Docker et des certificats SSL.
    * Configuration durcie du serveur SSH et des accès VPN.
    * Déploiement des fichiers de configuration de la Dashboard et de l'API.
* **Pipeline CI/CD (GitHub Actions)** :
    * À chaque mise à jour du code, un pipeline construit l'image Docker, la teste, et la déploie automatiquement sur les serveurs de production via SSH/Ansible.



---

## 3. Automatisation de la Maintenance et Sauvegardes

### Cible
Garantir la pérennité des données sans intervention humaine.

### Statut actuel
* Les sauvegardes des mondes Minecraft et des bases de données sont soit manuelles, soit basées sur des scripts locaux sans vérification d'intégrité déportée.

### Amélioration proposée
* **Scripts de Backup Idempotents** : Création de scripts (Shell ou Python) déclenchés par des *Cron Jobs* pour :
    1. Compresser les dossiers de jeux.
    2. Exporter les dumps PostgreSQL.
    3. Envoyer les archives vers un **Azure Blob Storage** ou un serveur de stockage distant.
* **Rotation automatique** : Mise en place d'une politique de rétention (ex: garder les 7 dernières sauvegardes quotidiennes et les 4 dernières hebdomadaires) pour optimiser l'espace disque.

---

## Synthèse de l'impact

| Composant | Méthode actuelle | Solution cible | Gain attendu |
| :--- | :--- | :--- | :--- |
| **Infrastructure** | Manuelle (Azure Portal) | **Terraform** | Déploiement 10x plus rapide |
| **Configuration** | Scripts shell / Manuel | **Ansible** | Standardisation et sécurité |
| **Déploiement** | Manuel | **CI/CD GitHub Actions** | Livraison continue sans erreur |
| **Maintenance** | Ponctuelle | **Cron & Cloud Backup** | Sécurité des données garantie |

## Conclusion
L'automatisation complète via l'approche **Infrastructure as Code** fait passer MineHost d'un projet artisanal à un produit industriel. Cela permet de se concentrer sur l'ajout de fonctionnalités plutôt que sur la gestion fastidieuse du serveur, tout en garantissant une résilience maximale face aux erreurs de configuration.
