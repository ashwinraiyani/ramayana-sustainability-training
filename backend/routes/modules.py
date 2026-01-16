"""Learning Module Management API Routes

Handles learning modules, content delivery, and progress tracking.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from enum import Enum

router = APIRouter(prefix="/api/modules", tags=["modules"])

# Enums
class ModuleDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ModuleCategory(str, Enum):
    SUSTAINABILITY = "sustainability"
    DHARMA = "dharma"
    LEADERSHIP = "leadership"
    TEAMWORK = "teamwork"
    ETHICS = "ethics"
    ENVIRONMENT = "environment"

class ProgressStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Pydantic Models
class ContentSection(BaseModel):
    id: int
    title: str
    content: str
    order: int
    estimated_time_minutes: int
    
    class Config:
        from_attributes = True

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer_index: int
    explanation: str
    points: int
    
    class Config:
        from_attributes = True

class ModuleBase(BaseModel):
    title: str
    description: str
    ramayana_reference: str
    sustainability_topic: str
    difficulty: ModuleDifficulty
    category: ModuleCategory
    estimated_duration_minutes: int
    points_reward: int

class ModuleResponse(ModuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    content_sections_count: int
    quiz_questions_count: int
    enrolled_users_count: int
    
    class Config:
        from_attributes = True

class ModuleDetail(ModuleResponse):
    content_sections: List[ContentSection]
    quiz_questions: List[QuizQuestion]
    
    class Config:
        from_attributes = True

class ModuleProgressResponse(BaseModel):
    id: int
    module_id: int
    user_id: int
    status: ProgressStatus
    progress_percentage: float
    current_section_id: Optional[int]
    quiz_score: Optional[int]
    quiz_attempts: int
    started_at: datetime
    completed_at: Optional[datetime]
    last_accessed_at: datetime
    time_spent_minutes: int
    
    class Config:
        from_attributes = True

class StartModuleRequest(BaseModel):
    module_id: int

class UpdateProgressRequest(BaseModel):
    current_section_id: int
    time_spent_minutes: int
    completed_sections: List[int]
    
    @validator('time_spent_minutes')
    def validate_time(cls, v):
        if v < 0:
            raise ValueError('Time spent cannot be negative')
        return v

class SubmitQuizRequest(BaseModel):
    module_id: int
    answers: List[int]  # List of selected answer indices

class QuizResultResponse(BaseModel):
    score: int
    total_questions: int
    percentage: float
    passed: bool
    points_earned: int
    feedback: List[dict]

# Database dependency
def get_db():
    """
    Database session dependency.
    Replace with your actual database session logic.
    """
    pass

# Auth dependency (import from users.py)
async def get_current_active_user(token: str = None):
    """
    Get current authenticated user.
    Import from backend.routes.users in actual implementation.
    """
    pass

# Utility Functions
def get_module_by_id(db: Session, module_id: int):
    """Get module by ID from database."""
    # Implement based on your Module model
    pass

def get_all_modules(db: Session, skip: int = 0, limit: int = 100, 
                    category: Optional[str] = None, difficulty: Optional[str] = None):
    """Get all modules with optional filtering."""
    # Implement based on your Module model
    pass

def get_user_progress(db: Session, user_id: int, module_id: int):
    """Get user's progress for a specific module."""
    # Implement based on your ModuleProgress model
    pass

def create_module_progress(db: Session, user_id: int, module_id: int):
    """Create new progress record for user starting a module."""
    # Implement based on your ModuleProgress model
    pass

def update_module_progress(db: Session, progress_id: int, update_data: dict):
    """Update module progress."""
    # Implement based on your ModuleProgress model
    pass

def calculate_progress_percentage(completed_sections: List[int], total_sections: int) -> float:
    """Calculate progress percentage."""
    if total_sections == 0:
        return 0.0
    return (len(completed_sections) / total_sections) * 100

# API Routes
@router.get("/", response_model=List[ModuleResponse])
async def get_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[ModuleCategory] = None,
    difficulty: Optional[ModuleDifficulty] = None,
    db: Session = Depends(get_db)
):
    """
    Get all learning modules with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **category**: Filter by category
    - **difficulty**: Filter by difficulty level
    """
    modules = get_all_modules(
        db,
        skip=skip,
        limit=limit,
        category=category.value if category else None,
        difficulty=difficulty.value if difficulty else None
    )
    return modules

