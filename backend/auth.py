from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import backend.models as models
import backend.schemas as schemas
from backend.database import SessionLocal

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production-use-openssl-rand-hex-32"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user"""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    if not user.active:
        return False
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current authenticated user - SUPPORTS AUTO-ADMIN SESSION"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # SPECIAL CASE: Bypass for auto-admin session
    if token == "auto-admin-session":
        admin = db.query(models.User).filter(models.User.role == models.UserRole.ADMIN).first()
        if admin:
            return admin
        # If no admin exists, just return the first active user
        return db.query(models.User).filter(models.User.active == True).first()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    """Ensure the current user is active"""
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Role-based permission checks
def require_role(*allowed_roles: models.UserRole):
    """Decorator to require specific roles"""
    def role_checker(current_user: models.User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


def is_commerciale(current_user: models.User = Depends(get_current_active_user)):
    """Check if user is commerciale"""
    if str(current_user.role).lower() not in ["commerciale", "admin"]:
        raise HTTPException(status_code=403, detail="Only commerciale can perform this action")
    return current_user


def is_admin(current_user: models.User = Depends(get_current_active_user)):
    """Check if user is admin"""
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def can_edit_offer(offer: models.Offer, current_user: models.User):
    """Check if user can edit an offer"""
    # Admin and commerciale can always edit
    if str(current_user.role).lower() in ["admin", "commerciale"]:
        return True
    
    # Department users can edit if they have a workflow step assigned
    workflow_step = next(
        (step for step in offer.workflow_steps if step.assigned_to_id == current_user.id),
        None
    )
    if workflow_step and workflow_step.status in [models.WorkflowStepStatus.PENDING, models.WorkflowStepStatus.IN_PROGRESS]:
        return True
    
    return False
