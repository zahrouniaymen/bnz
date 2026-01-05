# Guide de Déploiement M54 - Partage avec Collègues

## 🚀 Options de Déploiement

### Option 1 : Ngrok (Le Plus Rapide - 5 minutes)

**Avantages :** Gratuit, très rapide, pas de configuration
**Inconvénients :** URL change à chaque redémarrage, limité en temps

#### Installation et Utilisation

1. **Télécharger Ngrok**
   - Aller sur https://ngrok.com/download
   - Télécharger pour Windows
   - Extraire le fichier `ngrok.exe`

2. **Créer un compte gratuit**
   - Aller sur https://dashboard.ngrok.com/signup
   - Créer un compte gratuit
   - Copier votre authtoken

3. **Configurer Ngrok**
   ```powershell
   # Dans le dossier où vous avez extrait ngrok.exe
   .\ngrok.exe authtoken VOTRE_TOKEN_ICI
   ```

4. **Démarrer vos serveurs**
   ```powershell
   # Terminal 1 - Backend
   cd C:\Users\mayme\Desktop\M54\backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Frontend (build production)
   cd C:\Users\mayme\Desktop\M54\frontend
   npm run build
   npm run preview -- --host 0.0.0.0 --port 5173
   ```

5. **Exposer avec Ngrok**
   ```powershell
   # Terminal 3 - Ngrok pour le frontend
   .\ngrok.exe http 5173
   
   # Terminal 4 - Ngrok pour le backend
   .\ngrok.exe http 8000
   ```

6. **Partager les URLs**
   - Ngrok affichera des URLs comme : `https://xxxx-xxxx.ngrok-free.app`
   - Notez l'URL du frontend et du backend
   - Vous devrez modifier le frontend pour pointer vers l'URL backend Ngrok

#### Modifier le Frontend pour Ngrok

Créez un fichier `.env.production` dans `frontend/` :

```env
VITE_API_URL=https://VOTRE-URL-BACKEND-NGROK.ngrok-free.app
```

Modifiez `frontend/src/services/api.js` pour utiliser cette variable :

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

---

### Option 2 : Render.com (Gratuit et Permanent)

**Avantages :** Gratuit, URL permanente, professionnel
**Inconvénients :** Configuration plus longue (30 minutes)

#### Étapes

1. **Créer un compte sur Render.com**
   - Aller sur https://render.com
   - Créer un compte gratuit

2. **Préparer le Backend**
   
   Créer `backend/render.yaml` :
   ```yaml
   services:
     - type: web
       name: m54-backend
       env: python
       buildCommand: pip install -r requirements.txt
       startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: PYTHON_VERSION
           value: 3.11.0
   ```

3. **Préparer le Frontend**
   
   Créer `frontend/render.yaml` :
   ```yaml
   services:
     - type: web
       name: m54-frontend
       env: node
       buildCommand: npm install && npm run build
       startCommand: npm run preview -- --host 0.0.0.0 --port $PORT
   ```

4. **Déployer sur Render**
   - Connecter votre dépôt GitHub (vous devrez d'abord pousser le code sur GitHub)
   - Créer un nouveau "Web Service" pour le backend
   - Créer un nouveau "Web Service" pour le frontend
   - Render vous donnera des URLs permanentes

---

### Option 3 : Partage Réseau Local (Si même bureau)

**Avantages :** Gratuit, rapide, pas de compte nécessaire
**Inconvénients :** Fonctionne uniquement sur le même réseau WiFi/LAN

#### Configuration

1. **Trouver votre IP locale**
   ```powershell
   ipconfig
   # Chercher "Adresse IPv4" (ex: 192.168.1.100)
   ```

2. **Démarrer les serveurs**
   ```powershell
   # Backend
   cd C:\Users\mayme\Desktop\M54\backend
   uvicorn main:app --host 0.0.0.0 --port 8000
   
   # Frontend
   cd C:\Users\mayme\Desktop\M54\frontend
   npm run dev -- --host 0.0.0.0
   ```

3. **Partager l'URL**
   - Votre collègue peut accéder via : `http://VOTRE_IP:5173`
   - Exemple : `http://192.168.1.100:5173`

4. **Configurer le Pare-feu Windows**
   ```powershell
   # Autoriser les ports
   netsh advfirewall firewall add rule name="M54 Frontend" dir=in action=allow protocol=TCP localport=5173
   netsh advfirewall firewall add rule name="M54 Backend" dir=in action=allow protocol=TCP localport=8000
   ```

---

### Option 4 : Vercel + Railway (Recommandé pour Production)

**Avantages :** Gratuit, rapide, professionnel, CI/CD automatique
**Inconvénients :** Nécessite GitHub

#### Frontend sur Vercel

1. **Pousser le code sur GitHub**
   ```powershell
   cd C:\Users\mayme\Desktop\M54
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/VOTRE_USERNAME/m54.git
   git push -u origin main
   ```

2. **Déployer sur Vercel**
   - Aller sur https://vercel.com
   - Importer le projet GitHub
   - Configurer :
     - Framework Preset: Vite
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`

3. **Variables d'environnement**
   - Ajouter `VITE_API_URL` avec l'URL de votre backend Railway

#### Backend sur Railway

1. **Déployer sur Railway**
   - Aller sur https://railway.app
   - "New Project" → "Deploy from GitHub repo"
   - Sélectionner votre dépôt
   - Configurer :
     - Root Directory: `backend`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Ajouter la base de données**
   - Railway vous donnera une URL permanente
   - Copier cette URL et l'ajouter dans Vercel comme `VITE_API_URL`

---

## 🎯 Recommandation

**Pour un test rapide (aujourd'hui) :**
→ **Option 1 : Ngrok** (5 minutes)

**Pour partage réseau local (même bureau) :**
→ **Option 3 : Réseau Local** (2 minutes)

**Pour production (permanent) :**
→ **Option 4 : Vercel + Railway** (30 minutes)

---

## 📝 Script Rapide Ngrok

Créez `start-ngrok.ps1` :

```powershell
# Démarrer le backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\mayme\Desktop\M54\backend; uvicorn main:app --host 0.0.0.0 --port 8000"

# Attendre 5 secondes
Start-Sleep -Seconds 5

# Démarrer le frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\mayme\Desktop\M54\frontend; npm run preview -- --host 0.0.0.0 --port 5173"

# Attendre 5 secondes
Start-Sleep -Seconds 5

# Démarrer Ngrok pour le frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\ngrok.exe http 5173"

# Démarrer Ngrok pour le backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".\ngrok.exe http 8000"

Write-Host "✅ Tous les services démarrés !"
Write-Host "📋 Copiez les URLs Ngrok et partagez-les avec votre collègue"
```

Exécutez : `.\start-ngrok.ps1`

---

## 🔒 Sécurité

**Important :** Avant de partager :

1. **Réactiver l'authentification**
   - Retirer les endpoints `/test`
   - Activer JWT dans `backend/main.py`

2. **Variables d'environnement**
   - Ne jamais partager les credentials Gmail
   - Utiliser `.env` pour les secrets

3. **CORS**
   - Configurer les origines autorisées dans `backend/main.py`

---

**Besoin d'aide ?** Dites-moi quelle option vous préférez et je vous guide pas à pas ! 🚀
