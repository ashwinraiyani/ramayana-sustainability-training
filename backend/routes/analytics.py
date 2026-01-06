"""Analytics Routes

This module provides API endpoints for HR analytics dashboard,
including department-wise statistics, user progress analytics, and reports.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models import User, Module, Progress, Assessment, UserRole, ProgressStatus
from backend.auth import get_current_user

router = APIRouter()


# Pydantic models
class DepartmentStats(BaseModel):
    """Response model for department statistics."""
    department: str
    total_users: int
    avg_progress: float
    avg_score: float
    completion_rate: float


class OverallStats(BaseModel):
    """Response model for overall platform statistics."""
    total_users: int
    total_modules: int
    total_completions: int
    avg_score: float
    active_learners: int


class UserProgressSummary(BaseModel):
    """Response model for user progress summary."""
    user_id: int
    full_name: str
    email: str
    department: Optional[str]
    modules_completed: int
    avg_score: float
    last_activity: Optional[datetime]


@router.get("/overview", response_model=OverallStats)
async def get_overview_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall platform statistics.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        OverallStats: Overall platform statistics
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Calculate statistics
    total_users = db.query(func.count(User.id)).scalar()
    total_modules = db.query(func.count(Module.id)).scalar()
    total_completions = db.query(func.count(Progress.id)).filter(
        Progress.status == ProgressStatus.COMPLETED
    ).scalar()
    
    # Average score
    avg_score_result = db.query(func.avg(Progress.score)).filter(
        Progress.score.isnot(None)
    ).scalar()
    avg_score = round(float(avg_score_result or 0), 2)
    
    # Active learners (users with activity in last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    active_learners = db.query(func.count(func.distinct(Progress.user_id))).filter(
        Progress.started_at >= seven_days_ago
    ).scalar()
    
    return {
        "total_users": total_users,
        "total_modules": total_modules,
        "total_completions": total_completions,
        "avg_score": avg_score,
        "active_learners": active_learners
    }


@router.get("/departments", response_model=List[DepartmentStats])
async def get_department_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics by department.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[DepartmentStats]: Statistics for each department
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get all departments
    departments = db.query(User.department).distinct().filter(
        User.department.isnot(None)
    ).all()
    
    stats = []
    for (dept,) in departments:
        # Users in department
        dept_users = db.query(User).filter(User.department == dept).all()
        user_ids = [u.id for u in dept_users]
        
        if not user_ids:
            continue
        
        # Progress for department users
        dept_progress = db.query(Progress).filter(
            Progress.user_id.in_(user_ids)
        ).all()
        
        # Calculate metrics
        total_users = len(dept_users)
        completed = len([p for p in dept_progress if p.status == ProgressStatus.COMPLETED])
        scores = [p.score for p in dept_progress if p.score is not None]
        
        avg_score = round(sum(scores) / len(scores), 2) if scores else 0
        completion_rate = round((completed / len(dept_progress) * 100), 2) if dept_progress else 0
        avg_progress = round((completed / total_users * 100), 2) if total_users else 0
        
        stats.append({
            "department": dept,
            "total_users": total_users,
            "avg_progress": avg_progress,
            "avg_score": avg_score,
            "completion_rate": completion_rate
        })
    
    return stats


@router.get("/top-performers", response_model=List[UserProgressSummary])
async def get_top_performers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get top performing users (champions).
    
    Args:
        current_user: Current authenticated user
        db: Database session
        limit: Number of top performers to return
        
    Returns:
        List[UserProgressSummary]: Top performing users
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get users with their completion stats
    user_stats = []
    users = db.query(User).all()
    
    for user in users:
        progress_records = db.query(Progress).filter(
            Progress.user_id == user.id
        ).all()
        
        completed = [p for p in progress_records if p.status == ProgressStatus.COMPLETED]
        scores = [p.score for p in completed if p.score is not None]
        
        if completed:
            last_activity = max([p.completed_at or p.started_at for p in progress_records])
            avg_score = round(sum(scores) / len(scores), 2) if scores else 0
            
            user_stats.append({
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "department": user.department,
                "modules_completed": len(completed),
                "avg_score": avg_score,
                "last_activity": last_activity
            })
    
    # Sort by modules completed and avg score
    user_stats.sort(key=lambda x: (x["modules_completed"], x["avg_score"]), reverse=True)
    
    return user_stats[:limit]


@router.get("/user/{user_id}/progress", response_model=UserProgressSummary)
async def get_user_progress_detail(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a specific user.
    
    Args:
        user_id: User ID to get progress for
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        UserProgressSummary: User's progress details
        
    Raises:
        HTTPException: If user doesn't have permission or user not found
    """
    # Check permissions (users can view their own, managers/admins can view all)
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    progress_records = db.query(Progress).filter(Progress.user_id == user_id).all()
    completed = [p for p in progress_records if p.status == ProgressStatus.COMPLETED]
    scores = [p.score for p in completed if p.score is not None]
    
    last_activity = None
    if progress_records:
        last_activity = max([p.completed_at or p.started_at for p in progress_records])
    
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0
    
    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "department": user.department,
        "modules_completed": len(completed),
        "avg_score": avg_score,
        "last_activity": last_activity
    }
