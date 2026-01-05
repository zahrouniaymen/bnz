from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import backend.models as models
import backend.schemas as schemas
from backend.auth import get_password_hash


# ============= User CRUD =============

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        department=user.department,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Get all users"""
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
    """Update a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


# ============= Client CRUD =============

def create_client(db: Session, client: schemas.ClientCreate) -> models.Client:
    """Create a new client"""
    db_client = models.Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_client(db: Session, client_id: int) -> Optional[models.Client]:
    """Get client by ID"""
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def get_client_by_domain(db: Session, email_domain: str) -> Optional[models.Client]:
    """Get client by email domain"""
    return db.query(models.Client).filter(models.Client.email_domain == email_domain).first()


def get_clients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Client]:
    """Get all clients"""
    return db.query(models.Client).offset(skip).limit(limit).all()


def update_client(db: Session, client_id: int, client_update: schemas.ClientUpdate) -> Optional[models.Client]:
    """Update a client"""
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    update_data = client_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_client, field, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> bool:
    """Delete a client"""
    db_client = get_client(db, client_id)
    if not db_client:
        return False
    
    db.delete(db_client)
    db.commit()
    return True


# ============= Offer CRUD =============

def generate_offer_number(db: Session, year: int = None) -> str:
    """Generate next offer number"""
    if year is None:
        year = datetime.now().year
    
    # Get last offer number for this year
    last_offer = db.query(models.Offer).filter(
        models.Offer.offer_number.like(f"{year}%")
    ).order_by(models.Offer.offer_number.desc()).first()
    
    if last_offer:
        try:
            last_num = int(last_offer.offer_number.split('-')[1])
            next_num = last_num + 1
        except:
            next_num = 1
    else:
        next_num = 1
    
    return f"{year}-{next_num:04d}"


def create_offer(db: Session, offer: schemas.OfferCreate) -> models.Offer:
    """Create a new offer"""
    # Generate offer number if not provided
    if not offer.offer_number:
        offer.offer_number = generate_offer_number(db)
    
    db_offer = models.Offer(**offer.model_dump())
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    return db_offer


def get_offer(db: Session, offer_id: int) -> Optional[models.Offer]:
    """Get offer by ID"""
    return db.query(models.Offer).filter(models.Offer.id == offer_id).first()


def get_offers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[models.OfferStatus] = None,
    priority: Optional[models.Priority] = None,
    client_id: Optional[int] = None,
    managed_by_id: Optional[int] = None
) -> List[models.Offer]:
    """Get offers with optional filters"""
    query = db.query(models.Offer)
    
    if status:
        query = query.filter(models.Offer.status == status)
    if priority:
        query = query.filter(models.Offer.priority == priority)
    if client_id:
        query = query.filter(models.Offer.client_id == client_id)
    if managed_by_id:
        query = query.filter(models.Offer.managed_by_id == managed_by_id)
    
    return query.order_by(models.Offer.created_at.desc()).offset(skip).limit(limit).all()


def get_offers_for_department(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[models.Offer]:
    """Get offers assigned to a specific user through workflow steps"""
    # Get offers where user has an active workflow step
    offers = db.query(models.Offer).join(models.WorkflowStep).filter(
        models.WorkflowStep.assigned_to_id == user_id,
        models.WorkflowStep.status.in_([models.WorkflowStepStatus.PENDING, models.WorkflowStepStatus.IN_PROGRESS])
    ).order_by(models.Offer.priority.desc(), models.WorkflowStep.deadline).offset(skip).limit(limit).all()
    
    return offers


def update_offer(db: Session, offer_id: int, offer_update: schemas.OfferUpdate) -> Optional[models.Offer]:
    """Update an offer"""
    db_offer = get_offer(db, offer_id)
    if not db_offer:
        return None
    
    update_data = offer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_offer, field, value)
    
    db_offer.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_offer)
    return db_offer


# ============= Workflow CRUD =============

def create_workflow_steps(db: Session, offer_id: int, steps: List[schemas.WorkflowStepBase]) -> List[models.WorkflowStep]:
    """Create workflow steps for an offer"""
    db_steps = []
    for step_data in steps:
        db_step = models.WorkflowStep(
            offer_id=offer_id,
            **step_data.model_dump()
        )
        db.add(db_step)
        db_steps.append(db_step)
    
    db.commit()
    for step in db_steps:
        db.refresh(step)
    
    return db_steps


def get_workflow_steps(db: Session, offer_id: int) -> List[models.WorkflowStep]:
    """Get all workflow steps for an offer"""
    return db.query(models.WorkflowStep).filter(
        models.WorkflowStep.offer_id == offer_id
    ).order_by(models.WorkflowStep.order_index).all()


