@echo off
echo ========================================
echo   REPARATION DE L'APPLICATION M54
echo ========================================
echo.
echo [1/4] Verification de Python...
python --version
if %errorLevel% neq 0 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH.
    pause
    exit /b 1
)

echo.
echo [2/4] Recreation de l'environnement virtuel (.venv)...
if exist .venv (
    echo .venv existe deja, suppression...
    rmdir /s /q .venv
)
python -m venv .venv
if %errorLevel% neq 0 (
    echo ERREUR: Impossible de creer .venv.
    pause
    exit /b 1
)

echo.
echo [3/4] Installation des dependances...
call .venv\Scripts\activate

echo Installation de pip...
python -m pip install --upgrade pip

echo Installation des librairies requises...
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart requests openpyxl pandas bcrypt

if %errorLevel% neq 0 (
    echo ERREUR lors de l'installation des dependances.
    pause
    exit /b 1
)

echo.
echo [4/4] Verification terminee !
echo ========================================
echo.
echo L'environnement est repare. 
echo Vous pouvez maintenant lancer start_app_new.bat
echo.
pause
