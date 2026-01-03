"""Database Configuration Module

This module handles database connection setup using SQLAlchemy.
It provides the database engine, session management, and base class for models.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Load database URL from environment variable
# Format: postgresql://user:password@host:port/database
# For SQLite (development): sqlite:///./ramayana_training.db
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./ramayana_training.db"  # Default to SQLite for development
)

# Handle PostgreSQL URL format from some providers (replace postgres:// with postgresql://)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create database engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True  # Set to False in production
    )
else:
    # PostgreSQL/other database configuration
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=True  # Set to False in production
    )

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for SQLAlchemy models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency function to get database session.
    
    This function is used as a FastAPI dependency to provide
    database sessions to route handlers. It ensures proper
    session cleanup after each request.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables.
    
    Creates all tables defined in models if they don't exist.
    Should be called once during application startup.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


def drop_db():
    """Drop all database tables.
    
    WARNING: This will delete all data. Use only for testing/development.
    """
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped")
