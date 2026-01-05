@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   LANCEMENT DE L'APPLICATION M54
echo ===================================================
echo.

:: 1. Verification Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe.
    pause
    exit /b 1
)

:: 2. Verification .venv
echo [1/3] Verification environnement...
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Creation de l'environnement virtuel...
    if exist ".venv" rmdir /s /q .venv
    python -m venv .venv
    if errorlevel 1 (
        echo [ERREUR] Echec creation .venv
        pause
        exit /b 1
    )
    echo [INFO] Installation des dependances...
    call .venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r backend/requirements.txt
    if errorlevel 1 (
        echo [ERREUR] Echec installation dependances
        pause
        exit /b 1
    )
) else (
    echo [OK] Environnement pret.
    echo [INFO] Verification des dependances...
    call .venv\Scripts\activate
    pip install -r backend/requirements.txt --quiet
)

:: 3. Lancement Backend
echo [2/3] Demarrage Backend (Port 8002)...
start "M54_Backend" cmd /k "call .venv\Scripts\activate && cd backend && uvicorn main:app --host 0.0.0.0 --port 8002"

:: Pause pour laisser uvicorn demarrer
ping 127.0.0.1 -n 5 > nul

:: 4. Lancement Frontend
echo [3/3] Demarrage Frontend (Port 5175)...
echo.
echo [IMPORTANT] Adresses d'acces :
echo - Localement : http://localhost:5175

:: Detection IP simplifiee
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    set "ipaddr=%%i"
    set "ipaddr=!ipaddr: =!"
    echo - Reseau : http://!ipaddr!:5175
)

start "M54_Frontend" cmd /k "cd frontend && npm run dev -- --port 5175 --host"

echo.
echo ===================================================
echo   L'application est lancee !
echo   Ne fermez pas les fenetres qui viennent de s'ouvrir.
echo ===================================================
echo.
pause