@router.get("/{module_id}", response_model=ModuleDetail)
async def get_module(
    module_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific module.
    Includes content sections and quiz questions.
    Requires authentication.
    """
    module = get_module_by_id(db, module_id=module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module

@router.post("/start", response_model=ModuleProgressResponse, status_code=status.HTTP_201_CREATED)
async def start_module(
    request: StartModuleRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Start a new module or resume an existing one.
    Creates a progress tracking record.
    """
    # Check if module exists
    module = get_module_by_id(db, module_id=request.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check if user already has progress for this module
    existing_progress = get_user_progress(db, user_id=current_user.id, module_id=request.module_id)
    if existing_progress:
        # Update last accessed time
        existing_progress.last_accessed_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_progress)
        return existing_progress
    
    # Create new progress record
    progress = create_module_progress(db, user_id=current_user.id, module_id=request.module_id)
    return progress

@router.get("/progress/my", response_model=List[ModuleProgressResponse])
async def get_my_progress(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get current user's progress across all modules.
    """
    # Implement query to get all progress records for current user
    # Example:
    # from backend.models import ModuleProgress
    # progress_records = db.query(ModuleProgress).filter(
    #     ModuleProgress.user_id == current_user.id
    # ).all()
    # return progress_records
    pass

@router.get("/progress/{module_id}", response_model=ModuleProgressResponse)
async def get_module_progress(
    module_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get current user's progress for a specific module.
    """
    progress = get_user_progress(db, user_id=current_user.id, module_id=module_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this module. Start the module first."
        )
    return progress

@router.put("/progress/{module_id}", response_model=ModuleProgressResponse)
async def update_progress(
    module_id: int,
    update: UpdateProgressRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update progress for a specific module.
    
    - **current_section_id**: ID of the section currently being viewed
    - **time_spent_minutes**: Additional time spent in this session
    - **completed_sections**: List of all completed section IDs
    """
    # Get existing progress
    progress = get_user_progress(db, user_id=current_user.id, module_id=module_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found. Start the module first."
        )
    
    # Get module to calculate progress percentage
    module = get_module_by_id(db, module_id=module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Update progress
    progress.current_section_id = update.current_section_id
    progress.time_spent_minutes += update.time_spent_minutes
    progress.last_accessed_at = datetime.utcnow()
    
    # Calculate progress percentage
    total_sections = module.content_sections_count
    progress.progress_percentage = calculate_progress_percentage(
        update.completed_sections, total_sections
    )
    
    # Check if all sections completed
    if len(update.completed_sections) == total_sections:
        progress.status = ProgressStatus.IN_PROGRESS.value
        # Status will change to COMPLETED after quiz submission
    
    db.commit()
    db.refresh(progress)
    
    return progress

@router.post("/quiz/submit", response_model=QuizResultResponse)
async def submit_quiz(
    submission: SubmitQuizRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Submit quiz answers and get results.
    Awards points and marks module as completed if passed.
    """
    # Get module and quiz questions
    module = get_module_by_id(db, module_id=submission.module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Get user's progress
    progress = get_user_progress(db, user_id=current_user.id, module_id=submission.module_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found. Start the module first."
        )
    
    # Get quiz questions
    quiz_questions = module.quiz_questions
    if len(submission.answers) != len(quiz_questions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of answers doesn't match number of questions"
        )
    
    # Grade the quiz
    score = 0
    total_points = 0
    feedback = []
    
    for i, (question, answer) in enumerate(zip(quiz_questions, submission.answers)):
        total_points += question.points
        is_correct = answer == question.correct_answer_index
        
        if is_correct:
            score += question.points
        
        feedback.append({
            "question_id": question.id,
            "question_number": i + 1,
            "correct": is_correct,
            "user_answer": answer,
            "correct_answer": question.correct_answer_index,
            "explanation": question.explanation,
            "points_earned": question.points if is_correct else 0
        })
    
    # Calculate percentage
    percentage = (score / total_points * 100) if total_points > 0 else 0
    passed = percentage >= 70  # 70% passing grade
    
    # Update progress
    progress.quiz_score = score
    progress.quiz_attempts += 1
    
    # Award points and mark as completed if passed
    if passed:
        progress.status = ProgressStatus.COMPLETED.value
        progress.completed_at = datetime.utcnow()
        progress.progress_percentage = 100.0
        
        # Award points to user
        current_user.total_points += module.points_reward
        current_user.modules_completed += 1
    
    db.commit()
    
    return {
        "score": score,
        "total_questions": len(quiz_questions),
        "percentage": round(percentage, 2),
        "passed": passed,
        "points_earned": module.points_reward if passed else 0,
        "feedback": feedback
    }

@router.get("/recommended", response_model=List[ModuleResponse])
async def get_recommended_modules(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get personalized module recommendations based on user's progress and interests.
    """
    # Implement recommendation logic based on:
    # - User's completed modules
    # - User's skill level
    # - Popular modules
    # - Sequential learning path
    
    # Simple implementation: return modules user hasn't completed
    # Ordered by difficulty (beginner first)
    pass

@router.get("/categories", response_model=List[dict])
async def get_module_categories():
    """
    Get all available module categories with counts.
    """
    categories = [
        {
            "name": category.value,
            "display_name": category.value.replace('_', ' ').title(),
            "description": f"Learn about {category.value}"
        }
        for category in ModuleCategory
    ]
    return categories

@router.get("/leaderboard", response_model=List[dict])
async def get_module_leaderboard(
    module_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get top performers for a specific module.
    Shows users with highest quiz scores and fastest completion times.
    """
    # Implement leaderboard query
    # Order by quiz_score DESC, time_spent_minutes ASC
    pass
