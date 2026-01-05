# M54 Offer Management System - Setup Guide

## 🚨 PowerShell Execution Policy Issue

Votre système a une politique d'exécution PowerShell restrictive qui empêche l'exécution de npm et npx.

### Solution Rapide

Ouvrez PowerShell **en tant qu'administrateur** et exécutez :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Puis confirmez avec `Y` (Oui).

---

## 📦 Installation des Dépendances

### Backend

Le backend est déjà configuré. Pour installer les dépendances :

```powershell
cd C:\Users\mayme\Desktop\M54\backend
pip install -r requirements.txt
```

### Frontend

Après avoir résolu le problème PowerShell ci-dessus :

```powershell
cd C:\Users\mayme\Desktop\M54\frontend
npm install
```

---

## 🚀 Démarrage de l'Application

### 1. Démarrer le Backend (Terminal 1)

```powershell
cd C:\Users\mayme\Desktop\M54\backend
uvicorn main:app --reload
```

Le backend sera accessible sur : **http://localhost:8000**

### 2. Démarrer le Frontend (Terminal 2)

```powershell
cd C:\Users\mayme\Desktop\M54\frontend
npm run dev
```

Le frontend sera accessible sur : **http://localhost:5173**

---

## 📊 Import des Données

Pour importer les données depuis le fichier Excel :

```powershell
cd C:\Users\mayme\Desktop\M54
python import_script.py
```

---

## 🎯 Fonctionnalités Disponibles

### Dashboard
- Vue d'ensemble avec statistiques en temps réel
- Nombre total d'offres
- Offres en cours, acceptées, déclinées
- Valeur totale des offres

### Liste des Offres
- Tableau complet de toutes les offres
- Filtres avancés par :
  - Statut
  - Client
  - Gestionnaire
  - Vérifications des départements (Fattibilità, Tecnico, Acquisti, Pianificazione)
- Navigation vers les détails

### Détails de l'Offre
- Vue complète de toutes les informations
- Mode édition pour modifier les données
- Organisation par sections :
  - Informations de base
  - Vérifications des départements
  - Gestion et tempistiques
  - Informations financières
  - Notes

---

## 🎨 Design System

L'application utilise un design premium avec :
- **Thème sombre** avec palette de couleurs moderne
- **Glassmorphism** pour les cartes et conteneurs
- **Gradients** pour les accents et boutons
- **Animations fluides** pour les interactions
- **Police Inter** pour une typographie moderne
- **Design responsive** pour tous les écrans

---

## 🔧 Structure du Projet

```
M54/
├── backend/
│   ├── main.py           # API FastAPI
│   ├── models.py         # Modèles SQLAlchemy
│   ├── schemas.py        # Schémas Pydantic
│   ├── crud.py           # Opérations CRUD
│   ├── database.py       # Configuration DB
│   └── requirements.txt  # Dépendances Python
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── OfferList.jsx
│   │   │   └── OfferDetail.jsx
│   │   ├── services/
│   │   │   └── api.js    # Client API
│   │   ├── App.jsx       # Composant principal
│   │   └── index.css     # Design system
│   ├── package.json
│   └── vite.config.js
└── import_script.py      # Script d'import Excel
```

---

## 📝 API Endpoints

- `GET /offers/` - Liste toutes les offres
- `GET /offers/{id}` - Détails d'une offre
- `POST /offers/` - Créer une offre
- `PUT /offers/{id}` - Mettre à jour une offre

---

## ⚡ Prochaines Étapes

1. Résoudre le problème PowerShell
2. Installer les dépendances
3. Démarrer le backend
4. Démarrer le frontend
5. Importer les données (si pas déjà fait)
6. Accéder à l'application sur http://localhost:5173

---

## 🆘 Support

Si vous rencontrez des problèmes :

1. Vérifiez que Python et Node.js sont installés
2. Vérifiez que les ports 8000 et 5173 sont disponibles
3. Consultez les logs dans les terminaux
4. Vérifiez que la base de données SQLite est créée (`sql_app.db`)
