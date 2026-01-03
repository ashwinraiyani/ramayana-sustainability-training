"""SQLAlchemy Database Models

This module defines all database models for the Ramayana Sustainability Training platform.
Each model represents a table in the database with its respective columns and relationships.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    EMPLOYEE = "employee"
    MANAGER = "manager"
    ADMIN = "admin"


class ModuleDifficulty(str, enum.Enum):
    """Module difficulty level enumeration."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class ProgressStatus(str, enum.Enum):
    """Progress status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class User(Base):
    """User model representing platform users.
    
    Attributes:
        id: Primary key
        email: Unique user email address
        password_hash: Hashed password for authentication
        full_name: User's full name
        role: User role (employee, manager, admin)
        department: User's department
        created_at: Account creation timestamp
        progress: Relationship to user's module progress
        chat_messages: Relationship to user's chat history
        assessments: Relationship to user's assessment submissions
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class Module(Base):
    """Module model representing training modules.
    
    Attributes:
        id: Primary key
        title: Module title
        description: Detailed module description
        duration: Estimated duration in minutes
        difficulty: Difficulty level (beginner, intermediate, advanced)
        content: Module content (JSON or text)
        created_at: Module creation timestamp
        progress: Relationship to user progress for this module
        assessments: Relationship to assessments for this module
    """
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=False)  # Duration in minutes
    difficulty = Column(Enum(ModuleDifficulty), default=ModuleDifficulty.BEGINNER, nullable=False)
    content = Column(Text, nullable=True)  # Can store JSON or rich text content
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    progress = relationship("Progress", back_populates="module", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module(id={self.id}, title='{self.title}', difficulty='{self.difficulty}')>"


class Progress(Base):
    """Progress model tracking user progress through modules.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        module_id: Foreign key to Module
        status: Current progress status
        score: Assessment score (if completed)
        started_at: When user started the module
        completed_at: When user completed the module
        user: Relationship to User
        module: Relationship to Module
    """
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    status = Column(Enum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False)
    score = Column(Float, nullable=True)  # Score percentage (0-100)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    module = relationship("Module", back_populates="progress")

    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, module_id={self.module_id}, status='{self.status}')>"


class ChatMessage(Base):
    """ChatMessage model storing chatbot conversation history.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        message: User's message to the chatbot
        response: Chatbot's response
        context: Additional context (module, topic, etc.)
        timestamp: Message timestamp
        user: Relationship to User
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context = Column(String(255), nullable=True)  # E.g., module reference, topic
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, user_id={self.user_id}, timestamp={self.timestamp})>"


class Assessment(Base):
    """Assessment model storing user assessment submissions.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to User
        module_id: Foreign key to Module
        answers: User's answers (stored as JSON)
        score: Assessment score percentage
        passed: Whether user passed the assessment
        submitted_at: Submission timestamp
        user: Relationship to User
        module: Relationship to Module
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    answers = Column(Text, nullable=False)  # Store as JSON string
    score = Column(Float, nullable=False)  # Score percentage (0-100)
    passed = Column(Integer, default=0)  # 0 for false, 1 for true (SQLite compatibility)
    feedback = Column(Text, nullable=True)  # Optional feedback
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="assessments")
    module = relationship("Module", back_populates="assessments")

    def __repr__(self):
        return f"<Assessment(id={self.id}, user_id={self.user_id}, module_id={self.module_id}, score={self.score})>"
