# Quiz App

Application mobile de quiz réservée aux élèves d'une école, avec login par matricule,
quiz générés par IA (matières universitaires uniquement), classement et défis en ligne.

## Structure

```
quiz-app/
├── backend/                  # API FastAPI + PostgreSQL
│   ├── app/
│   │   ├── main.py           # point d'entrée FastAPI
│   │   ├── config.py         # variables d'environnement
│   │   ├── database.py       # connexion SQLAlchemy
│   │   ├── models.py         # Eleve, Matiere, Quiz, Resultat, Defi
│   │   ├── schemas.py        # schémas Pydantic
│   │   ├── routers/
│   │   │   ├── auth.py       # POST /auth/login
│   │   │   ├── matieres.py   # GET /matieres/{nom}
│   │   │   ├── quiz.py       # POST /quiz/generate, POST /quiz/submit
│   │   │   ├── classement.py # GET /classement (avec filtre optionnel ?matiere=)
│   │   │   ├── defis.py      # POST /defis/creer, POST /defis/{id}/soumettre, GET /defis/{matricule}/liste
│   │   │   ├── admin.py      # CRUD élèves + matières, protégé par la clé ADMIN_API_KEY
│   │   │   ├── notifications.py # GET /notifications/{matricule}, POST .../tout_marquer_lu
│   │   │   └── historique.py # GET /historique/{matricule} — quiz passés, score moyen
│   │   └── services/
│   │       └── ai_service.py # génération des questions via l'API Groq (gratuite, sans carte bancaire)
│   ├── seed.py                # insère des élèves/matières de test
│   ├── requirements.txt
│   └── .env.example
│
└── mobile/                    # App Kivy
    ├── main.py                 # point d'entrée, gère le ScreenManager
    ├── screens/
    │   ├── login_screen.py     # écran de connexion par matricule
    │   ├── home_screen.py      # écran de choix de matière
    │   ├── quiz_screen.py      # passage du quiz (normal OU défi), question par question, puis score
    │   ├── classement_screen.py # affichage du classement général
    │   ├── defi_creation_screen.py # lancer un défi contre un autre élève
    │   ├── defis_liste_screen.py   # liste de mes défis en cours et terminés
    │   ├── notifications_screen.py # notifications (défi reçu, adversaire a répondu, résultat)
    │   └── historique_screen.py    # historique des quiz passés + moyenne générale
    ├── services/
    │   └── api_service.py      # tous les appels HTTP vers le backend
    ├── buildozer.spec           # configuration pour compiler l'app en .apk Android
    └── requirements.txt

admin/
└── index.html                  # interface web d'administration (élèves + matières)
```

## Obtenir ta clé API Groq (gratuite, sans carte bancaire)

1. Va sur https://console.groq.com et inscris-toi (email ou Google)
2. Dans le menu, va sur "API Keys" → "Create API Key"
3. Copie la clé (elle commence par `gsk_`)
4. Colle-la dans `backend/.env` à la ligne `GROQ_API_KEY=`

Aucune carte bancaire n'est demandée pour le tier gratuit. Les limites de requêtes
(largement suffisantes pour un usage étudiant) sont visibles sur
https://console.groq.com/settings/limits une fois connecté.

## Lancer le backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Éditer .env avec ta vraie URL PostgreSQL et ta clé API Groq (gratuite, voir ci-dessous)

# Créer une base PostgreSQL nommée quizapp_db au préalable, puis :
python seed.py                  # insère des données de test
uvicorn app.main:app --reload   # lance le serveur sur http://127.0.0.1:8000
```

Tester rapidement avec les matricules de test : `ENI2024-001` ou `ENI2024-002`.

## Lancer l'app mobile (en mode bureau, pour tester avant Buildozer)

```bash
cd mobile
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Si le backend tourne sur un autre appareil ou une autre adresse, modifie `BASE_URL`
dans `mobile/services/api_service.py`.

## Ce qui est fait (Étape 1 : Base + Auth)

- [x] Structure du projet backend + mobile
- [x] Modèles PostgreSQL : élèves, matières (avec champ niveau), quiz, résultats, défis
- [x] Login par matricule (`POST /auth/login`)
- [x] Vérification du niveau de matière (`GET /matieres/{nom}`) — renvoie un message de
      refus si la matière n'est pas universitaire
