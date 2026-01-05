# Quick Start Guide - M54 Offer Management System

## 🚀 Démarrage Rapide (5 minutes)

### Étape 1: Installation des dépendances

```powershell
# Backend
cd C:\Users\mayme\Desktop\M54\backend
pip install -r requirements.txt

# Frontend  
cd C:\Users\mayme\Desktop\M54\frontend
npm install
```

### Étape 2: Initialisation de la base de données

```powershell
cd C:\Users\mayme\Desktop\M54
python init_db.py
```

✅ Cela crée automatiquement:
- Base de données SQLite
- 6 utilisateurs de test avec mots de passe
- 2 clients de test

### Étape 3: Démarrer l'application

**Terminal 1 - Backend:**
```powershell
cd C:\Users\mayme\Desktop\M54\backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\mayme\Desktop\M54\frontend
npm run dev
```

### Étape 4: Se connecter

Ouvrez http://localhost:5173 dans votre navigateur.

**Identifiants de test:**
- **Admin**: `admin` / `admin123`
- **Chiara (Commerciale)**: `chiara` / `chiara123`
- **Fattibilità**: `fattibilita` / `fatti123`
- **Tecnico**: `cristian` / `crist123`
- **Acquisti**: `acquisti` / `acqui123`
- **Pianificazione**: `pianificazione` / `piani123`

## 📋 Fonctionnalités Disponibles

### ✅ Implémenté
- ✅ Authentification avec JWT
- ✅ Dashboard avec statistiques
- ✅ Liste des offres avec filtres
- ✅ Détails offre
- ✅ Gestion workflow
- ✅ Upload fichiers
- ✅ Notes par département
- ✅ Messages/Chat
- ✅ Permissions basées sur rôles

### 🚧 En Développement
- 🚧 Intégration Gmail API
- 🚧 Notifications temps réel (WebSocket)
- 🚧 Statistiques avancées
- 🚧 Export Excel/PDF

## 🔧 Structure de l'Application

```
Backend (FastAPI):
- 40+ endpoints REST
- JWT authentication
- SQLAlchemy ORM
- Role-based permissions

Frontend (React):
- Login / Protected routes
- Dashboard role-based
- Offer management
- File upload
- Real-time updates
```

## 🆘 Problèmes Courants

**Port déjà utilisé:**
```powershell
# Changer le port backend dans backend/main.py
uvicorn main:app --reload --port 8001

# Changer le port frontend dans vite.config.js
```

**Erreur d'import:**
```powershell
# Vérifier que vous êtes dans le bon répertoire
cd C:\Users\mayme\Desktop\M54
python init_db.py
```

**Base de données verrouillée:**
```powershell
# Supprimer et recréer
del sql_app.db
python init_db.py
```

## 📝 Prochaines Étapes

1. Tester l'application avec les comptes de test
2. Créer des offres de test
3. Tester le workflow entre départements
4. Configurer l'intégration email (optionnel)
5. Déployer en production

## 📞 Support

Pour toute question, vérifier:
1. Les logs dans les terminaux
2. La console du navigateur (F12)
3. Le fichier README.md complet
