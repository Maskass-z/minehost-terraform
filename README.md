# 💡 Projet – Déploiement automatisé d’un serveur Minecraft

Le but du projet est de créer une plateforme web qui permet à n’importe quel utilisateur de déployer automatiquement un serveur Minecraft sur une machine virtuelle, en quelques clics.

L’ensemble repose sur trois technologies principales :

Node.js / Express → API web qui reçoit les demandes des utilisateurs,

Terraform → outil d’infrastructure as code pour créer et configurer la VM,

HTML / JavaScript → interface web simple pour remplir le formulaire utilisateur.

 **Fonctionnement global**

L’utilisateur remplit un formulaire web :
Il choisit son pseudo, la version Minecraft, la taille de la VM et la région (Azure ou local VirtualBox).

L’API Node.js reçoit la requête et :

génère un mot de passe admin et un port aléatoire,

copie les fichiers Terraform,

crée un dossier unique (ex: instances/alex_2025-11-12/),

écrit un fichier terraform.tfvars avec les valeurs du formulaire,

exécute terraform init puis terraform apply.

Terraform déploie la VM :

crée une machine virtuelle (Azure ou VirtualBox selon l’environnement),

configure le réseau et les ports,

exécute un script d’installation Minecraft sur la VM (Java, serveur, eula).

Résultat retourné à l’utilisateur :
L’API renvoie l’IP publique et le port du serveur Minecraft.
→ L’utilisateur peut se connecter directement depuis son client Minecraft.

 **Architecture du projet**
minecraft-terraform-api/
├── app.js                  → API Node.js/Express principale
├── package.json            → Dépendances Node.js
├── frontend/index.html     → Formulaire utilisateur
├── terraform_templates/    → Templates Terraform
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── install_minecraft.sh
└── instances/              → Dossiers créés par utilisateur (VM personnalisée)

 **Objectif technique**

Automatiser la création d’une VM et l’installation du serveur Minecraft.

Simplifier l’expérience utilisateur via un simple formulaire web.

Centraliser la gestion des serveurs (un serveur différent par utilisateur).

Rendre le processus reproductible grâce à Terraform (infrastructure as code).

 **Compétences visées**

Administration système (création et gestion de VMs).

Automatisation avec Terraform.

Développement d’API avec Node.js/Express.

Hébergement et gestion d’un service applicatif (Minecraft).

Sauvegarde, restauration et supervision d’un service en ligne.

 **Résultat attendu**

À la fin du projet, il faut que :
✅ Le site web fonctionne et permette de créer une VM automatiquement.
✅ Le serveur Minecraft soit opérationnel (connexion depuis le client).
✅ Les fichiers Terraform et scripts soient personnalisés et fonctionnels.
✅ Une documentation complète (5 écrits + oral) rende compte du projet.


