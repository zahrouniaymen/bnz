from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import os
import sys
from pathlib import Path

# Add project root to sys.path to allow imports from backend. and root scripts
# This handles cases where we run from root, backend/, or elsewhere
current_dir = Path(__file__).resolve().parent
if current_dir.name == 'backend':
    project_root = current_dir.parent
else:
    project_root = current_dir

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import backend.models as models
import backend.schemas as schemas
import backend.crud as crud
import backend.analytics_crud as analytics_crud
import backend.auth as auth
from backend.database import SessionLocal, engine
from backend.auth import (
    authenticate_user, create_access_token, get_current_active_user,
    is_commerciale, is_admin, ACCESS_TOKEN_EXPIRE_MINUTES
)
from backend.email_importer import EmailImporter
from backend.reports import ReportGenerator
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import io

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="M54 Offer Management System",
    description="Sistema completo di gestione offerte Benozzi",
    version="2.0.0"
)

# CORS configuration
origins = ["*"]  # Allow all origins for development to enable LAN access

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= WebSocket Manager =============

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)




# ============= Authentication Endpoints =============

@app.post("/auth/login", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(auth.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """Real login endpoint for getting access token"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@app.get("/auth/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get current authenticated user info"""
    return current_user


# Global variable to store import status
email_import_status = {
    "running": False,
    "last_run": None,
    "stats": None
}

def run_email_import_task():
    """Background task to import emails"""
    global email_import_status
    
    try:
        email_import_status["running"] = True
        email_import_status["stats"] = None
        
        importer = EmailImporter()
        stats = importer.import_offers()
        
        email_import_status["stats"] = stats
        email_import_status["last_run"] = datetime.now().isoformat()
        
    except Exception as e:
        email_import_status["stats"] = {
            "processed": 0,
            "created": 0,
            "errors": 1,
            "error_messages": [str(e)]
        }
    finally:
        email_import_status["running"] = False

@app.post("/offers/import-from-email")
async def import_offers_from_email(
    background_tasks: BackgroundTasks,
    
):
    """Import offers from email (protected)"""
    if email_import_status["running"]:
        raise HTTPException(
            status_code=400,
            detail="Import già in corso"
        )
    background_tasks.add_task(run_email_import_task)
    return {"message": "Import email avviato", "status": "processing"}

@app.get("/offers/import-status")
async def get_email_import_status():
    """Get status of email import"""
    return email_import_status

# ============= Excel Import Endpoints =============
from import_excel_complete import ExcelImporter

@app.post("/import/excel")
async def import_excel_data(
    background_tasks: BackgroundTasks, 
    db: Session = Depends(auth.get_db),
    
):
    """Trigger the Excel import process (protected)"""
    def run_import():
        importer = ExcelImporter()
        importer.run_import()
    
    background_tasks.add_task(run_import)
    return {"message": "Excel import started in background"}




@app.post("/auth/register", response_model=schemas.User)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(is_admin)
):
    """Register a new user (admin only)"""
    # Check if username exists
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return crud.create_user(db, user)





# ============= User Endpoints =============

@app.get("/users/", response_model=List[schemas.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(is_admin)
):
    """Get all users (admin only)"""
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get user by ID"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(is_admin)
):
    """Update user (admin only)"""
    user = crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ============= Client Endpoints =============

@app.post("/clients/", response_model=schemas.Client)
def create_client(
    client: schemas.ClientCreate,
    db: Session = Depends(auth.get_db),
    
):
    """Create a new client"""
    return crud.create_client(db, client)


@app.get("/clients/", response_model=List[schemas.Client])
def read_clients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth.get_db),
    
):
    """Get all clients"""
    return crud.get_clients(db, skip=skip, limit=limit)


