# Credentials

Ce dossier doit contenir les fichiers de credentials pour l'accès à l'API Google/Gmail.

## Fichiers requis :
- `gmail_credentials.json` : Le fichier de credentials téléchargé depuis la Google Cloud Console (OAuth 2.0 Client ID).

## Fichiers générés automatiquement :
- `gmail_token.json` : Ce fichier sera généré automatiquement lors de la première exécution si `gmail_credentials.json` est présent et que vous vous authentifiez.

## Comment obtenir `gmail_credentials.json` ?
1. Aller sur Google Cloud Console.
2. Sélectionner le projet associé à M54.
3. Aller dans "APIs & Services" > "Credentials".
4. Télécharger le fichier JSON pour le client OAuth 2.0.
5. Renommer ce fichier en `gmail_credentials.json` et le placer ici.
