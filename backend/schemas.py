from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from backend.models import (
    UserRole, OfferStatus, CheckStatus, Priority, 
    DeclinedReason, ProductionType, WorkflowStepStatus, MessageType
)


# ============= User Schemas =============

class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole
    department: Optional[str] = None
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    department: Optional[str] = None
    full_name: Optional[str] = None
    active: Optional[bool] = None


class User(UserBase):
    id: int
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


# ============= Client Schemas =============

class ClientBase(BaseModel):
    name: str
    email_domain: Optional[str] = None
    sector: Optional[str] = None
    management_time: Optional[int] = None
    strategic: bool = False
    voto: Optional[int] = None
    notes: Optional[str] = None
    # Analytics fields
    new_items_count: int = 0
    reorder_count: int = 0
    loyalty_score: float = 0.0


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email_domain: Optional[str] = None
    sector: Optional[str] = None
    management_time: Optional[int] = None
    strategic: Optional[bool] = None
    voto: Optional[int] = None
    notes: Optional[str] = None
    new_items_count: Optional[int] = None
    reorder_count: Optional[int] = None
    loyalty_score: Optional[float] = None


class Client(ClientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= Offer Schemas =============

class OfferBase(BaseModel):
    offer_number: Optional[str] = None
    article_progressive: Optional[str] = None
    month: Optional[str] = None
    mail_date: Optional[datetime] = None
    client_id: Optional[int] = None
    offer_type: Optional[str] = None
    offer_expiry: Optional[datetime] = None
    status: Optional[OfferStatus] = OfferStatus.PENDING_REGISTRATION
    priority: Optional[Priority] = Priority.MEDIA
    production_type: Optional[ProductionType] = None
    is_new_item: Optional[bool] = True
    check_feasibility: Optional[CheckStatus] = CheckStatus.DA_ESAMINARE
    check_technical: Optional[CheckStatus] = CheckStatus.DA_ESAMINARE
    check_purchasing: Optional[CheckStatus] = CheckStatus.DA_ESAMINARE
    check_planning: Optional[CheckStatus] = CheckStatus.DA_ESAMINARE
    item_name: Optional[str] = None
    email_subject: Optional[str] = None
    managed_by_id: Optional[int] = None
    purchasing_manager_id: Optional[int] = None
    commercial_lead_time: Optional[str] = None
    reply_deadline: Optional[datetime] = None
    planning_lead_time: Optional[str] = None
    offer_sent_date: Optional[datetime] = None
    confirmed_lead_time: Optional[str] = None
    offer_amount: Optional[float] = 0.0
    order_date: Optional[datetime] = None
    order_amount: Optional[float] = 0.0
    declined_reason: Optional[DeclinedReason] = None
    declined_notes: Optional[str] = None
    managed_by_name: Optional[str] = None
    purchasing_manager_name: Optional[str] = None
    year_stats: Optional[int] = None
    not_accepted_reason: Optional[str] = None


class OfferCreate(OfferBase):
    pass


class OfferUpdate(BaseModel):
    article_progressive: Optional[str] = None
    month: Optional[str] = None
    mail_date: Optional[datetime] = None
    client_id: Optional[int] = None
    offer_type: Optional[str] = None
    offer_expiry: Optional[datetime] = None
    status: Optional[OfferStatus] = None
    priority: Optional[Priority] = None
    production_type: Optional[ProductionType] = None
    is_new_item: Optional[bool] = None
    check_feasibility: Optional[CheckStatus] = None
    check_technical: Optional[CheckStatus] = None
    check_purchasing: Optional[CheckStatus] = None
    check_planning: Optional[CheckStatus] = None
    item_name: Optional[str] = None
    email_subject: Optional[str] = None
    managed_by_id: Optional[int] = None
    purchasing_manager_id: Optional[int] = None
    commercial_lead_time: Optional[str] = None
    reply_deadline: Optional[datetime] = None
    planning_lead_time: Optional[str] = None
    offer_sent_date: Optional[datetime] = None
    confirmed_lead_time: Optional[str] = None
    offer_amount: Optional[float] = None
    order_date: Optional[datetime] = None
    order_amount: Optional[float] = None
    declined_reason: Optional[DeclinedReason] = None
    declined_notes: Optional[str] = None
    not_accepted_reason: Optional[str] = None


class Offer(OfferBase):
    id: int
    created_at: datetime
    updated_at: datetime
    client: Optional[Client] = None
    manager: Optional[User] = None
    purchasing_manager: Optional[User] = None

    class Config:
        from_attributes = True


# ============= Workflow Schemas =============

class WorkflowStepBase(BaseModel):
    department: str
    assigned_to_id: Optional[int] = None
    order_index: int
    deadline: Optional[datetime] = None
    notes: Optional[str] = None


class WorkflowStepCreate(WorkflowStepBase):
    offer_id: int


class WorkflowStepUpdate(BaseModel):
    status: Optional[WorkflowStepStatus] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    notes: Optional[str] = None


class WorkflowStep(WorkflowStepBase):
    id: int
    offer_id: int
    status: WorkflowStepStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    assigned_user: Optional[User] = None

    class Config:
        from_attributes = True


class WorkflowCreate(BaseModel):
    steps: List[WorkflowStepBase]


# ============= File Schemas =============

class OfferFileBase(BaseModel):
    filename: str
    file_path: str
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class OfferFileCreate(OfferFileBase):
    offer_id: int
    uploaded_by_id: int


class OfferFile(OfferFileBase):
    id: int
    offer_id: int
    uploaded_by_id: int
    uploaded_at: datetime
    uploader: Optional[User] = None

    class Config:
        from_attributes = True


# ============= Message Schemas =============

class OfferMessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.CHAT
    parent_message_id: Optional[int] = None


class OfferMessageCreate(OfferMessageBase):
    offer_id: int
    user_id: int


class OfferMessage(OfferMessageBase):
    id: int
    offer_id: int
    user_id: int
    is_read: bool
    created_at: datetime
    user: Optional[User] = None

    class Config:
        from_attributes = True


# ============= Note Schemas =============

class OfferNoteBase(BaseModel):
    department: str
    content: str


class OfferNoteCreate(OfferNoteBase):
    offer_id: int
    created_by_id: int


class OfferNoteUpdate(BaseModel):
    content: str


class OfferNote(OfferNoteBase):
    id: int
    offer_id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime
    creator: Optional[User] = None

    class Config:
        from_attributes = True


# ============= Analytics Schemas =============

class MonthlyEvolution(BaseModel):
    month: str
    year: int
    requests: int = 0
    proposed: int = 0
    accepted: int = 0
    declined: int = 0
    total_value: float = 0.0
    order_value: float = 0.0


class ReasonStat(BaseModel):
    reason: str
    count: int
    percentage: float


class ReasonsAnalysis(BaseModel):
    declined_reasons: List[ReasonStat]
    not_accepted_reasons: List[ReasonStat]


class ClientRanking(BaseModel):
    client_name: str
    requests: int
    proposed: int
    accepted: int
    declined: int
    not_accepted: int
    total_value: float
    success_rate: float


# ============= Dashboard Schemas =============

class DashboardStats(BaseModel):
    total_offers: int
    pending_registration: int
    in_progress: int
    ready_to_send: int
    sent: int
    accepted: int
    declined: int
    total_value: float
    monthly_stats: dict
    by_client: dict
    by_department: dict
    by_year: dict


class OfferFilters(BaseModel):
    status: Optional[OfferStatus] = None
    priority: Optional[Priority] = None
    client_id: Optional[int] = None
    managed_by_id: Optional[int] = None
    department: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# ============= Holiday Schemas =============

class HolidayBase(BaseModel):
    date: datetime
    description: Optional[str] = None
    is_recurring: bool = True


class HolidayCreate(HolidayBase):
    pass


class Holiday(HolidayBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
# Add these schemas to the end of backend/schemas.py

# ============= User Performance Schemas =============

class UserPerformanceMetrics(BaseModel):
    user_id: int
    period: str  # "2024-01", "2024-02", etc.
    offers_handled: int = 0
    avg_processing_time_hours: float = 0.0
    success_rate: float = 0.0
    current_workload: int = 0
    avg_response_time_hours: float = 0.0
    total_hours_worked: float = 0.0
    declined_count: int = 0
    accepted_count: int = 0
    
    class Config:
        from_attributes = True


class TeamPerformanceSummary(BaseModel):
    period: str
    team_members: List[UserPerformanceMetrics]
    total_offers: int
    avg_success_rate: float
    total_workload: int


# ============= Workflow Timing Schemas =============

class WorkflowTimingStats(BaseModel):
    phase: str
    avg_duration_hours: float
    min_duration_hours: float
    max_duration_hours: float
    bottleneck_count: int
    total_steps: int


class BottleneckAlert(BaseModel):
    offer_id: int
    offer_number: str
    client_name: str
    phase: str
    duration_hours: float
    threshold_hours: float
    assigned_user: Optional[str] = None


# ============= Seasonal Trends Schemas =============

class MonthlyTrend(BaseModel):
    month: str  # "2024-01"
    total_offers: int
    accepted: int
    declined: int
    avg_value: float
    prediction_next_month: Optional[int] = None


class SeasonalPattern(BaseModel):
    month_number: int  # 1-12
    avg_volume: float
    peak_indicator: bool
    year_over_year_change: Optional[float] = None


# ============= Client Loyalty Schemas =============

class ClientLoyaltyMetrics(BaseModel):
    client_id: int
    client_name: str
    loyalty_score: float
    new_items_count: int
    reorder_count: int
    total_offers: int
    reorder_percentage: float
    last_order_date: Optional[datetime] = None
