# CAHIER DES CHARGES TECHNIQUE  
**PROJET MINEHOST : Infrastructure Cloud-Native Azure & Sécurité**

**Projet** : Plateforme SaaS d'Hébergement de Serveurs Minecraft  
**Date** : 07 Janvier 2026  
**Auteur** : Aydemir Alper, El Mensi Mehdi 

**Cible** : Direction Technique, Équipe DevOps, Audit de Sécurité  

---

## Sommaire Executive

### Vision du Projet
MineHost est une plateforme d'hébergement automatisée (PaaS/SaaS) permettant de déployer des serveurs Minecraft **isolés, performants et sécurisés en un temps record !**, avec une tarification à l'heure d'utilisation basée sur une architecture de VMs Azure orchestrant des conteneurs Docker.

### Proposition de Valeur
- **Sécurité** : Architecture Zero Trust avec VPN obligatoire (infrastructure invisible depuis Internet)
- **Performance** : Provisioning < 1-2 minutes, isolation Docker multi-niveaux
- **Économie** : Mutualisation des ressources VM + auto-shutdown des conteneurs inactifs

---

## 📋 SOMMAIRE

**PARTIE 1 : ANALYSE DES BESOINS**

1. [CONTEXTE ET COLLECTE DES BESOINS](#1-contexte-et-collecte-des-besoins)  
   1.1. Méthodologie de Collecte des Besoins  
   1.2. Analyse du Marché et Concurrence  
   1.3. Identification des Parties Prenantes  
   1.4. Synthèse des Besoins Recueillis  

2. [EXPRESSION DES BESOINS FONCTIONNELS](#2-expression-des-besoins-fonctionnels)  
   2.1. Objectifs Fonctionnels du Projet  
   2.2. Cas d'Usage et User Stories  
   2.3. Exigences Fonctionnelles Numérotées  

3. [CONTRAINTES ET EXIGENCES TECHNIQUES](#3-contraintes-et-exigences-techniques)  
   3.1. Contraintes de Sécurité  
   3.2. Contraintes de Performance  
   3.3. Contraintes Réglementaires (RGPD)  
   3.4. Matrice de Traçabilité Besoins → Solutions  

**PARTIE 2 : SPÉCIFICATIONS TECHNIQUES**

4. [ARCHITECTURE LOGICIELLE (BACKEND & API)](#4-architecture-logicielle-backend--api)  
   4.1. Stack Technologique (Python/Flask)  
   4.2. Logique d'Orchestration  
   4.3. Sécurisation du Code (AppSec)  

5. [INFRASTRUCTURE CLOUD AZURE](#5-infrastructure-cloud-azure)  
   5.1. Choix du Compute : VMs Azure + Docker  
   5.2. Stratégie de Stockage : Azure Files (Persistance)  
   5.3. Réseau et Isolation : VNet & NSG  

6. [STRATÉGIE DE SÉCURITÉ](#6-stratégie-de-sécurité-defense-in-depth)  
   6.1. Approche "Zero Trust" & Cloaking VPN  
   6.2. Durcissement des Conteneurs (Docker Hardening)  
   6.3. Gestion des Secrets et Identités  

7. [MODÈLE ÉCONOMIQUE & FINOPS](#7-modèle-économique--finops)  
   7.1. Mutualisation des Ressources VM  
   7.2. Algorithme d'Auto-Shutdown  

8. [JUSTIFICATION DES CHOIX TECHNIQUES](#8-justification-des-choix-techniques)  
   8.1. Alternatives Évaluées  
   8.2. Matrice de Décision Multi-Critères  
   8.3. Justification des Technologies Retenues  

9. [ANALYSE DES RISQUES ET OPPORTUNITÉS](#9-analyse-des-risques-et-opportunités)  
   9.1. Matrice des Risques  
   9.2. Opportunités Stratégiques et Business  

10. [INDICATEURS DE PERFORMANCE (KPIs)](#10-indicateurs-de-performance-kpis)  
    10.1. Performance Technique  
    10.2. Sécurité  
    10.3. FinOps  

11. [PLANNING ET ROADMAP](#11-planning-et-roadmap)  

12. [CONFORMITÉ RGPD ET LÉGALE](#12-conformité-rgpd-et-légale)  
    12.1. Protection des Données (Privacy by Design)  
    12.2. Droits Utilisateurs  

13. [BUDGET ET ROI PRÉVISIONNEL](#13-budget-et-roi-prévisionnel)  
    13.1. Coûts d'Infrastructure (OPEX Mensuel)  
    13.2. Rentabilité (ROI)  

14. [STRATÉGIE DE VALIDATION (QA)](#14-stratégie-de-validation-qa)  
    14.1. Tests de Sécurité (Pentest)  
    14.2. Tests de Charge  
    14.3. Tests de Résilience (Chaos Engineering)  

15. [MAINTENANCE ET SUPPORT](#15-maintenance-et-support)  
    15.1. Stratégie de Mise à Jour  
    15.2. Plan de Support Client  
    15.3. Disaster Recovery  

16. [ADMINISTRATION & MAINTENABILITÉ](#16-administration--maintenabilité)  
    16.1. Infrastructure as Code (Terraform)  
    16.2. Monitoring et Observabilité  

[ANNEXES](#annexes)

---

# PARTIE 1 : ANALYSE DES BESOINS

## 1. CONTEXTE ET COLLECTE DES BESOINS

### 1.1. Méthodologie de Collecte des Besoins

**Approche utilisée** : Méthodologie agile avec itérations de recueil des besoins sur 4 semaines.

#### Phase 1 : Étude documentaire (Semaine 1)
- Analyse de 15 hébergeurs Minecraft concurrents (Apex Hosting, Shockbyte, BisectHosting, etc.)
- Étude de 250 avis clients sur TrustPilot et Reddit (r/admincraft, r/minecraft)
- Review de 8 rapports d'incidents de sécurité sur des hébergeurs compromis (2022-2025)
- Analyse des prix du marché : fourchette 3€-25€/mois pour 2-8GB RAM

**Constats clés** :
- 78% des utilisateurs se plaignent de l'insécurité (attaques DDoS, accès non autorisés)
- 65% ont subi au moins 1 panne de plus de 30 minutes dans les 6 derniers mois
- Les hébergeurs low-cost utilisent des VPS mutualisés sans isolation ("Noisy Neighbor Effect")

#### Phase 2 : Interviews utilisateurs (Semaine 2)
**Cible** : 20 utilisateurs répartis en 3 profils

| Profil | Nombre | Méthodologie | Outils |
|--------|--------|--------------|--------|
| **Joueurs occasionnels** (serveurs privés 2-10 joueurs) | 8 | Interviews semi-directifs (30 min) | Google Meet + Typeform |
| **Communautés moyennes** (serveurs 20-100 joueurs) | 7 | Focus group (1h30) | Discord + Miro |
| **Administrateurs expérimentés** (>100 joueurs) | 5 | Interviews approfondis (1h) | Zoom + Notes |

**Questions clés posées** :
1. Quelles sont vos frustrations actuelles avec votre hébergeur ?
2. Quelle est votre tolérance au downtime ? (secondes, minutes, heures)
3. Êtes-vous prêt à payer plus pour une meilleure sécurité ?
4. Quelles fonctionnalités manquent sur le marché ?

**Citations représentatives** :
> *"Mon serveur a été DDoS 3 fois ce mois-ci, l'hébergeur n'a rien fait"* - Admin communauté 50 joueurs  
> *"Je ne comprends rien à Linux, j'ai abandonné l'auto-hébergement"* - Joueur occasionnel  
> *"Je paie 15€/mois mais le serveur lag quand un voisin utilise trop de CPU"* - Admin expérimenté

#### Phase 3 : Questionnaire quantitatif (Semaine 3)
- Diffusion d'un questionnaire en ligne (Google Forms) auprès de 50 répondants
- Taux de réponse : 68% (34 réponses exploitables)
- Segmentation : 60% joueurs occasionnels, 30% communautés moyennes, 10% admins experts

**Résultats statistiques clés** :
- 78% sont insatisfaits de la sécurité de leur hébergeur actuel
- 82% trouvent la configuration technique trop complexe
- 91% seraient intéressés par une tarification à l'usage (vs forfait mensuel)
- 87% accepteraient une connexion VPN pour plus de sécurité

#### Phase 4 : Analyse technique (Semaine 4)

### 1.1. Analyse du Marché et Concurrence

#### Taille du Marché
- **Marché global de l'hébergement de jeux** : 6,5 Mds USD en 2025 (Source : Grand View Research)
- **Part Minecraft** : ~15% du marché (975M USD)
- **Croissance annuelle** : +12% (CAGR 2025-2030)
- **Nombre de serveurs Minecraft actifs dans le monde** : ~500,000 (Source : Minecraft Server List)

#### Principaux Concurrents

| Concurrent | Part de Marché | Prix (2GB RAM) | Forces | Faiblesses |
|------------|---------------|----------------|--------|------------|
| **Apex Hosting** | 22% | 7.49 USD/mois | Support 24/7, Interface intuitive | Mutualisation (performances variables) |
| **Shockbyte** | 18% | 2.50 USD/mois | Prix agressif | **Sécurité faible**, Downtimes fréquents |
| **BisectHosting** | 15% | 8.99 USD/mois | Bonne stabilité | Configuration complexe |
| **Hébergeurs Cloud DIY** (AWS, Azure) | 10% | ~15 USD/mois | Contrôle total | **Expertise technique requise** |
| **Auto-hébergement** (Serveur maison) | 35% | Gratuit (élec.) | Gratuit | **Sécurité très faible**, IP domestique |

#### Positionnement de MineHost

**Notre différenciation** :
1. **Sécurité Premium** : Zero Trust + VPN obligatoire (unique sur le marché)
2. **Provisioning Ultra-Rapide** : < 1-2mins vs 5-15 min chez les concurrents
3. **Isolation Garantie** : Docker + NSG (pas de "Noisy Neighbor")
4. **Simplicité** : Interface Web (pas de SSH/CLI requis)

**Segment cible prioritaire** : Communautés moyennes (20-100 joueurs) prêtes à payer 10-15€/mois pour la qualité.

### 1.2. Identification des Parties Prenantes

| Partie Prenante | Rôle | Besoins/Attentes | Influence | Pouvoir |
|-----------------|------|------------------|-----------|---------|
| **Utilisateurs finaux** (Joueurs Minecraft) | Consommateurs | Serveur rapide, stable, sécurisé | Élevée | Faible |
| **Administrateurs de serveurs** | Clients payants | Interface simple, support réactif, backups | Élevée | Moyen |
| **Direction Technique** | Sponsor interne | ROI, scalabilité, maintenabilité | Élevée | Élevé |
| **Équipe DevOps** | Implémenteurs | Stack technique moderne, documentation | Moyenne | Moyen |
| **RSSI (Responsable Sécurité)** | Validateur sécurité | Conformité ISO 27001, audits | Élevée | Élevé |
| **Direction Générale** | Décideur final | Rentabilité, risques maîtrisés | Critique | Critique |
| **Autorité de régulation (CNIL)** | Compliance RGPD | Protection données, data residency | Moyenne | Élevé |
| **Fournisseur Cloud (Microsoft Azure)** | Partenaire technique | Utilisation optimale des services | Faible | Moyen |

**Stratégie d'engagement** :
- **Utilisateurs** : Bêta privée avec 50 early adopters (feedback continu)
- **Direction** : Points mensuels + dashboards ROI en temps réel
- **RSSI** : Pentests trimestriels + certifications (ISO 27001 visée année 2)

### 1.3. Synthèse des Besoins Recueillis

#### Besoins Métier (Business)
- **BUS-001** : Proposer une offre plus sécurisée que les concurrents low-cost
- **BUS-002** : Atteindre une marge brute de 45% minimum
- **BUS-003** : Scaler jusqu'à 1000 serveurs actifs en 12 mois
- **BUS-004** : Temps de provisioning < 1-2mins (avantage concurrentiel)

#### Besoins Utilisateurs (User Needs)
- **USR-001** : Interface Web simple sans connaissance technique requise
- **USR-002** : Connexion au serveur en < 2 minutes après commande
- **USR-003** : Garantie de disponibilité 99.5% minimum
- **USR-004** : Facturation transparente (pas de frais cachés)
- **USR-005** : Support réactif en cas de problème (< 4h pour incidents majeurs)

#### Besoins Techniques (Technical)
- **TEC-001** : Architecture Cloud-Native avec orchestration automatisée
- **TEC-002** : Isolation stricte entre clients (pas de "Noisy Neighbor")
- **TEC-003** : Sauvegarde automatique des mondes Minecraft
- **TEC-004** : Scalabilité horizontale (ajout de VMs selon la charge)
- **TEC-005** : Infrastructure as Code (reproductibilité)

#### Besoins de Sécurité (Security)
- **SEC-001** : Protection contre les attaques DDoS Layer 7
- **SEC-002** : Chiffrement de bout en bout (données au repos et en transit)
- **SEC-003** : Aucune exposition publique des serveurs (cloaking VPN)
- **SEC-004** : Audits de sécurité trimestriels
- **SEC-005** : Conformité RGPD (data residency France)

---

## 2. EXPRESSION DES BESOINS FONCTIONNELS

### 2.1. Objectifs Fonctionnels du Projet

**Objectif Principal** : Fournir une plateforme SaaS permettant à tout utilisateur de déployer et gérer un serveur Minecraft sécurisé sans compétence technique, avec une facturation à l'usage réel.

**Objectifs Secondaires** :
1. **Simplification** : Réduire le temps de configuration de 30 minutes (moyenne marché) à < 2 minutes
2. **Sécurisation** : Atteindre 0 incident de sécurité sur les 12 premiers mois
3. **Optimisation** : Mutualiser les ressources pour réduire les coûts unitaires
4. **Satisfaction** : Obtenir un NPS (Net Promoter Score) > 50 dès la première année

### 2.2. Cas d'Usage et User Stories

#### **CU-001 : Création d'un compte utilisateur**

**Acteur** : Utilisateur non authentifié  
**Objectif** : Créer un compte pour accéder à la plateforme

**Scénario nominal** :
1. L'utilisateur accède à `https://minehost.com/register`
2. Il remplit le formulaire : Email, Mot de passe (min 12 caractères)
3. Il accepte les CGU et la Politique de Confidentialité
4. Il clique sur "Créer mon compte"
5. Un email de confirmation est envoyé à son adresse
6. Il clique sur le lien de confirmation (valide 24h)
7. Son compte est activé → Redirection vers le dashboard

**Scénario alternatif** :
- L'email existe déjà → Message "Un compte existe déjà avec cet email"
- Le mot de passe est trop faible → Message "Mot de passe insuffisamment sécurisé"

**Critères d'acceptation** :
-  Mot de passe haché en Scrypt (pas en clair)
-  Email de confirmation envoyé en < 5 secondes
-  Validation RGPD (case à cocher obligatoire)

---

#### **CU-002 : Commande d'un nouveau serveur**

**Acteur** : Utilisateur authentifié  
**Objectif** : Commander et provisionner un serveur Minecraft

**User Story** :
> *"En tant qu'utilisateur, je veux commander un serveur en quelques clics pour jouer rapidement avec mes amis sans configuration technique."*

**Scénario nominal** :
1. L'utilisateur se connecte au dashboard
2. Il clique sur "Créer un serveur"
3. Il remplit le formulaire :
   - Nom du serveur : `serveur-de-paul` (alphanumerique uniquement)
   - RAM : 2GB / 4GB / 8GB (choix)
   - Version Minecraft : 1.20.4 (dernière stable par défaut)
4. Il clique sur "Commander" (prix affiché : 0.12€/h)
5. Le provisioning démarre (barre de progression en temps réel)
6. Après ~45 secondes : "Votre serveur est prêt !"
7. L'interface affiche :
   - **Bouton "Télécharger la config VPN"** (fichier .ovpn)
   - Instructions de connexion : "Installez OpenVPN, importez le fichier, connectez-vous au VPN"
   - IP privée du serveur (ex: `10.0.2.15:25565`) - accessible uniquement via VPN

**Scénario alternatif** :
- Nom déjà pris → Message "Ce nom est déjà utilisé, choisissez-en un autre"
- Limite de 5 serveurs atteinte → Message "Vous avez atteint votre quota"
- Provisioning échoue → Retry automatique, support contacté

**Critères d'acceptation** :
-  Provisioning réussi en < 2 minutess (P95)
-  Serveur accessible via VPN en < 2 minutes
-  Logs visibles en temps réel pendant la création

---

#### **CU-003 : Démarrage/Arrêt du serveur**

**Acteur** : Propriétaire du serveur  
**Objectif** : Contrôler l'état du serveur pour gérer les coûts

**User Story** :
> *"En tant qu'utilisateur, je veux pouvoir arrêter mon serveur quand je ne joue pas pour ne pas être facturé inutilement."*

**Scénario nominal** :
1. L'utilisateur accède à la page de son serveur
2. Statut actuel : "En cours d'exécution" (bouton vert)
3. Il clique sur "Arrêter"
4. Le conteneur Docker s'arrête gracieusement en ~10 secondes
5. Statut : "Arrêté" (bouton gris)
6. Facturation s'arrête immédiatement

**Scénario alternatif** :
- Joueurs connectés → Avertissement affiché avant arrêt
- Arrêt déjà en cours → Bouton désactivé

**Critères d'acceptation** :
-  Sauvegarde automatique du monde avant arrêt
-  Facturation s'arrête à la seconde près
-  Redémarrage possible en < 30 secondes

---

#### **CU-004 : Consultation des logs en temps réel**

**Acteur** : Administrateur du serveur  
**Objectif** : Débugger et surveiller l'activité du serveur

**User Story** :
> *"En tant qu'administrateur, je veux voir les logs de mon serveur en direct pour identifier rapidement les problèmes."*

**Scénario nominal** :
1. L'utilisateur clique sur l'onglet "Console" de son serveur
2. Une WebSocket se connecte au conteneur Docker Minecraft
3. Les logs défilent en temps réel :
   ```
   [12:34:56] [Server thread/INFO]: Starting minecraft server version 1.20.4
   [12:34:58] [Server thread/INFO]: Done (2.1s)! For help, type "help"
   [12:35:12] [User Authenticator #1/INFO]: UUID of player Paul is 7a8b9c0d-...
   [12:35:12] [Server thread/INFO]: Paul joined the game
   ```
4. L'utilisateur peut filtrer par niveau : INFO, WARN, ERROR
5. Bouton "Télécharger les logs" (export en .txt)

**Critères d'acceptation** :
-  Latence WebSocket < 500ms
-  Rétention des logs : 7 jours
-  Pas de fuite de données sensibles dans les logs

---

#### **CU-005 : Suppression du serveur**

**Acteur** : Propriétaire du serveur  
**Objectif** : Supprimer définitivement un serveur non utilisé

**Scénario nominal** :
1. L'utilisateur clique sur "Supprimer" (icône poubelle rouge)
2. Popup de confirmation : "⚠️ ATTENTION : Cette action est irréversible. Toutes les données seront perdues."
3. Il doit taper le nom exact du serveur pour confirmer : `serveur-de-paul`
4. Il clique sur "Supprimer définitivement"
5. Suppression en cascade :
   - Arrêt du conteneur Docker
   - Suppression du volume Azure Files (monde perdu)
   - Suppression de l'entrée BDD
6. Redirection vers le dashboard : "Serveur supprimé avec succès"

**Critères d'acceptation** :
-  Double confirmation obligatoire
-  Impossible de récupérer les données après suppression
- Facturation s'arrête immédiatement

---

### 2.3. Exigences Fonctionnelles Numérotées

#### Module : Authentification & Gestion Utilisateurs

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| **EXI-001** | Le système doit permettre la création de compte via email/mot de passe | Critique | Test : Créer 100 comptes en 10 min |
| **EXI-002** | Les mots de passe doivent être hachés en Scrypt (pas MD5/SHA1) | Critique | Audit : Vérifier la BDD (pas de MDP clair) |
| **EXI-003** | La connexion doit être sécurisée par un jeton CSRF | Haute | Pentest : Tester attaque CSRF |
| **EXI-004** | La session doit expirer après 7 jours d'inactivité | Moyenne | Test : Attendre 7j, session invalidée |
| **EXI-005** | L'utilisateur doit pouvoir réinitialiser son mot de passe par email | Haute | Test : Email reçu en < 2 min |

#### Module : Gestion des Serveurs Minecraft

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| **EXI-006** | Le système doit permettre de créer un serveur en < 60 secondes | Critique | Test de charge : 50 créations simultanées |
| **EXI-007** | L'utilisateur doit pouvoir choisir entre 3 offres : 2GB, 4GB, 8GB RAM | Haute | Test : Vérifier l'allocation mémoire via `docker stats` |
| **EXI-008** | Le nom du serveur doit être unique et alphanumerique (a-z0-9-) | Haute | Test : Tenter de créer 2 serveurs identiques |
| **EXI-009** | L'utilisateur doit pouvoir démarrer/arrêter son serveur à tout moment | Critique | Test : 100 cycles start/stop sans erreur |
| **EXI-010** | L'arrêt du serveur doit déclencher une sauvegarde automatique du monde | Critique | Test : Vérifier fichier level.dat après arrêt |
| **EXI-011** | La suppression d'un serveur doit être irréversible et confirmée 2 fois | Haute | Test : Vérifier popup + champ de confirmation |
| **EXI-012** | L'utilisateur doit pouvoir consulter les logs en temps réel (WebSocket) | Moyenne | Test : Vérifier latence < 500ms |
| **EXI-013** | Le système doit limiter chaque utilisateur à 5 serveurs maximum | Moyenne | Test : Tenter de créer un 6ème serveur |

#### Module : Facturation & Paiement

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| **EXI-014** | La facturation doit être à la seconde d'utilisation réelle | Critique | Test : Vérifier coût serveur 1h = 60 × prix/s |
| **EXI-015** | L'utilisateur doit pouvoir consulter son historique de facturation | Haute | Test : Export CSV des 12 derniers mois |
| **EXI-016** | Le paiement doit être sécurisé via Stripe (PCI-DSS compliant) | Critique | Audit : Vérifier intégration Stripe Elements |
| **EXI-017** | Une facture PDF doit être générée mensuellement | Moyenne | Test : Recevoir facture le 1er du mois |

#### Module : Sécurité & Réseau (VPN Obligatoire)

| ID | Exigence | Priorité | Critère de Validation |
|----|----------|----------|----------------------|
| **EXI-018** | Les serveurs ne doivent être accessibles QUE via VPN | Critique | Test : Tenter connexion directe sans VPN = refusé |
| **EXI-019** | La connexion VPN doit utiliser des certificats X.509 (pas de mot de passe) | Critique | Pentest : Tenter brute-force VPN |
| **EXI-020** | Les conteneurs doivent tourner en utilisateur non-root (UID 1000) | Haute | Test : `docker exec ps aux | grep minecraft` |
| **EXI-021** | Les logs d'accès doivent être anonymisés après 30 jours | Haute | Audit RGPD : Vérifier purge automatique |

---

## 3. CONTRAINTES ET EXIGENCES TECHNIQUES

### 3.1. Contraintes de Sécurité

**Conformité** : ISO 27001 (visé année 2), OWASP Top 10 (2021), CIS Docker Benchmark v1.6.0

| ID | Contrainte | Impact | Solution Technique |
|----|------------|--------|-------------------|
| **SEC-C01** | Aucun secret en dur dans le code source | Critique | Azure Key Vault + Managed Identity |
| **SEC-C02** | Chiffrement AES-256 pour les données au repos | Critique | Azure Storage Service Encryption |
| **SEC-C03** | TLS 1.3 obligatoire pour toutes les communications | Critique | Configuration Nginx + Let's Encrypt |
| **SEC-C04** | Protection contre les injections SQL | Critique | ORM SQLAlchemy (requêtes paramétrées) |
| **SEC-C05** | Rate limiting API : 10 req/s par IP | Haute | Flask-Limiter + Redis |
| **SEC-C06** | Logs d'audit immuables (pas de suppression) | Haute | Azure Log Analytics (append-only) |

### 3.2. Contraintes de Performance

| ID | Contrainte | Seuil | Pénalité si Non-Respect |
|----|------------|-------|------------------------|
| **PERF-C01** | Temps de provisioning d'un serveur | < 60s (P95) | Perte de l'avantage concurrentiel |
| **PERF-C02** | Latence API (GET /servers) | < 200ms (P95) | Mauvaise UX |
| **PERF-C03** | Latence réseau (ping depuis Paris) | < 30ms | Lag in-game |
| **PERF-C04** | Disponibilité de l'API | 99.5% | Pénalités SLA clients |
| **PERF-C05** | Densité conteneurs par VM | 10-15 serveurs/VM | Coûts trop élevés |

### 3.3. Contraintes Réglementaires (RGPD)

| Article RGPD | Contrainte | Implémentation MineHost |
|--------------|-----------|------------------------|
| **Art. 5** (Minimisation) | Collecter uniquement les données nécessaires | Email + Mot de passe (pas de téléphone, adresse) |
| **Art. 6** (Base légale) | Consentement explicite | Checkbox CGU obligatoire à l'inscription |
| **Art. 15** (Droit d'accès) | Export des données sur demande | Endpoint `GET /api/user/data` (JSON) |
| **Art. 17** (Droit à l'oubli) | Suppression des données | Endpoint `DELETE /api/account` (cascade) |
| **Art. 25** (Privacy by Design) | Sécurité dès la conception | Chiffrement natif, minimisation data |
| **Art. 32** (Sécurité) | Mesures techniques appropriées | Chiffrement, pseudonymisation, audits |
| **Art. 33** (Notification violation) | Informer CNIL sous 72h si breach | Procédure documentée + alerte auto |

### 3.4. Matrice de Traçabilité Besoins → Solutions

Cette matrice garantit que chaque besoin exprimé a une solution technique associée (**alignement besoin/contrainte** → **C23.3**).

| Besoin | Solution Technique | Composant | Validation |
|--------|--------------------|-----------|------------|
| **BUS-001** : Sécurité supérieure aux concurrents | Architecture Zero Trust + VPN Cloaking | OpenVPN + NSG Azure | Pentest externe |
| **BUS-002** : Marge 45% minimum | Mutualisation VMs (10-15 conteneurs/VM) | Docker + Orchestration | Suivi FinOps |
| **BUS-003** : Scaler à 1000 serveurs | Ajout automatique de VMs selon charge | Terraform + Autoscaling | Test charge 1000 conteneurs |
| **BUS-004** : Provisioning < 60s | Création conteneur Docker (pas de VM) | Docker API + Images pré-pull | Monitoring P95 |
| **USR-001** : Interface simple | Dashboard Web responsive | Vue.js 3 + Flask API | Tests utilisateurs |
| **USR-002** : Connexion < 2min | VPN auto-configuré + provisioning rapide | OpenVPN + Docker | Chronomètre E2E |
| **USR-003** : Disponibilité 99.5% | Monitoring + Redéploiement auto | Azure Monitor + Scripts | Uptime monitoring |
| **USR-004** : Facturation transparente | Dashboard conso temps réel | Stripe + PostgreSQL | Audit factures |
| **USR-005** : Support < 4h incidents P2 | Ticketing Freshdesk + Discord | Service managé | SLA tracking |
| **TEC-001** : Cloud-Native | VMs Azure + Docker orchestré par API | Azure VMs + Docker Engine | Audit architecture |
| **TEC-002** : Isolation stricte | Conteneurs Docker + NSG réseau | Docker isolation + NSG | Test noisy neighbor |
| **TEC-003** : Backup automatique | Sauvegarde avant arrêt | Hook Docker + Azure Files | Restauration test |
| **TEC-004** : Scalabilité horizontale | Ajout de VMs selon charge | Terraform + Autoscaling | Test 1000 serveurs |
| **TEC-005** : Infrastructure as Code | Terraform | Modules Terraform | CI/CD pipeline |
| **SEC-001** : Protection DDoS | Azure DDoS Protection Standard | Service Azure natif | Simulation attaque |
| **SEC-002** : Chiffrement E2E | TLS 1.3 + AES-256 | Nginx + Azure SSE | Scan SSL Labs |
| **SEC-003** : Cloaking | VPN obligatoire, pas d'accès direct | VNet privé + OpenVPN | Test connexion directe |
| **SEC-004** : Audits trimestriels | Pentests externes | Cabinet sécurité | Rapports audits |
| **SEC-005** : Conformité RGPD | Data residency France Central | Azure région FR | Attestation Azure |

---

# PARTIE 2 : SPÉCIFICATIONS TECHNIQUES

## 4. ARCHITECTURE LOGICIELLE (BACKEND & API)

### 4.1. Stack Technologique (Python/Flask)

**Langage** : Python 3.11  
**Framework Web** : Flask 3.0.0  
**ORM** : SQLAlchemy 2.0 (requêtes paramétrées anti-injection)  
**Base de données** : PostgreSQL 15 (Azure Database for PostgreSQL)  
**Authentification** : Flask-Login + Scrypt (hashing)  
**Rate Limiting** : Flask-Limiter + Redis  
**WebSocket** : Flask-SocketIO (logs temps réel)  
**Orchestration Docker** : Docker SDK for Python (`docker-py`)

### 4.2. Logique d'Orchestration

L'API Flask orchestre les conteneurs Docker sur des VMs Azure pré-provisionnées :

```python
import docker
import uuid
from flask import request, jsonify

docker_clients = {
    "vm-host-01": docker.DockerClient(base_url="tcp://10.0.2.10:2375"),
    "vm-host-02": docker.DockerClient(base_url="tcp://10.0.2.11:2375"),
    "vm-host-03": docker.DockerClient(base_url="tcp://10.0.2.12:2375"),
}

def create_server(user_id, server_name, ram_size):
    """
    Crée un conteneur Docker Minecraft sur une VM disponible
    
    Args:
        user_id (int): ID de l'utilisateur authentifié
        server_name (str): Nom du serveur (validé par regex)
        ram_size (int): RAM en GB (2, 4 ou 8)
    
    Returns:
        dict: Statut de création + métadonnées
    """
    
    if not re.match(r"^[a-z0-9-]{3,20}$", server_name):
        raise SecurityException("Nom de serveur invalide (Risque Injection)")
    
    if get_user_server_count(user_id) >= 5:
        raise QuotaExceededException("Limite de 5 serveurs atteinte")
    
    target_vm = select_least_loaded_vm(docker_clients)
    client = docker_clients[target_vm]
    
    volume_name = f"vol-{user_id}-{uuid.uuid4().hex[:8]}"
    azure_storage.create_file_share(share_name=volume_name, quota=10)
    
    container = client.containers.run(
        image="itzg/minecraft-server:latest",
        name=f"{user_id}-{server_name}",
        detach=True,
        environment={
            "EULA": "TRUE",
            "VERSION": "1.20.4",
            "MAX_MEMORY": f"{ram_size-1}G"  
        },
        volumes={
            volume_name: {"bind": "/data", "mode": "rw"}
        },
        ports={"25565/tcp": None},  
        mem_limit=f"{ram_size}g",
        cpu_quota=200000,  
        restart_policy={"Name": "unless-stopped"},
        network_mode="minecraft-net",  
        user="1000:1000"  
    )
    
    container.reload()
    private_ip = container.attrs['NetworkSettings']['Networks']['minecraft-net']['IPAddress']
    
    db.session.add(Server(
        owner_id=user_id,
        name=server_name,
        vm_host=target_vm,
        container_id=container.id,
        private_ip=private_ip,
        volume_name=volume_name,
        status="running",
        created_at=datetime.utcnow()
    ))
    db.session.commit()
    
    return {
        "status": "running",
        "private_ip": f"{private_ip}:25565",
        "vpn_config_url": f"/api/vpn/config/{user_id}",
        "instructions": "Installez OpenVPN, importez le fichier .ovpn, puis connectez-vous pour accéder à votre serveur"
    }
```

**Logique de sélection VM** :
```python
def select_least_loaded_vm(docker_clients):
    """Sélectionne la VM avec le moins de conteneurs actifs"""
    loads = {}
    for vm_name, client in docker_clients.items():
        loads[vm_name] = len(client.containers.list())
    return min(loads, key=loads.get)  # VM avec le moins de conteneurs
```

### 4.3. Sécurisation du Code (AppSec)

- **Input Validation** : Regex strict `^[a-z0-9-]{3,20}$` sur tous les champs utilisateurs
- **CSRF Protection** : Jetons anti-CSRF sur toutes les actions sensibles (POST/PUT/DELETE)
- **Command Injection** : Utilisation du Docker SDK Python (pas d'appels `os.system()`)
- **BOLA/IDOR** : Vérification systématique `if server.owner_id != current_user.id: abort(403)`
- **Rate Limiting** : 10 req/s par IP, 5 tentatives de login max/min
- **Logging Sécurisé** : Pas de secrets loggés

---

## 5. INFRASTRUCTURE CLOUD (AZURE)

### 5.1. Choix du Compute : VMs Azure + Docker

**Architecture** :
- **VMs pré-provisionnées** : 3 VMs Ubuntu 24.04 LTS (taille Standard_D4s_v3 : 4 vCPU, 4GB RAM)
- **Docker Engine** installé sur chaque VM avec API Docker exposée sur le VNet privé
- **Mutualisation** : Chaque VM héberge 10-15 conteneurs Minecraft (isolation Docker)

**Avantages de cette approche** :
-  **Coût optimisé** : VMs 24/7 mutualisées vs provisioning à la demande
-  **Provisioning ultra-rapide** : Création conteneur = 5-10s (image déjà pullée sur VM)
-  **Isolation Docker** : Namespaces Linux (PID, NET, MNT, IPC) + cgroups (CPU/RAM)
-  **Scalabilité** : Ajout de VMs selon la charge (Terraform + Autoscaling)

**Configuration VM type** :
```yaml
VM Specification:
  Size: Standard_D4s_v3
  vCPU: 4
  RAM: 4GB
  OS: Ubuntu 24.04 LTS
  Disk: Premium SSD 128GB (OS) + Azure Files (data)
  Network: VNet privé (10.0.2.0/24)
  Docker: Engine 24.0 + Docker Compose 2.20
  Capacité: 10-15 conteneurs Minecraft simultanés
```

**Calcul de Densité** :
- Serveur Minecraft 2GB RAM → ~12 serveurs par VM (4GB / 1.3 = 12 avec overhead OS)
- Serveur Minecraft 4GB RAM → ~3 serveurs par VM
- Mix réaliste : 70% 2GB + 30% 4GB → ~10 serveurs/VM en moyenne

**Isolation Multi-Niveaux** :
1. **Isolation Processus** : Chaque conteneur a son propre namespace PID
2. **Isolation Réseau** : Network namespace Docker (chaque conteneur a son IP privée)
3. **Isolation Stockage** : Volumes Azure Files montés individuellement
4. **Isolation Ressources** : Limites cgroups strictes (CPU quota, mem_limit)

**Exemple Commande Docker** :
```bash
docker run -d \
  --name user123-serveur01 \
  --memory="2g" \
  --cpus="2.0" \
  --user=1000:1000 \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --security-opt=no-new-privileges \
  --network=minecraft-net \
  -v vol-user123-abc123:/data:rw \
  -e EULA=TRUE \
  -e VERSION=1.20.4 \
  itzg/minecraft-server:latest
```

### 5.2. Stratégie de Stockage : Azure Files (Persistance)

- **Type** : Premium Files (SSD) pour performances
- **Redondance** : ZRS (Zone-Redundant Storage) → 3 copies sur 3 zones
- **Quotas** : 10GB par serveur par défaut (évolutif jusqu'à 100TB)
- **Protocole** : SMB 3.0 chiffré
- **Montage** : Volumes Docker montant les File Shares Azure
- **Snapshots** : Quotidiens (rétention 7 jours) via Azure Backup

**Workflow de Persistance** :
1. Création du serveur → API crée un File Share unique (`vol-user123-abc123`)
2. File Share monté dans le conteneur Docker : `/data`
3. Minecraft sauvegarde les mondes dans `/data/world`
4. Arrêt conteneur → Données restent sur Azure Files (indépendant du cycle de vie)
5. Redémarrage → Même File Share remonté = données intactes

### 5.3. Réseau et Isolation : VNet & NSG

**Architecture Réseau** :

```
Internet
    ↓
[Azure VPN Gateway] ← Clients se connectent ici avec certificats X.509
    ↓
[VNet: 10.0.0.0/16 - "minehost-vnet"]
    ├── Subnet VPN: 10.0.1.0/24 (OpenVPN Server)
    │   └── NSG: Allow inbound 1194/UDP (OpenVPN)
    │
    ├── Subnet VMs: 10.0.2.0/24 (VMs Docker)
    │   ├── vm-host-01: 10.0.2.10
    │   ├── vm-host-02: 10.0.2.11
    │   └── vm-host-03: 10.0.2.12
    │   └── NSG: Allow inbound 25565/TCP ONLY from Subnet VPN
    │
    ├── Subnet Data: 10.0.3.0/24 (PostgreSQL + Azure Files)
    │   └── NSG: Allow inbound 5432/TCP + 445/TCP ONLY from Subnet VMs
    │
    └── Subnet Admin: 10.0.4.0/24 (Azure Bastion pour accès SSH admin)
        └── NSG: Allow inbound 22/TCP ONLY from Azure Bastion
```

**Règles NSG Critiques** :

| NSG | Règle | Source | Destination | Port | Action | Justification |
|-----|-------|--------|-------------|------|--------|---------------|
| **NSG-VMs** | Allow-Minecraft-VPN | 10.0.1.0/24 (VPN) | 10.0.2.0/24 (VMs) | 25565/TCP | Allow | Clients VPN accèdent aux serveurs |
| **NSG-VMs** | Deny-Internet-Inbound | Internet | 10.0.2.0/24 (VMs) | * | **Deny** | ❌ Aucun accès direct depuis Internet |
| **NSG-Data** | Allow-VMs-to-PostgreSQL | 10.0.2.0/24 (VMs) | 10.0.3.0/24 (Data) | 5432/TCP | Allow | API accède à la BDD |
| **NSG-Data** | Allow-VMs-to-AzureFiles | 10.0.2.0/24 (VMs) | 10.0.3.0/24 (Data) | 445/TCP | Allow | Docker monte les volumes SMB |
| **NSG-Admin** | Allow-Bastion-SSH | AzureBastion | 10.0.2.0/24 (VMs) | 22/TCP | Allow | Admin SSH sécurisé |

**Cloaking VPN** :
- **Principe** : Les VMs n'ont **AUCUNE IP publique**
- **Conséquence** : Invisible sur Shodan, Censys, scans de ports automatisés
- **Accès** : Uniquement via VPN OpenVPN (certificats clients uniques par utilisateur)
- **Bénéfice** : Suppression de 99% des attaques opportunistes

---

## 6. STRATÉGIE DE SÉCURITÉ (DEFENSE IN DEPTH)

### 6.1. Approche "Zero Trust" & Cloaking VPN

**Principe** : Ne faire confiance à aucun réseau, même interne. Vérifier chaque connexion.

**Implémentation VPN Obligatoire** :

1. **OpenVPN Server** : Déployé sur une VM dédiée dans le subnet VPN (10.0.1.0/24)
2. **Authentification** : Certificats X.509 uniques par utilisateur (pas de mot de passe)
3. **Génération certificats** : 
   ```bash
   easyrsa build-client-full user123 nopass
   ```
4. **Révocation** : Si compromission, révocation du certificat via CRL (Certificate Revocation List)
5. **Logging** : Toutes les connexions VPN loggées (IP source, timestamp, user, durée)

**Workflow Utilisateur** :
1. Commande d'un serveur → API génère certificat client
2. Téléchargement fichier `.ovpn` depuis le dashboard
3. Import dans OpenVPN Connect (Windows/Mac/Linux/Android/iOS)
4. Connexion VPN → Attribution IP privée (ex: 10.0.1.50)
5. Accès au serveur Minecraft via IP privée (ex: `10.0.2.25:25565`)

**Bénéfice** :
-  Pas d'attaques DDoS Layer 3/4 impossible (pas d'IP publique cible)
-  Pas de scans de ports automatisés inefficaces
-  Audit trail complet (qui s'est connecté et quand)

### 6.2. Durcissement des Conteneurs (Docker Hardening)

Conformément au **CIS Docker Benchmark v1.6.0** :

| Règle CIS | Implémentation MineHost | Commande Docker |
|-----------|------------------------|-----------------|
| **4.1** - User non-root | UID 1000 (utilisateur `minecraft`) | `--user=1000:1000` |
| **5.1** - Capabilities drop | Révocation de toutes sauf NET_BIND_SERVICE | `--cap-drop=ALL --cap-add=NET_BIND_SERVICE` |
| **5.3** - Read-only rootfs | Système fichiers racine en RO (sauf /data, /tmp) | `--read-only --tmpfs /tmp:rw,noexec` |
| **5.12** - No new privileges | Flag empêchant escalade via setuid | `--security-opt=no-new-privileges` |
| **5.25** - Image minimale | Alpine Linux (5MB vs 200MB Ubuntu) | `FROM alpine:3.19` dans Dockerfile |
| **5.28** - PID limit | Limiter nombre de processus fork | `--pids-limit=100` |

**Scan de Vulnérabilités** :
```bash
trivy image --severity HIGH,CRITICAL itzg/minecraft-server:latest

```

### 6.3. Gestion des Secrets et Identités

- **Azure Key Vault** : Coffre-fort pour secrets (mots de passe BDD, clés API, certificats VPN)
- **Managed Identity** : VMs Azure authentifiées automatiquement (pas de clé API stockée)
- **Pas de secrets en dur** : Variables d'environnement injectées au démarrage

**Exemple Récupération Secret** :
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://minehost-vault.vault.azure.net/", credential=credential)

db_password = client.get_secret("postgresql-password").value
```

---

## 7. MODÈLE ÉCONOMIQUE & FINOPS

### 7.1. Mutualisation des Ressources VM

**Stratégie de Mutualisation** :

Au lieu de déployer une VM par serveur (coût prohibitif), nous mutualisons :
- **3 VMs Azure** (Standard_D4s_v3 : 4 vCPU, 4GB RAM) → ~30 serveurs Minecraft au total
- **Coût VM** : 0.196€/h × 3 VMs × 730h/mois = **429€/mois** (VMs 24/7)
- **Coût par serveur** : 429€ / 30 serveurs = **14.3€/serveur/mois** (si tous actifs 24/7)

**Optimisation via Auto-Shutdown** :
- Réalité : Les serveurs ne sont PAS utilisés 24/7
- Taux d'utilisation moyen observé : **4h/jour** (17% du temps)
- Coût réel par serveur : 14.3€ × 17% = **2.4€/serveur/mois** (avec auto-shutdown)

**Comparaison avec Alternatives** :

| Architecture | Coût / Serveur Actif 24/7 | Coût / Serveur 4h/jour | Scalabilité |
|--------------|---------------------------|------------------------|-------------|
| **VMs Dédiées** (1 VM par serveur) | 143€/mois | 23.8€/mois | Faible |
| **VMs Mutualisées** (notre choix) | 14.3€/mois | **2.4€/mois** ✅ | Moyenne |
| **ACI Serverless** | 8.6€/mois | 1.4€/mois | Élevée |

**Scalabilité Horizontale** :
- Si charge > 80% sur les 3 VMs → Terraform ajoute automatiquement une 4ème VM
- Ajout VM = +10-15 serveurs de capacité en ~5 minutes

### 7.2. Algorithme d'Auto-Shutdown

**Watchdog RCON** (exécuté toutes les 5 minutes via cron sur l'API Flask) :

```python
import mcrcon  # Bibliothèque RCON Python

def auto_shutdown_check(server_id):
    """Vérifie si un serveur est inactif et l'arrête si nécessaire"""
    
    server = db.session.get(Server, server_id)
    
    try:
        with mcrcon.MCRcon(server.private_ip, "rcon_password") as mcr:
            response = mcr.command("list")  
            
        player_count = int(response.split()[2])
        
        if player_count == 0:
            server.idle_minutes += 5
            db.session.commit()
            
            if server.idle_minutes >= 15: 
                docker_client = docker.DockerClient(base_url=f"tcp://{server.vm_host}:2375")
                container = docker_client.containers.get(server.container_id)
                
                container.exec_run("rcon-cli save-all")
                
                container.stop(timeout=30)
                
                server.status = "stopped"
                server.stopped_at = datetime.utcnow()
                db.session.commit()
                
                
        else:
            server.idle_minutes = 0
            db.session.commit()
            
    except Exception as e:
        logger.error(f"RCON error for server {server_id}: {e}")
```

**Résultat** : Économie de ~83% sur les coûts compute (4h/24h = 17% du temps facturé)

---

## 8. JUSTIFICATION DES CHOIX TECHNIQUES

### 8.1. Alternatives Évaluées

#### **Choix 1 : Architecture Compute**

| Solution | Avantages | Inconvénients | Score /10 |
|----------|-----------|---------------|-----------|
| **VMs Azure + Docker** ✅ | Mutualisation, provisioning rapide (5-10s), maîtrise totale | VMs 24/7 (coût fixe), gestion infra | **8/10** |
| Azure Container Instances (ACI) | Serverless, pas d'infra à gérer, coût à la seconde | Cold start 30-45s, pas de mutualisation, coût unitaire élevé | 7/10 |
| Kubernetes (AKS) | Scalabilité ultime, écosystème riche | Complexité, overhead, coût cluster permanent | 6/10 |
| VMs dédiées (1 VM = 1 serveur) | Isolation maximale | Coût prohibitif (143€/serveur/mois), gaspillage ressources | 3/10 |

**Décision** : **VMs Azure + Docker** pour le meilleur ratio coût/performance/simplicité.

**Justification détaillée** :
-  **Provisioning ultra-rapide** : Docker crée un conteneur en 5-10s (image déjà sur la VM) vs 30-45s pour ACI
-  **Coût optimisé** : Mutualisation 10-15 serveurs/VM vs ACI qui facture chaque conteneur individuellement
-  **Simplicité opérationnelle** : Pas de cluster K8s à maintenir (vs AKS qui nécessite des SREs dédiés)
- ⚠️ **Compromis** : VMs 24/7 (coût fixe) mais largement compensé par la mutualisation

---

#### **Choix 2 : Sécurité Réseau**

| Solution | Avantages | Inconvénients | Score /10 |
|----------|-----------|---------------|-----------|
| **VPN Obligatoire (OpenVPN)** ✅ | Cloaking complet, audit trail, authentification forte | Friction utilisateur (install VPN) | **9/10** |
| IPs Publiques + WAF + DDoS Protection | Simple pour utilisateurs | Exposition aux attaques, coût DDoS élevé | 6/10 |
| Azure Private Link + ExpressRoute | Sécurité maximale | Coût prohibitif (500€/mois), complexité | 5/10 |

**Décision** : **VPN Obligatoire** pour la sécurité maximale (acceptation de la friction utilisateur).

**Justification détaillée** :
-  **Sécurité supérieure** : Aucune IP publique = 0 scan, 0 DDoS opportuniste
-  **Différenciation marché** : Aucun concurrent n'offre ce niveau de sécurité
-  **Audit** : Logs VPN permettent de tracer qui se connecte et quand
- ⚠️ **Friction** : Utilisateurs doivent installer OpenVPN (compensé par tutoriels vidéo)

---

#### **Choix 3 : Base de données**

| BDD | Avantages | Inconvénients | Score /10 |
|-----|-----------|---------------|-----------|
| **PostgreSQL (Azure Database)** ✅ | ACID, relationnel, Private Link | Moins scalable qu'un NoSQL | **8/10** |
| MySQL | Populaire, bien documenté | Moins de features avancées (JSONB) | 7/10 |
| MongoDB | Flexible, scalable | Pas ACID, overkill pour notre use case | 6/10 |

**Décision** : **PostgreSQL** pour la fiabilité ACID et les fonctionnalités avancées.

---

### 8.2. Matrice de Décision Multi-Critères

Méthodologie : Pondération des critères selon l'importance business.

| Critère | Poids | VMs + Docker | ACI Serverless | K8s (AKS) |
|---------|-------|-------------|----------------|-----------|
| **Sécurité** (Isolation) | 30% | 8/10 (Docker namespaces) | 9/10 (Hyperviseur) | 6/10 (Noyau partagé) |
| **Coûts** (FinOps) | 25% | **9/10** (Mutualisation) | 6/10 (Coût unitaire élevé) | 5/10 (Cluster permanent) |
| **Simplicité** (Ops) | 20% | **9/10** (Docker standard) | 9/10 (Serverless) | 4/10 (K8s complexe) |
| **Performance** (Provisioning) | 15% | **9/10** (5-10s) | 7/10 (30-45s cold start) | 8/10 (Rapide) |
| **Scalabilité** | 10% | 7/10 (Ajout VMs manuel) | 9/10 (Auto-scale natif) | 10/10 (K8s best-in-class) |
| **TOTAL PONDÉRÉ** | - | **8.45/10**  | 7.75/10 | 5.8/10 |

**Conclusion** : VMs + Docker obtient le meilleur score grâce à l'optimisation des coûts (mutualisation) et la simplicité opérationnelle.

---

### 8.3. Justification des Technologies Retenues

#### **Python + Flask**
- **Pour** : SDK Azure natifs, Docker SDK Python excellent, développement rapide
- **Contre** : Performances inférieures à Go/Rust (mais non critique pour orchestration)
- **Verdict** : Ratio productivité/performance optimal

#### **Docker**
- **Pour** : Isolation processus/réseau/stockage, portabilité, écosystème mature
- **Contre** : Moins sécurisé que des VMs dédiées (mais amplement suffisant avec hardening)
- **Verdict** : Standard industrie pour conteneurisation

#### **OpenVPN**
- **Pour** : Standard industrie, certificats X.509, open-source audité, multi-plateforme
- **Contre** : Moins moderne que WireGuard (mais plus mature)
- **Verdict** : Fiabilité éprouvée pour un usage enterprise

#### **Terraform**
- **Pour** : Infrastructure as Code standard, multi-cloud, state management
- **Contre** : Courbe d'apprentissage initiale
- **Verdict** : Indispensable pour reproductibilité et disaster recovery

#### **Vue.js 3 (Frontend)**
- **Pour** : Réactivité, Composition API moderne, bundle size réduit
- **Contre** : Moins populaire que React (mais plus simple)
- **Verdict** : Excellent pour des dashboards interactifs avec WebSocket

---

## 9. ANALYSE DES RISQUES ET OPPORTUNITÉS

### 9.1. Matrice des Risques

| ID | Risque | Probabilité | Impact | Criticité | Mitigation | Responsable |
|----|--------|-------------|--------|-----------|------------|-------------|
| **RIS-001** | Saturation VM (>15 conteneurs/VM) | Moyenne | Moyen | **6** | Monitoring charge + Ajout auto de VMs (Terraform) | SRE Lead |
| **RIS-002** | Attaque DDoS sur VPN Gateway | Élevée | Élevé | **9** | Azure DDoS Protection Standard + Rate limiting VPN | RSSI |
| **RIS-003** | Fuite de données clients (breach RGPD) | Faible | Critique | **6** | Chiffrement E2E + Key Vault + Audits trimestriels | RSSI |
| **RIS-004** | Container Escape (vulnérabilité Docker) | Faible | Élevé | **5** | Hardening CIS + Scan Trivy + User non-root | DevSecOps |
| **RIS-005** | Panne région Azure France Central | Faible | Élevé | **5** | Plan Disaster Recovery multi-régions (voir 15.3) | SRE Lead |
| **RIS-006** | Friction utilisateur (install VPN complexe) | Moyenne | Moyen | **5** | Tutoriels vidéo + Support réactif + Client VPN simplifié | Product Owner |
| **RIS-007** | Coût VM fixe 24/7 (si peu de clients) | Moyenne | Moyen | **5** | Auto-shutdown conteneurs + Monitoring FinOps | FinOps |
| **RIS-008** | Vulnérabilité Mod Minecraft (code malveillant) | Moyenne | Élevé | **7** | Scan antivirus Azure Defender + Isolation conteneurs | DevSecOps |

**Légende Criticité** : Probabilité (1-5) × Impact (1-5) = Score /25

---

### 9.2. Opportunités Stratégiques et Business

#### **OPP-001 : Extension à d'autres jeux**
- **Description** : Appliquer l'architecture VMs + Docker à d'autres jeux (Rust, ARK, Valheim, Terraria)
- **Impact Business** : Multiplication du TAM (Total Addressable Market) par 3-5x
- **Faisabilité** : Élevée (architecture générique, changement d'image Docker uniquement)
- **Investissement** : Faible (2-3 semaines de dev par jeu)
- **Roadmap** : Année 2 (après consolidation Minecraft)
- **ROI Estimé** : +150% de CA en année 2

#### **OPP-002 : Partenariat avec streamers Twitch/YouTube**
- **Description** : Offrir serveurs gratuits aux streamers (>1000 viewers) en échange de visibilité (mention en live)
- **Impact Business** : Acquisition client à coût quasi-nul (vs 50€ CAC en publicité)
- **Faisabilité** : Moyenne (négociations nécessaires)
- **Investissement** : Coût infra négligeable (~20€/mois pour 10 streamers)
- **Roadmap** : Semaine 12 (après lancement)
- **ROI Estimé** : 1 streamer = 20-50 conversions clients

#### **OPP-003 : API publique pour développeurs**
- **Description** : Ouvrir une API REST permettant de créer/gérer serveurs programmatiquement
- **Impact Business** : Attirer les communautés techniques (modders, développeurs de plugins)
- **Faisabilité** : Élevée (architecture API déjà prête)
- **Investissement** : 1 semaine (documentation OpenAPI + rate limiting API)
- **Roadmap** : Trimestre 2
- **ROI Estimé** : +10% de clients "power users"

#### **OPP-004 : Certification ISO 27001**
- **Description** : Obtenir la certification sécurité ISO 27001 pour rassurer les clients entreprise
- **Impact Business** : Accès au marché B2B (écoles, entreprises organisant des événements gaming)
- **Faisabilité** : Moyenne (audit 6-12 mois)
- **Investissement** : 15,000€ (cabinet d'audit)
- **Roadmap** : Année 2
- **ROI Estimé** : Marché B2B = 30% de CA supplémentaire

#### **OPP-005 : Modèle Freemium**
- **Description** : Offre gratuite limitée (1 serveur, 1GB RAM, 10h/mois) pour acquisition virale
- **Impact Business** : Taux de conversion freemium → premium de 2-5% (standard SaaS)
- **Faisabilité** : Élevée (limitation quota déjà implémentée)
- **Investissement** : Coût infra gérable (10-20€/mois pour 100 users freemium)
- **Roadmap** : Trimestre 3 (après stabilisation facturation)
- **ROI Estimé** : Acquisition virale = -60% de CAC

---

## 10. INDICATEURS DE PERFORMANCE (KPIs)

### 10.1. Performance Technique

| KPI | Cible | Méthode de Mesure | Fréquence |
|-----|-------|-------------------|-----------|
| **Temps de provisioning** | < 45s (P95) | Azure Monitor + custom metric (temps création conteneur Docker) | Temps réel |
| **Latence API** (GET /servers) | < 200ms (P95) | Application Insights | Temps réel |
| **Latence réseau** (ping) | < 30ms (Europe Ouest) | PingPlotter depuis 5 sites via VPN | Horaire |
| **Disponibilité API** | 99.5% | Uptime Robot + StatusPage | Temps réel |
| **Densité conteneurs/VM** | 10-15 serveurs/VM | `docker ps | wc -l` sur chaque VM | Quotidien |

### 10.2. Sécurité

| KPI | Cible | Méthode de Mesure | Fréquence |
|-----|-------|-------------------|-----------|
| **Incidents de fuite de données** | 0 | Azure Sentinel alerts | Temps réel |
| **Temps détection intrusion** | < 5 min | SIEM (Azure Sentinel) | Temps réel |
| **Couverture tests sécurité** | 100% endpoints critiques | CI/CD (SAST + DAST) | À chaque commit |
| **Délai de patch CVE critique** | < 24h | Dependabot + SLA interne | Post-découverte |
| **Taux de connexion VPN réussies** | > 95% | Logs OpenVPN | Quotidien |

### 10.3. FinOps

| KPI | Cible | Méthode de Mesure | Fréquence |
|-----|-------|-------------------|-----------|
| **Coût moyen par serveur actif** | < 3€/mois (avec auto-shutdown) | Azure Cost Management | Quotidien |
| **Taux d'utilisation VMs** | > 70% (conteneurs actifs / capacité totale) | Custom query Docker | Quotidien |
| **Marge brute** | > 48% | (CA - OPEX) / CA | Mensuel |
| **Efficacité auto-shutdown** | > 80% des serveurs arrêtés après 15 min | Logs watchdog RCON | Hebdomadaire |

---

## 11. PLANNING ET ROADMAP

### Phases Détaillées

| Phase | Durée | Sprint | Livrables Techniques | Responsable | Critères de Succès | Jalon |
|-------|-------|--------|---------------------|-------------|-------------------|-------|
| **Phase 1 : MVP** | Semaines 1-4 | Sprint 1-2 | - API Flask CRUD serveurs<br>- Docker orchestration sur VMs<br>- PostgreSQL setup<br>- Auth Scrypt<br>- Dashboard Vue.js | Lead Dev | ✅ Créer 1 serveur en < 60s<br> Auth fonctionnelle<br> CRUD complet | **J+28** : Demo interne |
| **Phase 2 : Hardening** | Semaines 5-6 | Sprint 3 | - **VPN Gateway OpenVPN**<br>- **Génération certificats clients**<br>- Azure Key Vault intégration<br>- Input validation (regex)<br>- Rate Limiting (Flask-Limiter)<br>- HTTPS (Let's Encrypt) | DevSecOps |  0 vulnérabilité critique (ZAP)<br> VPN fonctionnel<br> Secrets externalisés | **J+42** : Audit sécurité intermédiaire |
| **Phase 3 : FinOps** | Semaines 7-8 | Sprint 4 | - **Auto-Shutdown RCON Watchdog**<br>- Monitoring charge VMs<br>- Autoscaling Terraform<br>- Facturation Stripe<br>- Dashboard conso | SRE |  Auto-shutdown testé<br> Monitoring charge VMs<br> Facturation précise | **J+56** : Beta privée (50 users) |
| **Phase 4 : Production** | Semaine 9 | Sprint 5 | - Tests de charge (Locust 1000 users)<br>- Pentest externe<br>- Disaster Recovery test<br>- Documentation complète<br>- Formation support | QA + PenTester |  1000 req/s soutenus<br> 0 CVE critique<br> Pentest passé<br> DR < 15min | **J+63** :  **GO LIVE** |

### Diagramme de Gantt Simplifié

```
Semaine:  1  2  3  4  5  6  7  8  9
Phase 1:  [----------------]
Phase 2:                [----------] ← VPN implémenté ici
Phase 3:                      [----------] ← Auto-shutdown ici
Phase 4:                            [----]
Tests:                              [----]
```

---

## 12. CONFORMITÉ RGPD ET LÉGALE

### 12.1. Protection des Données (Privacy by Design)

**Principes appliqués (Art. 25 RGPD)** :

| Principe | Implémentation MineHost |
|----------|------------------------|
| **Minimisation** | Collecte uniquement Email + Mot de passe (pas de téléphone, adresse postale, date de naissance) |
| **Limitation de finalité** | Données utilisées uniquement pour le service (pas de revente, pas de publicité ciblée) |
| **Exactitude** | Utilisateur peut modifier son email via profil |
| **Limitation de conservation** | Logs purgés après 30j, comptes inactifs >2 ans supprimés |
| **Intégrité/Confidentialité** | Chiffrement AES-256 (repos) + TLS 1.3 (transit) |
| **Responsabilité** | Registre des traitements tenu, DPO nommé |

**Data Residency** : Toutes les données sont hébergées en **France Central** (datacenter Azure Paris).

### 12.2. Droits Utilisateurs (Art. 15-22 RGPD)

| Droit | Endpoint API | Délai de Traitement |
|-------|-------------|---------------------|
| **Droit d'accès** (Art. 15) | `GET /api/user/data` (export JSON) | Immédiat |
| **Droit de rectification** (Art. 16) | `PUT /api/user/profile` | Immédiat |
| **Droit à l'oubli** (Art. 17) | `DELETE /api/account` (soft delete 7j puis hard) | 7 jours |
| **Droit à la portabilité** (Art. 20) | `GET /api/user/export` (JSON + ZIP mondes) | < 24h |
| **Droit d'opposition** (Art. 21) | Opt-out emails marketing (checkbox profil) | Immédiat |

**Contact DPO** : dpo@minehost.com (réponse sous 48h ouvrées)

---

## 13. BUDGET ET ROI PRÉVISIONNEL

### 13.1. Coûts d'Infrastructure (OPEX Mensuel)

**Hypothèses** : 100 serveurs actifs, 4h/jour d'utilisation moyenne, 3 VMs Azure

| Composant | Calcul Détaillé | Coût Mensuel |
|-----------|-----------------|--------------|
| **Compute (VMs 24/7)** | 3 VMs Standard_D4s_v3 (4 vCPU, 4GB) × 0.196€/h × 730h | **429 €** |
| **Stockage (Azure Files Premium)** | 200 GB (40 serveurs × 5GB moyens) × 0.225€/GB | **45 €** |
| **Base de Données (PostgreSQL)** | Instance Burstable B2s (2 vCPU, 4GB RAM) | **30 €** |
| **Réseau VPN** | VPN Gateway Basic (P2S + S2S) : 30€<br>Bande passante sortante (500GB @ 0.08€/GB) : 40€ | **70 €** |
| **Sécurité** | Azure Key Vault (10000 ops/mois) : 10€<br>DDoS Protection Standard : 40€ | **50 €** |
| **TOTAL INFRASTRUCTURE** | | **624 €/mois** |

**MAIS avec Auto-Shutdown (serveurs actifs 4h/24h = 17% du temps)** :
- Coût compute effectif : 429€ (VMs fixes) + stockage/BDD/réseau inchangés
- Densité : 100 serveurs sur 3 VMs (mutualisation)
- **Coût réel estimé** : **520€/mois** (tenant compte de l'optimisation)

**Coût par serveur actif** : 520€ / 100 = **5.2€/mois/serveur**

### 13.2. Rentabilité (ROI)

**Modèle Tarifaire** :

| Offre | RAM | Prix Public | Coût Infra Estimé | Marge |
|-------|-----|-------------|-------------------|-------|
| **Starter** | 2GB | 9.99€/mois | 4.00€/mois | 60% |
| **Pro** | 4GB | 14.99€/mois | 6.50€/mois | 57% |
| **Ultimate** | 8GB | 24.99€/mois | 11.00€/mois | 56% |

**Projection Financière (Scénario Base : 100 clients Starter)** :

| Métrique | Valeur |
|----------|--------|
| **Chiffre d'Affaires** | 100 × 9.99€ = **999 €/mois** |
| **Coûts Fixes (Infra)** | **520 €/mois** |
| **Marge Brute** | 999€ - 520€ = **479 €/mois (48%)** |
| **Break-Even** | 520€ / 9.99€ = **53 clients** |

**Projection Année 1 (Scénario Optimiste : 500 clients, mix offres)** :

| Mois | Clients | CA Mensuel | Coûts Infra | Marge |
|------|---------|-----------|-------------|-------|
| **M1-3** (MVP) | 50 | 500€ | 520€ | -20€ (investissement) |
| **M4-6** (Beta) | 150 | 1,650€ | 780€ | 870€ (53%) |
| **M7-9** (Launch) | 300 | 3,600€ | 1,100€ | 2,500€ (69%) |
| **M10-12** (Growth) | 500 | 6,500€ | 1,500€ | 5,000€ (77%) |
| **TOTAL ANNÉE 1** | - | **78,000€** | **22,000€** | **56,000€ (72%)** |

**ROI Investissement Initial** (Développement + Infrastructure) :
- Investissement : 30,000€ (6 mois de dev @ 5000€/mois)
- CA Année 1 : 78,000€
- ROI : (78,000 - 30,000 - 22,000) / 30,000 = **87%** (quasi-doublement de l'investissement)

---

## 14. STRATÉGIE DE VALIDATION (QA)

### 14.1. Tests de Sécurité (Pentest)

#### SAST (Static Application Security Testing)
- **Outil** : Bandit (Python), SonarQube
- **Fréquence** : À chaque commit (CI/CD)
- **Critères de blocage** : 
  -  CVE critique (CVSS > 9.0)
  -  Secrets hard-codés
  -  Injection SQL (requêtes non-paramétrées)
  -  Command Injection (os.system, subprocess sans validation)

#### DAST (Dynamic Application Security Testing)
- **Outil** : OWASP ZAP
- **Scénarios** :
  1. Test injection SQL sur tous les endpoints
  2. Test XSS (Cross-Site Scripting) sur formulaires
  3. Test CSRF (absence de jetons anti-CSRF)
  4. Test BOLA/IDOR (accès non autorisé aux serveurs d'autres users)
- **Fréquence** : Hebdomadaire (environnement staging)

#### Scan Conteneurs
- **Outil** : Trivy
- **Cible** : Image `itzg/minecraft-server`
- **Critère** : 0 CVE critique (> 9.0 CVSS)
- **Fréquence** : Quotidienne (rebuild si CVE détectée)
- **Commande** :
  ```bash
  trivy image --severity HIGH,CRITICAL itzg/minecraft-server:latest
  ```

#### Pentest Externe
- **Cabinet** : À sélectionner (budget : 5000€)
- **Scope** : API, VPN, Infrastructure réseau, Conteneurs Docker
- **Durée** : 5 jours
- **Livrables** : Rapport détaillé + PoC exploits + Plan de remédiation
- **Planification** : Semaine 9 (avant Go-Live)

### 14.2. Tests de Charge

**Outil** : Locust (Python-based load testing)

#### Test 1 : Création Massive
```python
from locust import HttpUser, task, between
import random, string

class MinehostUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def create_server(self):
        name = ''.join(random.choices(string.ascii_lowercase, k=10))
        self.client.post("/api/servers", json={
            "name": f"server-{name}",
            "ram": random.choice([2, 4, 8])
        })

```

**Objectifs** :
-  1000 req/s soutenus
-  Taux d'erreur < 1%
-  Latence P95 < 500ms
-  Aucune exception non catchée
-  Charge VMs < 80% CPU

#### Test 2 : Stress Test
- Montée en charge progressive : 0 → 2000 users en 10 min
- Objectif : Identifier le point de rupture (CPU/RAM/DB connections/Docker daemon)

#### Test 3 : Endurance (Soak Test)
- 1000 utilisateurs pendant 1 heure
- Objectif : Détecter fuites mémoire, connexions non fermées, saturation disque

### 14.3. Tests de Résilience (Chaos Engineering)

**Outil** : Scripts Bash custom + Azure CLI

#### Scénario 1 : Kill Aléatoire de Conteneurs
```bash
ssh vm-host-01 "docker ps -q | shuf -n 3 | xargs -I {} docker kill {}"
```
**Validation** :
-  Redémarrage auto < 30s (restart policy unless-stopped)
-  Aucune perte de données (Azure Files)
-  Notification utilisateur via email

#### Scénario 2 : Saturation CPU d'une VM
```bash
ssh vm-host-01 "stress-ng --cpu 4 --timeout 300s"
```
**Validation** :
-  Les autres VMs continuent de fonctionner normalement
-  Nouveaux serveurs créés sur VMs moins chargées
-  Alert monitoring déclenchée

#### Scénario 3 : Perte Connexion Azure Files
```bash
ssh vm-host-01 "umount /mnt/azurefiles && sleep 60 && mount /mnt/azurefiles"
```
**Validation** :
-  Conteneurs passent en "unhealthy" mais ne crashent pas
-  Reconnexion automatique après restauration
-  Aucune corruption de données (SMB robuste)

#### Scénario 4 : Panne Région Azure France Central
**Simulation** : Arrêt manuel de toutes les VMs + BDD
**Validation** : Plan Disaster Recovery (voir section 15.3)
-  Bascule sur North Europe en < 15 min
-  Données restaurées depuis backup
-  Service rétabli

**Fréquence** : Tests Chaos trimestriels en pré-production

---

## 15. MAINTENANCE ET SUPPORT

### 15.1. Stratégie de Mise à Jour

#### Image Docker Minecraft
- **Scan hebdomadaire** : Trivy détecte les CVEs dans `itzg/minecraft-server`
- **Rebuild automatique** : Si CVE critique (CVSS > 9.0), rebuild + rolling update conteneurs
- **Rolling Update** : Redémarrage des conteneurs par VM (max 33% simultanés pour éviter indisponibilité)
- **Notification** : Email aux utilisateurs 24h avant maintenance (si impact)

#### Dépendances Python
- **Dependabot** : Activé sur GitHub, PR automatiques pour mises à jour sécurité
- **Review** : Obligatoire par 2 développeurs + tests CI/CD passés
- **Cadence** : Mises à jour mineures mensuelles, majeures trimestrielles

#### VMs Azure (OS Ubuntu)
- **Unattended Upgrades** : Mises à jour sécurité automatiques (apt)
- **Reboot** : Planifié dimanche 4h du matin (faible traffic)
- **Vérification** : Script post-reboot vérifie que Docker daemon + conteneurs sont UP

### 15.2. Plan de Support Client

| Niveau | Description | Temps de Réponse | Canal | SLA Résolution |
|--------|-------------|------------------|-------|----------------|
| **P1 (Critique)** | Service Down (API indispo, VPN down, 0 serveur démarre) | **< 30 min** | Téléphone astreinte + Discord urgent | **< 4h** |
| **P2 (Majeur)** | Dégradé (lenteurs, erreurs sporadiques, 1 serveur ne démarre pas) | **< 4h** | Ticket Email + Discord | **< 24h** |
| **P3 (Mineur)** | Question générale (config VPN, install OpenVPN, demande de feature) | **< 24h** | FAQ + Chatbot IA + Email | **< 48h** |

**Canaux de Support** :
1. **FAQ Interactive** : Knowledge base (Confluence/Notion) avec recherche
   - Section dédiée : "Comment installer OpenVPN" (tutoriels Windows/Mac/Linux)
2. **Chatbot IA** : GPT-4 entraîné sur notre doc (réponse instantanée 80% questions)
3. **Discord Communautaire** : Serveur Discord avec channels par catégorie
4. **Email** : support@minehost.com (ticketing Freshdesk)
5. **Téléphone** : Astreinte 24/7 pour P1 (rotation équipe DevOps)

**Équipe Support** :
- **Phase MVP** (0-50 clients) : Fondateurs assurent le support
- **Scaling** (50-200 clients) : Recrutement 1 Support Engineer (2500€/mois)
- **Growth** (200+ clients) : Équipe support 3 personnes + système de ticketing

### 15.3. Disaster Recovery (Plan de Continuité)

#### Objectifs
- **RTO (Recovery Time Objective)** : **15 minutes**
- **RPO (Recovery Point Objective)** : **1 heure** (perte de données maximale acceptable)

#### Scénario : Panne Région Azure France Central (Datacenter Down)

**Procédure de Failover** :

1. **Détection** (T+0) : Azure Monitor alerte l'équipe (SMS + email + Discord)
   
2. **Bascule DNS** (T+2 min) : 
   ```bash
   az network dns record-set a update --resource-group dns-rg \
     --zone-name minehost.com --name api --set arecords[0].ipv4Address=<IP_NORTH_EUROPE>
   ```

3. **Redéploiement Infrastructure** (T+5 min) :
   ```bash
   cd terraform/
   terraform apply -var="primary_region=northeurope" -auto-approve
   ```
   
4. **Restauration Données** (T+10 min) :
   - **Base de données** : Promotion du read-replica North Europe en primary (RPO = 0)
   - **Azure Files** : Copie depuis snapshot le plus récent (rétention 7 jours, RPO = 1h max)
   - **Certificats VPN** : Regénération depuis Azure Key Vault (répliqué geo)
   
5. **Redéploiement Conteneurs** (T+12 min) :
   - API redémarre automatiquement les conteneurs Docker sur les nouvelles VMs
   - Volumes Azure Files remontés (`docker run -v ...`)
   
6. **Validation** (T+14 min) : Tests smoke (créer 1 serveur, vérifier logs, connexion VPN)
   
7. **Communication** (T+15 min) : 
   - Bannière site : "Maintenance terminée, service rétabli"
   - Email clients : "Incident résolu, reconnectez-vous au VPN"
   - Post Discord : Post-mortem transparent de l'incident

**Coût du Failover** : ~100€ (coût infra temporaire en double pendant 1h)

#### Tests de DR
- **Fréquence** : 2 fois par an (janvier et juillet)
- **Documentation** : Temps réels enregistrés, amélioration continue du processus
- **Runbook** : Procédure détaillée accessible 24/7 (Confluence)

---

## 16. ADMINISTRATION & MAINTENABILITÉ

### 16.1. Infrastructure as Code (Terraform)

**Organisation du Code** :

```
terraform/
├── modules/
│   ├── networking/       # VNet, NSG, VPN Gateway
│   ├── compute/          # VMs Azure + Docker install
│   ├── storage/          # Azure Files, Blob (Terraform state)
│   ├── database/         # PostgreSQL avec read-replica
│   └── security/         # Key Vault, Managed Identity
├── environments/
│   ├── dev/              # Variables dev (1 VM, quotas réduits)
│   ├── staging/          # Pré-prod (2 VMs, France Central)
│   └── prod/             # Production (3 VMs, multi-régions)
├── main.tf               # Orchestration globale
├── variables.tf          # Paramètres configurables
└── outputs.tf            # IPs, URLs, connection strings
```

**Module Terraform : VMs Docker** :
```hcl
resource "azurerm_linux_virtual_machine" "docker_host" {
  count               = var.vm_count
  name                = "vm-docker-host-${count.index + 1}"
  location            = var.location
  resource_group_name = var.resource_group_name
  size                = "Standard_D4s_v3"
  
  admin_username = "azureuser"
  admin_ssh_key {
    username   = "azureuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }
  
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Premium_LRS"
  }
  
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }
  
  network_interface_ids = [
    azurerm_network_interface.docker_host[count.index].id
  ]
  
  custom_data = base64encode(templatefile("${path.module}/cloud-init.yaml", {
    docker_api_port = 2375
  }))
}
```

**Cloud-Init Script** (installation Docker automatique) :
```yaml
#cloud-config
package_update: true
package_upgrade: true

packages:
  - apt-transport-https
  - ca-certificates
  - curl
  - gnupg
  - lsb-release

runcmd:
  - curl -fsSL https://get.docker.com -o get-docker.sh
  - sh get-docker.sh
  
  - echo '{"hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]}' > /etc/docker/daemon.json
  - systemctl restart docker
  
  - docker pull itzg/minecraft-server:latest
  
  - wget https://aka.ms/InstallAzureMonitorLinuxAgent && sudo bash InstallAzureMonitorLinuxAgent
```

**Pipeline CI/CD (GitHub Actions)** :

```yaml
name: Terraform Deploy
on:
  push:
    branches: [main]
    paths: ['terraform/**']

jobs:
  terraform:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Terraform Init
        run: terraform init
        working-directory: terraform/environments/prod
      
      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: terraform/environments/prod
      
      - name: Manual Approval
        uses: trstringer/manual-approval@v1
        with:
          approvers: lead-devops,rssi
          minimum-approvals: 2
      
      - name: Terraform Apply
        run: terraform apply tfplan
        working-directory: terraform/environments/prod
```

**Bénéfices** :
-  Déploiement reproductible (dev = staging = prod)
-  Versioning de l'infrastructure (Git)
-  Disaster Recovery accéléré (1 commande `terraform apply`)
   Audit trail (qui a modifié quoi et quand)

### 16.2. Monitoring et Observabilité

#### Logs Centralisés (Azure Log Analytics)

**Sources** :
- API Flask (logs applicatifs via syslog)
- Conteneurs Docker (stdout/stderr redirigés)
- VPN OpenVPN (logs de connexion)
- PostgreSQL (slow queries, erreurs)
- VMs (syslog kernel, Docker daemon)

**Requêtes KQL Pré-Configurées** :
```kql
// Erreurs HTTP 5xx dans l'API (dernières 24h)
AppRequests
| where TimeGenerated > ago(24h)
| where ResultCode startswith "5"
| summarize count() by bin(TimeGenerated, 1h), ResultCode
| render timechart

// Tentatives de connexion VPN échouées (brute-force)
Syslog
| where Facility == "auth" and ProcessName == "openvpn"
| where SyslogMessage contains "TLS Error"
| summarize attempts=count() by SrcIP=extract("([0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+)", 1, SyslogMessage)
| where attempts > 5
| order by attempts desc

// Charge Docker par VM (conteneurs actifs)
ContainerInventory
| summarize containers=dcount(ContainerID) by Computer
| render columnchart
```

#### Métriques (Azure Monitor)

**Dashboards** :

1. **Dashboard Opérationnel** (Grafana, temps réel) :
   - Nombre de conteneurs actifs par VM (gauge)
   - CPU/RAM des VMs (line chart)
   - Latence API P50/P95/P99 (line chart)
   - Connexions VPN actives (gauge)

2. **Dashboard Business** (Power BI, hebdomadaire) :
   - Nouveaux utilisateurs (bar chart)
   - Churn rate (taux de désabonnement)
   - Revenus par région (map)
   - Coûts d'infrastructure vs CA (stacked area)

#### Alerting

**Règles d'Alerte** :

| Alerte | Condition | Destination | Criticité |
|--------|-----------|-------------|-----------|
| API Down | 5 requêtes échouées en 5 min | SMS + Discord | P1 |
| VM CPU Élevé | > 80% pendant 10 min | Email DevOps | P2 |
| VM RAM Saturée | > 90% pendant 5 min | Email DevOps | P2 |
| Conteneurs > 12/VM | Seuil densité dépassé | Email FinOps | P3 |
| VPN Connexions échouées | > 10 tentatives/min | Email RSSI | P2 |
| Coût Anormal | Coût quotidien > 25€ (vs 17€ attendu) | Email FinOps | P2 |

**Outil de Gestion d'Incidents** : PagerDuty (escalade automatique si pas de réponse en 15 min)

---

# ANNEXES

## ANNEXE A : Exemple de Code API 

```python
from flask import Flask, request, jsonify
from flask_limiter import Limiter
import docker
import re
import uuid

app = Flask(__name__)
limiter = Limiter(app, key_func=lambda: request.remote_addr)

docker_clients = {
    "vm-host-01": docker.DockerClient(base_url="tcp://10.0.2.10:2375"),
    "vm-host-02": docker.DockerClient(base_url="tcp://10.0.2.11:2375"),
    "vm-host-03": docker.DockerClient(base_url="tcp://10.0.2.12:2375"),
}

@app.route('/api/servers', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limiting
def create_server():
    """Endpoint de création de serveur Minecraft"""
    
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    server_name = request.json.get('name')
    if not re.match(r'^[a-z0-9-]{3,20}$', server_name):
        return jsonify({"error": "Nom invalide (a-z0-9- uniquement)"}), 400
    
    ram_size = request.json.get('ram', 2)
    if ram_size not in [2, 4, 8]:
        return jsonify({"error": "RAM doit être 2, 4 ou 8 GB"}), 400
    
    if count_user_servers(user_id) >= 5:
        return jsonify({"error": "Limite de 5 serveurs atteinte"}), 403
    
    target_vm = select_least_loaded_vm(docker_clients)
    client = docker_clients[target_vm]
    
    volume_name = f"vol-{user_id}-{uuid.uuid4().hex[:8]}"
    
    azure_storage.create_file_share(share_name=volume_name, quota=10)
    
    container = client.containers.run(
        image="itzg/minecraft-server:latest",
        name=f"{user_id}-{server_name}",
        detach=True,
        environment={
            "EULA": "TRUE",
            "VERSION": "1.20.4",
            "MAX_MEMORY": f"{ram_size-1}G"
        },
        volumes={
            f"/mnt/azurefiles/{volume_name}": {"bind": "/data", "mode": "rw"}
        },
        ports={"25565/tcp": None}, 
        mem_limit=f"{ram_size}g",
        cpu_quota=200000,  
        restart_policy={"Name": "unless-stopped"},
        network_mode="minecraft-net",
        user="1000:1000",  
        cap_drop=["ALL"],
        cap_add=["NET_BIND_SERVICE"],
        security_opt=["no-new-privileges"]
    )
    
    container.reload()
    private_ip = container.attrs['NetworkSettings']['Networks']['minecraft-net']['IPAddress']
    
    db.session.add(Server(
        owner_id=user_id,
        name=server_name,
        vm_host=target_vm,
        container_id=container.id,
        private_ip=private_ip,
        volume_name=volume_name,
        status="running",
        created_at=datetime.utcnow()
    ))
    db.session.commit()
    
    return jsonify({
        "status": "running",
        "private_ip": f"{private_ip}:25565",
        "vpn_config_url": f"/api/vpn/config/{user_id}",
        "instructions": "Téléchargez le fichier .ovpn, installez OpenVPN, puis connectez-vous pour accéder à votre serveur"
    }), 201


def select_least_loaded_vm(docker_clients):
    """Sélectionne la VM avec le moins de conteneurs actifs"""
    loads = {}
    for vm_name, client in docker_clients.items():
        try:
            loads[vm_name] = len(client.containers.list())
        except Exception as e:
            logger.error(f"Cannot connect to {vm_name}: {e}")
            loads[vm_name] = 999  # Pénalité si VM inaccessible
    return min(loads, key=loads.get)
```

---

## ANNEXE B : Glossaire Technique

| Terme | Définition |
|-------|------------|
| **AES-256** | Advanced Encryption Standard 256 bits - Chiffrement symétrique standard |
| **BOLA/IDOR** | Broken Object Level Authorization / Insecure Direct Object Reference - Vulnérabilité permettant accès non autorisé |
| **cgroups** | Control Groups - Mécanisme Linux pour limiter ressources (CPU, RAM) d'un processus |
| **CIS Benchmark** | Center for Internet Security - Référentiel de bonnes pratiques sécurité |
| **CSRF** | Cross-Site Request Forgery - Attaque forçant un utilisateur authentifié à exécuter des actions non désirées |
| **DAST** | Dynamic Application Security Testing - Tests de sécurité en boîte noire |
| **DDoS** | Distributed Denial of Service - Attaque saturant un service par du trafic massif |
| **Docker** | Plateforme de conteneurisation permettant d'isoler des applications |
| **FinOps** | Financial Operations - Discipline d'optimisation des coûts cloud |
| **NSG** | Network Security Group - Firewall Azure au niveau sous-réseau/NIC |
| **OpenVPN** | Solution VPN open-source utilisant des certificats X.509 pour l'authentification |
| **P95** | 95e percentile - 95% des requêtes sont plus rapides que cette valeur |
| **RCON** | Remote Console - Protocole pour administrer un serveur Minecraft à distance |
| **SAST** | Static Application Security Testing - Analyse de code source (boîte blanche) |
| **Scrypt** | Fonction de hachage cryptographique conçue pour être coûteuse en mémoire |
| **SMB 3.0** | Server Message Block - Protocole de partage de fichiers (Azure Files) |
| **VNet** | Virtual Network - Réseau privé isolé dans Azure |
| **ZRS** | Zone-Redundant Storage - 3 copies sur 3 zones de disponibilité |

---

## ANNEXE C : Références et Documentation

### Standards de Sécurité
- **CIS Docker Benchmark v1.6.0** : https://www.cisecurity.org/benchmark/docker
- **OWASP Top 10 (2021)** : https://owasp.org/www-project-top-ten/
- **NIST Cybersecurity Framework** : https://www.nist.gov/cyberframework
- **ISO 27001** : https://www.iso.org/isoiec-27001-information-security.html

### Documentation Azure
- **Azure Virtual Machines** : https://learn.microsoft.com/azure/virtual-machines/
- **Azure Files** : https://learn.microsoft.com/azure/storage/files/
- **Azure VPN Gateway** : https://learn.microsoft.com/azure/vpn-gateway/
- **Azure Key Vault** : https://learn.microsoft.com/azure/key-vault/

### Documentation Docker
- **Docker Engine** : https://docs.docker.com/engine/
- **Docker SDK for Python** : https://docker-py.readthedocs.io/
- **Docker Security Best Practices** : https://docs.docker.com/engine/security/

### Projets Open-Source
- **itzg/docker-minecraft-server** : https://github.com/itzg/docker-minecraft-server (25k+ stars)
- **Terraform Azure Provider** : https://registry.terraform.io/providers/hashicorp/azurerm/
- **OpenVPN** : https://openvpn.net/community-resources/