def update_workflow_step(db: Session, step_id: int, step_update: schemas.WorkflowStepUpdate) -> Optional[models.WorkflowStep]:
    """Update a workflow step"""
    db_step = db.query(models.WorkflowStep).filter(models.WorkflowStep.id == step_id).first()
    if not db_step:
        return None
    
    update_data = step_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_step, field, value)
    
    db_step.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_step)
    return db_step


# ============= File CRUD =============

def create_offer_file(db: Session, file_data: schemas.OfferFileCreate) -> models.OfferFile:
    """Create a file record"""
    db_file = models.OfferFile(**file_data.model_dump())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_offer_files(db: Session, offer_id: int) -> List[models.OfferFile]:
    """Get all files for an offer"""
    return db.query(models.OfferFile).filter(
        models.OfferFile.offer_id == offer_id
    ).order_by(models.OfferFile.uploaded_at.desc()).all()


# ============= Message CRUD =============

def create_message(db: Session, message: schemas.OfferMessageCreate) -> models.OfferMessage:
    """Create a message"""
    db_message = models.OfferMessage(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_offer_messages(db: Session, offer_id: int, skip: int = 0, limit: int = 100) -> List[models.OfferMessage]:
    """Get messages for an offer"""
    return db.query(models.OfferMessage).filter(
        models.OfferMessage.offer_id == offer_id
    ).order_by(models.OfferMessage.created_at).offset(skip).limit(limit).all()


def mark_messages_as_read(db: Session, offer_id: int, user_id: int):
    """Mark all messages as read for a user"""
    db.query(models.OfferMessage).filter(
        models.OfferMessage.offer_id == offer_id,
        models.OfferMessage.user_id != user_id,
        models.OfferMessage.is_read == False
    ).update({"is_read": True})
    db.commit()


# ============= Note CRUD =============

def create_note(db: Session, note: schemas.OfferNoteCreate) -> models.OfferNote:
    """Create a note"""
    db_note = models.OfferNote(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_offer_notes(db: Session, offer_id: int, department: Optional[str] = None) -> List[models.OfferNote]:
    """Get notes for an offer, optionally filtered by department"""
    query = db.query(models.OfferNote).filter(models.OfferNote.offer_id == offer_id)
    
    if department:
        query = query.filter(models.OfferNote.department == department)
    
    return query.order_by(models.OfferNote.created_at.desc()).all()


def update_note(db: Session, note_id: int, note_update: schemas.OfferNoteUpdate) -> Optional[models.OfferNote]:
    """Update a note"""
    db_note = db.query(models.OfferNote).filter(models.OfferNote.id == note_id).first()
    if not db_note:
        return None
    
    db_note.content = note_update.content
    db_note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_note)
    return db_note


# ============= Statistics =============

def get_dashboard_stats(db: Session, user_role: models.UserRole = None, user_id: int = None, year: int = None) -> dict:
    """Get dashboard statistics"""
    stats = {
        "total_offers": 0,
        "pending_registration": 0,
        "in_progress": 0,
        "ready_to_send": 0,
        "sent": 0,
        "accepted": 0,
        "declined": 0,
        "total_value": 0.0,
        "monthly_stats": {},
        "by_client": {},
        "by_department": {},
        "by_year": {}
    }
    
    # Base query
    query = db.query(models.Offer)
    
    # Filter by user role
    role_str = str(user_role).lower() if user_role else None
    if role_str and role_str not in ["admin", "commerciale"]:
        # Department users see only their assigned offers
        query = query.join(models.WorkflowStep).filter(models.WorkflowStep.assigned_to_id == user_id)
    
    # Filter by year if provided
    if year:
        query = query.filter(models.Offer.year_stats == year)
    
    offers = query.all()
    
    stats["total_offers"] = len(offers)
    
    for offer in offers:
        # Count by year
        offer_year = str(offer.year_stats) if offer.year_stats else "N/A"
        stats["by_year"][offer_year] = stats["by_year"].get(offer_year, 0) + 1
        # Count by status
        status_str = str(offer.status).upper() if offer.status else ""
        if status_str == "PENDING_REGISTRATION":
            stats["pending_registration"] += 1
        elif status_str in ["IN_LAVORO", "CHECKS_IN_PROGRESS"]:
            stats["in_progress"] += 1
        elif status_str == "READY_TO_SEND":
            stats["ready_to_send"] += 1
        elif status_str == "SENT":
            stats["sent"] += 1
        elif status_str == "ACCETTATA":
            stats["accepted"] += 1
        elif status_str == "DECLINATA":
            stats["declined"] += 1
        elif status_str == "NON_ACCETTATA":
            stats["declined"] += 1
        
        # Total value
        if offer.offer_amount:
            stats["total_value"] += offer.offer_amount
    
    return stats
