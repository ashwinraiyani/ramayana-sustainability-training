"""Authentication and Authorization Module

This module provides authentication utilities including password hashing,
JWT token creation/verification, and user authentication dependencies.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
# from models import User  # Uncomment when using in routes

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    """Hash a plain text password.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
        
    Example:
        hashed = hash_password("mypassword123")
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        is_valid = verify_password("mypassword123", stored_hash)
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        str: Encoded JWT token
        
    Example:
        token = create_access_token(data={"sub": user.email})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        dict: Decoded token payload, or None if invalid
        
    Example:
        payload = decode_access_token(token)
        if payload:
            user_email = payload.get("sub")
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency to get the current authenticated user.
    
    This function is used as a FastAPI dependency to extract and verify
    the JWT token from the request and return the authenticated user.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
        
    Example:
        @app.get("/profile")
        def get_profile(current_user: User = Depends(get_current_user)):
            return current_user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    # Uncomment and modify when User model is imported
    # user = db.query(User).filter(User.email == email).first()
    # if user is None:
    #     raise credentials_exception
    # return user
    
    # Placeholder return for now
    return {"email": email}


async def get_current_active_user(current_user = Depends(get_current_user)):
    """Dependency to get the current active user.
    
    Can be extended to check if user account is disabled, suspended, etc.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user account is inactive
    """
    # Extend this to check user.is_active or similar fields
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: str):
    """Dependency factory to require specific user role.
    
    Args:
        required_role: Required role (e.g., 'admin', 'manager')
        
    Returns:
        Dependency function that checks user role
        
    Example:
        @app.get("/admin/users")
        def get_all_users(
            current_user: User = Depends(get_current_user),
            _: None = Depends(require_role("admin"))
        ):
            # Only admin users can access this
            return users
    """
    async def role_checker(current_user = Depends(get_current_user)):
        # Uncomment when User model has role attribute
        # if current_user.role != required_role:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="Insufficient permissions"
        #     )
        return current_user
    
    return role_checker