@app.get("/clients/{client_id}", response_model=schemas.Client)
def read_client(
    client_id: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get client by ID"""
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.put("/clients/{client_id}", response_model=schemas.Client)
def update_client(
    client_id: int,
    client_update: schemas.ClientUpdate,
    db: Session = Depends(auth.get_db),
    
):
    """Update client"""
    client = crud.update_client(db, client_id, client_update)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.delete("/clients/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(auth.get_db),
    
):
    """Delete a client (commerciale/admin)"""
    success = crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}


# ============= Offer Endpoints =============

@app.post("/offers/", response_model=schemas.Offer)
def create_offer(
    offer: schemas.OfferCreate,
    db: Session = Depends(auth.get_db),
    
):
    """Create a new offer"""
    return crud.create_offer(db, offer)


@app.get("/offers/", response_model=List[schemas.Offer])
def read_offers(
    skip: int = 0,
    limit: int = 10000,
    status: Optional[models.OfferStatus] = None,
    priority: Optional[models.Priority] = None,
    client_id: Optional[int] = None,
    managed_by_id: Optional[int] = None,
    db: Session = Depends(auth.get_db)
):
    """Get offers with optional filters - NO AUTH REQUIRED"""
    return crud.get_offers(db, skip, limit, status, priority, client_id, managed_by_id)


@app.get("/offers/my-offers", response_model=List[schemas.Offer])
def read_my_offers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth.get_db)
):
    """Get offers assigned to current user - FORCED ADMIN ACCESS"""
    return crud.get_offers(db, skip, limit)


@app.get("/offers/{offer_id}", response_model=schemas.Offer)
def read_offer(
    offer_id: int,
    db: Session = Depends(auth.get_db)
):
    """Get offer by ID - NO AUTH REQUIRED"""
    offer = crud.get_offer(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    return offer


@app.put("/offers/{offer_id}", response_model=schemas.Offer)
async def update_offer(
    offer_id: int,
    offer_update: schemas.OfferUpdate,
    db: Session = Depends(auth.get_db)
):
    """Update offer - NO AUTH REQUIRED"""
    offer = crud.get_offer(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    updated_offer = crud.update_offer(db, offer_id, offer_update)
    
    # Broadcast notification
    await manager.broadcast({
        "type": "offer_update",
        "offer_id": offer_id,
        "offer_number": updated_offer.offer_number,
        "status": updated_offer.status,
        "message": f"Offerta {updated_offer.offer_number} aggiornata a {updated_offer.status}"
    })
    
    return updated_offer


# ============= Workflow Endpoints =============

@app.post("/offers/{offer_id}/workflow", response_model=List[schemas.WorkflowStep])
def create_workflow(
    offer_id: int,
    workflow: schemas.WorkflowCreate,
    db: Session = Depends(auth.get_db)
):
    """Create workflow for an offer"""
    offer = crud.get_offer(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    steps = crud.create_workflow_steps(db, offer_id, workflow.steps)
    
    # Update offer status
    crud.update_offer(db, offer_id, schemas.OfferUpdate(status=models.OfferStatus.CHECKS_IN_PROGRESS))
    
    return steps


@app.get("/offers/{offer_id}/workflow", response_model=List[schemas.WorkflowStep])
def read_workflow(
    offer_id: int,
    db: Session = Depends(auth.get_db)
):
    """Get workflow steps for an offer"""
    return crud.get_workflow_steps(db, offer_id)


@app.put("/workflow/{step_id}", response_model=schemas.WorkflowStep)
def update_workflow_step(
    step_id: int,
    step_update: schemas.WorkflowStepUpdate,
    db: Session = Depends(auth.get_db)
):
    """Update a workflow step"""
    step = crud.update_workflow_step(db, step_id, step_update)
    if not step:
        raise HTTPException(status_code=404, detail="Workflow step not found")
    
    # Check if all steps are completed
    if step.status == models.WorkflowStepStatus.COMPLETED:
        all_steps = crud.get_workflow_steps(db, step.offer_id)
        if all(s.status == models.WorkflowStepStatus.COMPLETED for s in all_steps):
            # Update offer status to ready to send
            crud.update_offer(db, step.offer_id, schemas.OfferUpdate(status=models.OfferStatus.READY_TO_SEND))
    
    return step


# ============= File Endpoints =============

@app.post("/offers/{offer_id}/files", response_model=schemas.OfferFile)
async def upload_file(
    offer_id: int,
    file: UploadFile = File(...),
    file_type: str = "attachment",
    db: Session = Depends(auth.get_db)
):
    """Upload a file for an offer - NO AUTH"""
    offer = crud.get_offer(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Create directory structure
    year = offer.created_at.year if offer.created_at else 2024
    client_name = offer.client.name if offer.client else "Unknown"
    upload_dir = f"P:/VENDITE/OFFERTE CLIENTI/{year}/{client_name}/O{offer.offer_number}"
    
    # For development, use local directory
    if not os.path.exists("P:/"):
        upload_dir = f"uploads/{year}/{client_name}/O{offer.offer_number}"
    
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create file record (use admin ID 1 as default)
    file_data = schemas.OfferFileCreate(
        offer_id=offer_id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=len(content),
        mime_type=file.content_type,
        uploaded_by_id=1 
    )
    
    return crud.create_offer_file(db, file_data)


@app.get("/offers/{offer_id}/files", response_model=List[schemas.OfferFile])
def read_offer_files(
    offer_id: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get all files for an offer"""
    return crud.get_offer_files(db, offer_id)


# ============= Message Endpoints =============

@app.post("/offers/{offer_id}/messages", response_model=schemas.OfferMessage)
def create_message(
    offer_id: int,
    message: schemas.OfferMessageBase,
    db: Session = Depends(auth.get_db)
):
    """Create a message for an offer - NO AUTH"""
    message_data = schemas.OfferMessageCreate(
        offer_id=offer_id,
        user_id=1,
        **message.model_dump()
    )
    return crud.create_message(db, message_data)


@app.get("/offers/{offer_id}/messages", response_model=List[schemas.OfferMessage])
def read_messages(
    offer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(auth.get_db)
):
    """Get messages for an offer - NO AUTH"""
    messages = crud.get_offer_messages(db, offer_id, skip, limit)
    # Mark as read (use admin ID 1 as default)
    crud.mark_messages_as_read(db, offer_id, 1)
    return messages


# ============= Note Endpoints =============

@app.post("/offers/{offer_id}/notes", response_model=schemas.OfferNote)
def create_note(
    offer_id: int,
    note: schemas.OfferNoteBase,
    db: Session = Depends(auth.get_db)
):
    """Create a note for an offer - NO AUTH"""
    note_data = schemas.OfferNoteCreate(
        offer_id=offer_id,
        created_by_id=1,
        **note.model_dump()
    )
    return crud.create_note(db, note_data)


@app.get("/offers/{offer_id}/notes", response_model=List[schemas.OfferNote])
def read_notes(
    offer_id: int,
    department: Optional[str] = None,
    db: Session = Depends(auth.get_db),
    
):
    """Get notes for an offer"""
    return crud.get_offer_notes(db, offer_id, department)


@app.put("/notes/{note_id}", response_model=schemas.OfferNote)
def update_note(
    note_id: int,
    note_update: schemas.OfferNoteUpdate,
    db: Session = Depends(auth.get_db),
    
):
    """Update a note"""
    note = crud.update_note(db, note_id, note_update)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


# ============= Analytics Endpoints =============
# Endpoints used by Analytics.jsx

@app.get("/analytics/monthly-evolution/{year}", response_model=List[schemas.MonthlyEvolution])
def get_monthly_evolution(
    year: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get monthly evolution stats"""
    return analytics_crud.get_monthly_evolution(db, year)


@app.get("/analytics/reasons/{year}", response_model=schemas.ReasonsAnalysis)
def get_reasons_stats(
    year: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get declined/not accepted reasons stats"""
    return analytics_crud.get_reasons_stats(db, year)


@app.get("/analytics/client-ranking/{year}", response_model=List[schemas.ClientRanking])
def get_client_ranking(year: int, db: Session = Depends(auth.get_db)):
    return analytics_crud.get_client_ranking(db, year)


@app.get("/analytics/sector-distribution/{year}")
def get_sector_distribution(year: int, db: Session = Depends(auth.get_db)):
    return analytics_crud.get_sector_distribution(db, year)


@app.get("/analytics/item-mix/{year}")
def get_new_vs_reorder_stats(year: int, db: Session = Depends(auth.get_db)):
    return analytics_crud.get_new_vs_reorder_stats(db, year)


@app.get("/analytics/comparison", response_model=dict)
def get_comparison_data(
    years: str = "2024,2025",
    db: Session = Depends(auth.get_db),
    
):
    """Get comparison stats for multiple years (comma separated)"""
    year_list = [int(y) for y in years.split(',') if y.isdigit()]
    return analytics_crud.get_comparison_data(db, year_list)


@app.get("/analytics/export/excel/{year}")
def export_excel_report(
    year: int,
    db: Session = Depends(auth.get_db),
    
):
    """Export analytics to Excel"""
    generator = ReportGenerator(db)
    file_handle = generator.generate_excel_analytics(year)
    return StreamingResponse(
        file_handle,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=Report_M54_{year}.xlsx"}
    )


@app.get("/analytics/export/pdf/{year}")
def export_pdf_report(
    year: int,
    db: Session = Depends(auth.get_db),
    
):
    """Export analytics to PDF"""
    generator = ReportGenerator(db)
    file_handle = generator.generate_pdf_summary(year)
    return StreamingResponse(
        file_handle,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Report_M54_{year}.pdf"}
    )


# ============= Dashboard Endpoints =============

@app.get("/dashboard/stats", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    year: Optional[int] = None,
    db: Session = Depends(auth.get_db)
):
    """Get dashboard statistics - NO AUTH"""
    return crud.get_dashboard_stats(db, None, None, year)


# ============= New Analytics Endpoints =============

@app.get("/analytics/user-performance/{user_id}")
def get_user_performance_endpoint(
    user_id: int,
    period: str = Query(..., description="Period in format YYYY-MM"),
    db: Session = Depends(auth.get_db),
    
):
    """Get performance metrics for a specific user"""
    from backend import analytics_enrichment
    metrics = analytics_enrichment.get_user_performance(db, user_id, period)
    if not metrics:
        raise HTTPException(status_code=404, detail="No metrics found for this period")
    return metrics


@app.get("/analytics/team-performance")
def get_team_performance_endpoint(
    period: str = Query(..., description="Period in format YYYY-MM"),
    db: Session = Depends(auth.get_db),
    
):
    """Get performance metrics for all team members"""
    from backend import analytics_enrichment
    return analytics_enrichment.get_team_performance(db, period)


@app.get("/analytics/workflow-timing/{year}")
def get_workflow_timing_endpoint(
    year: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get workflow timing statistics by phase"""
    from backend import analytics_enrichment
    return analytics_enrichment.calculate_workflow_timing_stats(db, year)


@app.get("/analytics/bottlenecks")
def get_bottlenecks_endpoint(
    threshold_hours: float = Query(48, description="Alert threshold in hours"),
    db: Session = Depends(auth.get_db),
    
):
    """Get alerts for stuck offers in workflow"""
    from backend import analytics_enrichment
    return analytics_enrichment.get_bottleneck_alerts(db, threshold_hours)


@app.get("/analytics/seasonal-trends/{year}")
def get_seasonal_trends_endpoint(
    year: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get seasonal trends and monthly patterns"""
    from backend import analytics_enrichment
    return analytics_enrichment.calculate_seasonal_trends(db, year)


@app.get("/analytics/client-loyalty/{year}")
def get_client_loyalty_endpoint(
    year: int,
    db: Session = Depends(auth.get_db),
    
):
    """Get client loyalty metrics"""
    from backend import analytics_enrichment
    return analytics_enrichment.calculate_client_loyalty(db, year)


# ============= Health Check =============

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}
