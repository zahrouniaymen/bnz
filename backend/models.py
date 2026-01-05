from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMMERCIALE = "commerciale"
    FATTIBILITA = "fattibilita"
    TECNICO = "tecnico"
    ACQUISTI = "acquisti"
    PIANIFICAZIONE = "pianificazione"


class OfferStatus(str, enum.Enum):
    PENDING_REGISTRATION = "PENDING_REGISTRATION"
    IN_LAVORO = "IN_LAVORO"
    CHECKS_IN_PROGRESS = "CHECKS_IN_PROGRESS"
    READY_TO_SEND = "READY_TO_SEND"
    SENT = "SENT"
    ACCETTATA = "ACCETTATA"
    DECLINATA = "DECLINATA"
    NON_ACCETTATA = "NON_ACCETTATA"


class CheckStatus(str, enum.Enum):
    DA_ESAMINARE = "Da esaminare"
    OK = "OK"
    KO = "KO"


class Priority(str, enum.Enum):
    BASSA = "bassa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"


class DeclinedReason(str, enum.Enum):
    ARTICOLO_NON_FATTIBILE = "ARTICOLO NON FATTIBILE"
    TEMPI_CONSEGNA = "TEMPI DI CONSEGNA"
    SOVRACCARICO_PRODUTTIVO = "SOVRACCARICO PRODUTTIVO"
    QUANTITA_ALTE = "QUANTITÀ ALTE"
    QUANTITA_BASSE = "QUANTITÀ BASSE"
    CLIENTE_NON_STRATEGICO = "CLIENTE NON STRATEGICO"
    COMPONENTE_NON_STRATEGICO = "COMPONENTE NON STRATEGICO"
    TARGET_BASSO = "TARGET BASSO"


class ProductionType(str, enum.Enum):
    MACCHINE = "macchine"
    OUTSOURCING = "outsourcing"
    MISTO = "misto"


class WorkflowStepStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class MessageType(str, enum.Enum):
    CHAT = "chat"
    TASK = "task"
    NOTE = "note"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    department = Column(String(100))
    full_name = Column(String(255))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    managed_offers = relationship("Offer", foreign_keys="Offer.managed_by_id", back_populates="manager")
    purchasing_offers = relationship("Offer", foreign_keys="Offer.purchasing_manager_id", back_populates="purchasing_manager")
    workflow_steps = relationship("WorkflowStep", back_populates="assigned_user")
    messages = relationship("OfferMessage", back_populates="user")
    uploaded_files = relationship("OfferFile", back_populates="uploader")
    created_notes = relationship("OfferNote", back_populates="creator")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    email_domain = Column(String(255), unique=True, index=True)
    sector = Column(String(255))
    management_time = Column(Integer)
    strategic = Column(Boolean, default=False)
    voto = Column(Integer)  # Client score/rating (1-10)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    offers = relationship("Offer", back_populates="client")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    offer_number = Column(String(50), unique=True, index=True, nullable=False)
    article_progressive = Column(String(50))
    month = Column(String(20))
    mail_date = Column(DateTime)
    
    # Client
    client_id = Column(Integer, ForeignKey("clients.id"))
    
    # Offer details
    offer_type = Column(String(100))
    offer_expiry = Column(DateTime)
    status = Column(String(50), default="PENDING_REGISTRATION", index=True)
    priority = Column(String(50), default="media")
    production_type = Column(String(50))
    is_new_item = Column(Boolean, default=True)  # True if Nuovo, False if Riordine
    
    # Checks
    check_feasibility = Column(String(50), default="Da esaminare")
    check_technical = Column(String(50), default="Da esaminare")
    check_purchasing = Column(String(50), default="Da esaminare")
    check_planning = Column(String(50), default="Da esaminare")
    
    # Item info
    item_name = Column(Text)
    email_subject = Column(Text)
    
    # Management
    managed_by_id = Column(Integer, ForeignKey("users.id"))
    purchasing_manager_id = Column(Integer, ForeignKey("users.id"))
    managed_by_name = Column(String(255))
    purchasing_manager_name = Column(String(255))
    
    # Timing
    commercial_lead_time = Column(String(100))
    reply_deadline = Column(DateTime)
    planning_lead_time = Column(String(100))
    offer_sent_date = Column(DateTime)
    confirmed_lead_time = Column(String(100))
    
    # Financial
    offer_amount = Column(Float, default=0.0)
    order_date = Column(DateTime)
    order_amount = Column(Float, default=0.0)
    
    # Declined info
    declined_reason = Column(SQLEnum(DeclinedReason))
    declined_notes = Column(Text)
    not_accepted_reason = Column(Text)
    
    # Statistics
    week_stats = Column(Integer)
    month_stats = Column(String(20))
    year_stats = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    client = relationship("Client", back_populates="offers")
    manager = relationship("User", foreign_keys=[managed_by_id], back_populates="managed_offers")
    purchasing_manager = relationship("User", foreign_keys=[purchasing_manager_id], back_populates="purchasing_offers")
    workflow_steps = relationship("WorkflowStep", back_populates="offer", cascade="all, delete-orphan")
    files = relationship("OfferFile", back_populates="offer", cascade="all, delete-orphan")
    messages = relationship("OfferMessage", back_populates="offer", cascade="all, delete-orphan")
    notes = relationship("OfferNote", back_populates="offer", cascade="all, delete-orphan")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    department = Column(String(100), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default="pending")
    order_index = Column(Integer, nullable=False)
    
    # Timing
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    deadline = Column(DateTime)
    estimated_completion = Column(DateTime)
    actual_duration_minutes = Column(Float)
    bottleneck_flag = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    offer = relationship("Offer", back_populates="workflow_steps")
    assigned_user = relationship("User", back_populates="workflow_steps")


class OfferFile(Base):
    __tablename__ = "offer_files"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))  # email, attachment, preventivo, response, drawing, etc.
    file_size = Column(Integer)
    mime_type = Column(String(100))
    uploaded_by_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    offer = relationship("Offer", back_populates="files")
    uploader = relationship("User", back_populates="uploaded_files")


class OfferMessage(Base):
    __tablename__ = "offer_messages"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_type = Column(String(50), default="chat")
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    parent_message_id = Column(Integer, ForeignKey("offer_messages.id"))  # For replies
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    offer = relationship("Offer", back_populates="messages")
    user = relationship("User", back_populates="messages")


class OfferNote(Base):
    __tablename__ = "offer_notes"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    department = Column(String(100), nullable=False)  # commerciale, tecnico, acquisti, pianificazione
    content = Column(Text, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    offer = relationship("Offer", back_populates="notes")
    creator = relationship("User", back_populates="created_notes")


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, unique=True, index=True, nullable=False)
    description = Column(String(255))
    is_recurring = Column(Boolean, default=True)  # True for fixed dates like Dec 25
    created_at = Column(DateTime, default=datetime.utcnow)
# Add this to the end of backend/models.py after the Holiday model

class UserPerformanceMetrics(Base):
    """Track user performance metrics over time"""
    __tablename__ = "user_performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period = Column(String(7), nullable=False)  # Format: "2024-01", "2024-02", etc.
    
    # Performance metrics
    offers_handled = Column(Integer, default=0)
    avg_processing_time_hours = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)  # Percentage of successful offers
    current_workload = Column(Integer, default=0)  # Active offers assigned
    
    # Timing metrics
    avg_response_time_hours = Column(Float, default=0.0)
    total_hours_worked = Column(Float, default=0.0)
    
    # Quality metrics
    declined_count = Column(Integer, default=0)
    accepted_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