- [x] Écran Kivy de connexion + écran de choix de matière

## Ce qui est fait (Étape 2 : Génération de quiz par IA)

- [x] `POST /quiz/generate` — génère 5 questions à choix multiples via l'API Groq,
      avec mise en cache simple (réutilise le dernier quiz généré pour la matière)
- [x] `POST /quiz/submit` — calcule le score en comparant les réponses de l'élève aux
      bonnes réponses stockées côté serveur (jamais envoyées au client)
- [x] Écran Kivy `quiz_screen.py` : affiche les questions une par une, boutons pour
      choisir une réponse, puis affiche le score final

## Ce qui est fait (Étape 3 : Classement)

- [x] `GET /classement` — classe les élèves par score moyen (filtrable par matière avec
      `?matiere=...`), calculé via une agrégation SQL (AVG des scores, groupé par élève)
- [x] Écran Kivy `classement_screen.py` : liste défilante avec rang, nom, matricule,
      score moyen et nombre de quiz passés
- [x] Bouton "Voir le classement" ajouté sur l'écran d'accueil

## Ce qui est fait (Étape 4 : Défis en ligne)

- [x] `POST /defis/creer` — un élève défie un autre sur une matière ; un quiz dédié est
      généré (les deux élèves répondent aux mêmes questions, pour une comparaison équitable)
- [x] `POST /defis/{defi_id}/soumettre` — enregistre le score de chaque participant ; dès
      que les deux ont joué, calcule automatiquement Victoire/Défaite/Égalité
- [x] `GET /defis/{matricule}/liste` — historique des défis d'un élève (en attente, en
      cours, terminés) avec les scores des deux camps
- [x] `defi_creation_screen.py` — saisir le matricule de l'adversaire + la matière, puis
      lancer le défi (réutilise `quiz_screen.py` en mode défi)
- [x] `defis_liste_screen.py` — liste de tous les défis de l'élève connecté
- [x] Bouton "Défier un élève" ajouté sur l'écran d'accueil

## Interface d'administration

Un fichier HTML autonome (`admin/index.html`) permet de gérer les élèves et les
matières sans toucher à la base de données directement.

1. Lance le backend (voir ci-dessus)
2. Ouvre `admin/index.html` directement dans un navigateur (double-clic suffit)
3. Renseigne l'URL du backend (ex: `http://127.0.0.1:8000`) et la clé `ADMIN_API_KEY`
   définie dans ton `.env`, puis clique sur "Se connecter"
4. Ajoute/supprime des élèves (matricule, nom, école) et des matières (nom + niveau
   universitaire/secondaire) — clique sur "Modifier" pour éditer une ligne directement
   dans le tableau, "Enregistrer" pour valider ou "Annuler" pour revenir en arrière

