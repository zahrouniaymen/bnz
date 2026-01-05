# Configuration Gmail pour Import Email

## Prérequis

Pour utiliser la fonctionnalité d'import email, vous devez configurer l'accès à Gmail API.

## Étapes de Configuration

### 1. Installer les bibliothèques Google

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib beautifulsoup4
```

### 2. Créer un Projet Google Cloud

1. Aller sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créer un nouveau projet ou sélectionner un projet existant
3. Activer Gmail API :
   - Menu "APIs & Services" > "Library"
   - Rechercher "Gmail API"
   - Cliquer sur "Enable"

### 3. Créer des Credentials OAuth 2.0

1. Menu "APIs & Services" > "Credentials"
2. Cliquer sur "Create Credentials" > "OAuth client ID"
3. Type d'application : "Desktop app"
4. Nom : "M54 Email Importer"
5. Télécharger le fichier JSON

### 4. Configurer les Credentials

1. Créer le dossier `backend/credentials/` :
   ```bash
   mkdir backend/credentials
   ```

2. Copier le fichier JSON téléchargé dans `backend/credentials/gmail_credentials.json`

### 5. Premier Lancement

Au premier lancement de l'import email :
1. Une fenêtre de navigateur s'ouvrira
2. Connectez-vous avec le compte `commerciale@benozzi.com`
3. Autorisez l'application à accéder à Gmail
4. Le token sera sauvegardé dans `backend/credentials/gmail_token.json`

## Configuration des Labels Gmail

L'import recherche les emails avec le label **`1-RICHIESTA_D'OFFERTA`**.

Après traitement, les emails sont déplacés vers **`2-OFFERTE_DA_GESTIRE`**.

### Créer les Labels

1. Ouvrir Gmail
2. Paramètres > Labels
3. Créer les labels :
   - `1-RICHIESTA_D'OFFERTA`
   - `2-OFFERTE_DA_GESTIRE`

## Utilisation

1. **Dashboard** : Cliquer sur le bouton "📧 Importa Email"
2. **Ligne de commande** : 
   ```bash
   cd backend
   python email_importer.py
   ```

## Dépannage

### Erreur "Credentials not found"
- Vérifier que le fichier `backend/credentials/gmail_credentials.json` existe
- Vérifier les permissions du fichier

### Erreur "Invalid grant"
- Supprimer `backend/credentials/gmail_token.json`
- Relancer l'import pour réautoriser

### Aucun email trouvé
- Vérifier que les labels existent dans Gmail
- Vérifier qu'il y a des emails avec le label `1-RICHIESTA_D'OFFERTA`

## Structure des Fichiers

```
M54/
├── backend/
│   ├── credentials/
│   │   ├── gmail_credentials.json  (à créer)
│   │   └── gmail_token.json        (généré automatiquement)
│   └── email_importer.py
```

## Sécurité

⚠️ **IMPORTANT** : Ne jamais commiter les fichiers de credentials dans Git !

Ajouter au `.gitignore` :
```
backend/credentials/
*.json
!package.json
!package-lock.json
```
