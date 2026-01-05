# M54 Offer Management System v2.0

Sistema completo di gestione offerte Benozzi con automazione email, workflow multi-dipartimento e dashboard personalizzate.

## 🚀 Quick Start

### 1. Installazione Dipendenze

#### Backend (Python)
```powershell
cd backend
pip install -r requirements.txt
```

#### Frontend (Node.js)
```powershell
cd frontend
npm install
```

### 2. Inizializzazione Database

Crea il database e gli utenti predefiniti:

```powershell
python init_db.py
```

**Credenziali predefinite:**
- **Admin**: `admin` / `admin123`
- **Chiara (Commerciale)**: `chiara` / `chiara123`
- **Fattibilità**: `fattibilita` / `fatti123`
- **Cristian (Tecnico)**: `cristian` / `crist123`
- **Acquisti**: `acquisti` / `acqui123`
- **Pianificazione**: `pianificazione` / `piani123`

⚠️ **IMPORTANTE**: Cambiare queste password in produzione!

### 3. Avvio Applicazione

#### Terminal 1 - Backend
```powershell
cd backend
uvicorn main:app --reload
```
Backend disponibile su: **http://localhost:8000**

#### Terminal 2 - Frontend
```powershell
cd frontend
npm run dev
```
Frontend disponibile su: **http://localhost:5173**

## 📋 Funzionalità Principali

### 🔐 Sistema di Autenticazione
- Login con JWT
- Ruoli: Admin, Commerciale, Fattibilità, Tecnico, Acquisti, Pianificazione
- Permessi basati su ruolo

### 📊 Dashboard Personalizzate
- **Commerciale (Chiara/Cynda)**: Vista completa di tutte le offerte
- **Dipartimenti**: Solo offerte assegnate con priorità e scadenze

### 🔄 Workflow Dinamico
- Chiara definisce il flusso per ogni offerta
- Selezione dipartimenti necessari
- Assegnazione priorità
- Tracking stato per fase

### 💬 Sistema di Comunicazione
- Chat per offerta
- Task assignment
- Note per dipartimento
- Notifiche real-time (in sviluppo)

### 📁 Gestione File
- Upload file per ogni offerta
- Organizzazione automatica in P:\VENDITE\
- Versioning e tracking

### 📈 Statistiche
- Dashboard con metriche in tempo reale
- Statistiche per cliente, dipartimento, periodo
- Report personalizzati

## 🏗️ Architettura

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (dev) / MS SQL Server (prod)
- **Authentication**: JWT con bcrypt
- **API**: REST con 40+ endpoints

### Frontend
- **Framework**: React 18 + Vite
- **Routing**: React Router v6
- **State**: Context API
- **Styling**: Custom CSS con glassmorphism

## 📁 Struttura Progetto

```
M54/
├── backend/
│   ├── main.py              # FastAPI app principale
│   ├── models.py            # Modelli SQLAlchemy
│   ├── schemas.py           # Schemi Pydantic
│   ├── crud.py              # Operazioni database
│   ├── auth.py              # Autenticazione JWT
│   ├── database.py          # Configurazione DB
│   └── requirements.txt     # Dipendenze Python
├── frontend/
│   ├── src/
│   │   ├── components/      # Componenti React
│   │   ├── context/         # Context providers
│   │   ├── services/        # API client
│   │   ├── App.jsx          # App principale
│   │   └── index.css        # Design system
│   ├── package.json
│   └── vite.config.js
├── init_db.py               # Script inizializzazione
└── README.md
```

## 🔧 API Endpoints

### Authentication
- `POST /auth/login` - Login
- `POST /auth/register` - Registrazione (admin only)
- `GET /auth/me` - Utente corrente

### Offers
- `GET /offers/` - Lista offerte (con filtri)
- `GET /offers/my-offers` - Offerte assegnate
- `GET /offers/{id}` - Dettaglio offerta
- `POST /offers/` - Crea offerta
- `PUT /offers/{id}` - Aggiorna offerta

### Workflow
- `POST /offers/{id}/workflow` - Crea workflow
- `GET /offers/{id}/workflow` - Ottieni workflow
- `PUT /workflow/{step_id}` - Aggiorna step

### Files
- `POST /offers/{id}/files` - Upload file
- `GET /offers/{id}/files` - Lista file

### Messages & Notes
- `POST /offers/{id}/messages` - Invia messaggio
- `GET /offers/{id}/messages` - Lista messaggi
- `POST /offers/{id}/notes` - Crea nota
- `GET /offers/{id}/notes` - Lista note

### Dashboard
- `GET /dashboard/stats` - Statistiche

## 🎨 Design System

L'applicazione utilizza un design moderno con:
- **Tema scuro** con palette professionale
- **Glassmorphism** per card e contenitori
- **Gradients** per accenti
- **Animazioni fluide**
- **Responsive** per tutti i dispositivi

## 🔜 Prossimi Sviluppi

- [ ] Integrazione Gmail API per import automatico email
- [ ] WebSocket per notifiche real-time
- [ ] Sistema di chat avanzato
- [ ] Report e statistiche avanzate
- [ ] Export Excel/PDF
- [ ] Mobile app

## 🆘 Supporto

Per problemi o domande:
1. Verificare che Python 3.11+ e Node.js 18+ siano installati
2. Verificare che le porte 8000 e 5173 siano disponibili
3. Controllare i log nei terminali
4. Verificare che il database sia stato inizializzato

## 📝 Note di Sviluppo

- Il sistema usa SQLite in development
- Per production, configurare MS SQL Server in `database.py`
- I file vengono salvati in `uploads/` in dev, `P:\VENDITE\` in prod
- Cambiare `SECRET_KEY` in `auth.py` per production

---

**© 2024 Benozzi - Sistema Gestione Offerte M54 v2.0**
