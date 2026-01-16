"""User Management API Routes

Handles user registration, authentication, and profile management.
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, validator
import os

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

router = APIRouter(prefix="/api/users", tags=["users"])

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('username')
    def username_validation(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    total_points: int
    modules_completed: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Database dependency (to be implemented based on your database setup)
def get_db():
    """
    Database session dependency.
    Replace with your actual database session logic.
    """
    # Example:
    # from backend.database import SessionLocal
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    pass

# Utility Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str):
    """Get user by email from database."""
    # Implement based on your User model
    # Example:
    # from backend.models import User
    # return db.query(User).filter(User.email == email).first()
    pass

def get_user_by_username(db: Session, username: str):
    """Get user by username from database."""
    # Implement based on your User model
    pass

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID from database."""
    # Implement based on your User model
    pass

def create_user(db: Session, user: UserCreate):
    """Create a new user in database."""
    # Implement based on your User model
    # Example:
    # from backend.models import User
    # hashed_password = get_password_hash(user.password)
    # db_user = User(
    #     email=user.email,
    #     username=user.username,
    #     full_name=user.full_name,
    #     hashed_password=hashed_password
    # )
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)
    # return db_user
    pass

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# API Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **username**: Unique username (alphanumeric, min 3 characters)
    - **password**: Strong password (min 8 characters)
    - **full_name**: Optional full name
    """
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    new_user = create_user(db=db, user=user)
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login with username/email and password.
    Returns JWT access token.
    """
    # Try to find user by username or email
    user = get_user_by_username(db, username=form_data.username)
    if not user:
        user = get_user_by_email(db, email=form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user = Depends(get_current_active_user)):
    """
    Get current user's profile.
    Requires authentication.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    - **full_name**: Update full name
    - **email**: Update email address
    - **current_password**: Required for password change
    - **new_password**: New password (if changing password)
    """
    # Update full name
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    # Update email
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = get_user_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = user_update.email
    
    # Update password
    if user_update.new_password:
        if not user_update.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password required to set new password"
            )
        
        if not verify_password(user_update.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect current password"
            )
        
        if len(user_update.new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long"
            )
        
        current_user.hashed_password = get_password_hash(user_update.new_password)
    
    # Save changes
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete current user's account.
    This action is irreversible.
    """
    # Soft delete by deactivating
    current_user.is_active = False
    db.commit()
    
    # Or hard delete:
    # db.delete(current_user)
    # db.commit()
    
    return None

@router.get("/stats", response_model=dict)
async def get_user_stats(current_user = Depends(get_current_active_user)):
    """
    Get current user's learning statistics.
    """
    return {
        "user_id": current_user.id,
        "total_points": current_user.total_points,
        "modules_completed": current_user.modules_completed,
        "member_since": current_user.created_at,
        "badges_earned": [],  # Implement based on your badge system
        "current_streak": 0,  # Implement streak tracking
    }