Toutes les routes `/admin/*` exigent l'en-tête `X-Admin-Key` — sans la bonne clé,
elles renvoient une erreur 401. Pense à changer `ADMIN_API_KEY` avant tout déploiement
réel (la valeur par défaut `change-moi` n'est pas sécurisée).

## Ce qui est fait (Étape 5 : Interface d'administration)

- [x] `GET/POST/PUT/DELETE /admin/eleves` — gestion complète des élèves
- [x] `GET/POST/PUT/DELETE /admin/matieres` — gestion complète des matières (avec
      validation du niveau : universitaire ou secondaire)
- [x] Protection par clé secrète (`X-Admin-Key`) sur toutes les routes admin
- [x] Interface web autonome (`admin/index.html`) : tableaux + formulaires d'ajout,
      édition en ligne directement dans le tableau (Modifier/Enregistrer/Annuler),
      suppression en un clic, aucune installation nécessaire (juste un navigateur)
- [x] CORS activé côté backend pour permettre à cette page de l'appeler

## L'application est maintenant fonctionnelle de bout en bout, avec administration complète

## Ce qui est fait (Étape 6 : Notifications de défi)

- [x] Nouvelle table `notifications` (destinataire, message, lu/non lu, défi lié)
- [x] Un élève est notifié dès qu'on le défie (`POST /defis/creer`)
- [x] Un élève est notifié dès que son adversaire répond au défi — que ce soit le
      premier à jouer ("à toi de jouer !") ou le second (résultat final : Victoire/
      Défaite/Égalité)
- [x] `GET /notifications/{matricule}` — liste des notifications + nombre de non lues
- [x] `POST /notifications/{matricule}/tout_marquer_lu` — marque tout comme lu
- [x] Écran Kivy `notifications_screen.py`, et badge "Notifications (N)" sur l'accueil
      qui se met à jour à chaque retour sur cet écran

### Pistes d'amélioration futures (non demandées mais utiles)
- Remplacer le polling par un vrai push (Firebase Cloud Messaging) pour recevoir les
  notifications même app fermée
- Remplacer la clé admin unique par un vrai système de comptes utilisateurs
- Inclure les défis dans l'historique (actuellement seulement les quiz normaux)

## Ce qui est fait (Étape 7 : Historique des quiz)

- [x] `GET /historique/{matricule}` — liste tous les quiz passés par un élève (matière,
      score, date), avec la moyenne générale et le nombre total de quiz
- [x] Écran Kivy `historique_screen.py` : résumé en haut (nombre de quiz + moyenne),
      liste chronologique en dessous
- [x] Bouton "Mon historique" ajouté sur l'écran d'accueil

## Étape 8 : Compiler un .apk avec Buildozer

⚠️ **Important avant de compiler** : ouvre `mobile/services/api_service.py` et remplace
`BASE_URL = "http://127.0.0.1:8000"` par l'adresse réelle de ton backend. `127.0.0.1`
sur un téléphone pointe vers le téléphone lui-même, pas vers ton PC — l'app ne
fonctionnera pas tant que ce n'est pas corrigé. Deux options :
- Backend déployé en ligne (Railway, Render...) → mets son URL publique (`https://...`)
- Backend lancé sur ton PC, test sur le même réseau Wi-Fi → mets l'IP locale de ton PC
  (ex: `http://192.168.1.42:8000`), trouvable avec `ipconfig` (Windows) ou `ip a` (Linux/Mac)

### Prérequis (sur ta machine, Linux recommandé — WSL2 fonctionne sous Windows)

- Python 3.10+ et pip
- Java JDK 17
- Les paquets système : `git zip unzip openjdk-17-jdk python3-pip autoconf libtool
  pkg-config zlib1g-dev libncurses5-dev libtinfo5 cmake libffi-dev libssl-dev`
  (`sudo apt install ...` sur Ubuntu/Debian)

Buildozer télécharge lui-même le SDK et le NDK Android au premier lancement — c'est
normal que ça prenne du temps (plusieurs centaines de Mo) et une connexion stable.

### Étapes de compilation

```bash
cd mobile
python -m venv venv
source venv/bin/activate
pip install buildozer cython==0.29.36

# Première compilation (télécharge le SDK/NDK Android, peut prendre 20-40 min)
buildozer -v android debug
```

L'APK généré se trouve dans `mobile/bin/quizapp-0.1-arm64-v8a-debug.apk`.

### Installer l'APK sur un téléphone

**Option A — via USB avec adb :**
```bash
adb install bin/quizapp-0.1-arm64-v8a-debug.apk
```
(active le mode développeur + débogage USB sur le téléphone au préalable)

**Option B — sans USB :**
Transfère le fichier `.apk` sur le téléphone (clé USB, Bluetooth, lien de téléchargement,
etc.), puis ouvre-le directement depuis le gestionnaire de fichiers du téléphone.
Android demandera d'autoriser "l'installation depuis des sources inconnues" — c'est
normal pour une app qui n'est pas sur le Play Store.

### Problèmes fréquents

- **Erreur de licence Android SDK** : lance `yes | buildozer android sdkmanager
  --licenses` avant `buildozer -v android debug`
- **Build très lent ou qui échoue à la première tentative** : relance simplement
  `buildozer -v android debug` — le SDK/NDK est mis en cache après le premier téléchargement
- **L'app se lance mais rien ne répond** : vérifie `BASE_URL` (voir avertissement
  ci-dessus) et que le backend est bien accessible depuis le téléphone (même réseau
  Wi-Fi si en local, pare-feu du PC pas bloquant)
- **Pour nettoyer un build cassé** : `buildozer android clean` puis relancer
