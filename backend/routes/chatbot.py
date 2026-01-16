"""Chatbot API Routes

Handles AI chatbot interactions with Hanuman (the AI assistant)
for sustainability guidance based on Ramayana wisdom.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
import os
import json

# OpenAI integration
try:
    import openai
    OPENAI_AVAILABLE = True
    openai.api_key = os.getenv("OPENAI_API_KEY")
except ImportError:
    OPENAI_AVAILABLE = False

router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])

# Configuration
MAX_MESSAGE_LENGTH = 1000
MAX_HISTORY_LENGTH = 50
DEFAULT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 500
TEMPERATURE = 0.7

# System prompt for Hanuman AI
HANUMAN_SYSTEM_PROMPT = """
You are Hanuman, a wise AI assistant based on the noble character from the Ramayana.
You guide users through their sustainability learning journey with wisdom, devotion, and strength.

Your role:
1. Answer questions about sustainability concepts and how they relate to Ramayana teachings
2. Provide guidance on learning modules and content
3. Encourage users with motivational messages inspired by Hanuman's virtues: devotion, courage, strength, and service
4. Connect ancient wisdom from the Ramayana to modern sustainability challenges
5. Help users understand the dharmic principles behind environmental stewardship

Your personality:
- Wise and knowledgeable
- Encouraging and supportive
- Humble yet confident
- Focus on action and service
- Reference Ramayana stories when relevant

Keep responses concise, practical, and inspiring.
Always maintain respect for the sacred text while making concepts accessible to modern learners.
"""

# Fallback responses when OpenAI is not available
FALLBACK_RESPONSES = [
    {
        "keywords": ["hello", "hi", "hey", "greetings"],
        "response": "🙏 Namaste! I am Hanuman, your guide on this sustainability journey. Like how I served Lord Rama with devotion, I am here to serve you in learning. How may I assist you today?"
    },
    {
        "keywords": ["help", "what can you do", "how to use"],
        "response": "I can help you with:\n\n📚 Understanding learning modules\n🌱 Sustainability concepts\n📖 Ramayana wisdom and its relevance\n💡 Answering your questions\n🎯 Guidance on your learning path\n\nJust ask me anything!"
    },
    {
        "keywords": ["sustainability", "environment", "nature"],
        "response": "In the Ramayana, we see deep respect for nature. When I searched for Sita, I spoke with the trees, mountains, and rivers. This teaches us that nature is sacred and deserves our protection. Sustainability means caring for our Earth with the same devotion we give to dharma."
    },
    {
        "keywords": ["dharma", "duty", "righteousness"],
        "response": "Dharma means righteous duty. In protecting the environment, we fulfill our dharma to future generations. Like how Lord Rama upheld dharma in all situations, we must uphold our duty to protect and preserve our planet. Every small action matters!"
    },
    {
        "keywords": ["motivation", "inspire", "encourage"],
        "response": "🔥 Remember, just as I leaped across the ocean to Lanka with unwavering faith, you too can overcome any challenge in your learning journey! Strength, devotion, and consistent effort will lead you to success. Keep moving forward!"
    },
    {
        "keywords": ["module", "lesson", "learn", "course"],
        "response": "The modules combine ancient wisdom with modern sustainability knowledge. Each lesson connects a teaching from the Ramayana to practical environmental action. Progress through them steadily, like climbing Mount Gandhamadana - one step at a time!"
    },
    {
        "keywords": ["thank", "thanks", "grateful"],
        "response": "🙏 You are most welcome! It is my honor to serve you on this journey. May your learning bring wisdom and may your actions bring positive change to the world. Jai Shri Ram!"
    }
]

DEFAULT_FALLBACK_RESPONSE = """🙏 I am Hanuman, your learning companion. While I'm currently in simple mode, I'm still here to help!

I can discuss:
• Sustainability and environmental protection
• Ramayana wisdom and its modern applications
• Your learning journey and modules
• Motivation and guidance

What would you like to know?"""

# Pydantic Models
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SendMessageRequest(BaseModel):
    message: str
    context: Optional[str] = None  # Optional context like current module
    
    @validator('message')
    def validate_message(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Message cannot be empty')
        if len(v) > MAX_MESSAGE_LENGTH:
            raise ValueError(f'Message cannot exceed {MAX_MESSAGE_LENGTH} characters')
        return v

class ChatResponse(BaseModel):
    message: str
    timestamp: datetime
    is_fallback: bool = False

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]
    total_messages: int

# Database dependency
def get_db():
    """
    Database session dependency.
    Replace with your actual database session logic.
    """
    pass

# Auth dependency
async def get_current_active_user(token: str = None):
    """
    Get current authenticated user.
    Import from backend.routes.users in actual implementation.
    """
    pass

# Utility Functions
def get_user_chat_history(db: Session, user_id: int, limit: int = 20):
    """Get user's chat history from database."""
    # Implement based on your ChatMessage model
    # Example:
    # from backend.models import ChatMessage
    # return db.query(ChatMessage).filter(
    #     ChatMessage.user_id == user_id
    # ).order_by(ChatMessage.timestamp.desc()).limit(limit).all()
    pass

def save_chat_message(db: Session, user_id: int, role: str, content: str):
    """Save a chat message to database."""
    # Implement based on your ChatMessage model
    # Example:
    # from backend.models import ChatMessage
    # message = ChatMessage(
    #     user_id=user_id,
    #     role=role,
    #     content=content,
    #     timestamp=datetime.utcnow()
    # )
    # db.add(message)
    # db.commit()
    # db.refresh(message)
    # return message
    pass

def delete_user_chat_history(db: Session, user_id: int):
    """Delete all chat history for a user."""
    # Implement based on your ChatMessage model
    pass

def get_fallback_response(message: str) -> str:
    """Get a fallback response based on keywords."""
    message_lower = message.lower()
    
    # Check for keyword matches
    for response_data in FALLBACK_RESPONSES:
        for keyword in response_data["keywords"]:
            if keyword in message_lower:
                return response_data["response"]
    
    # Return default fallback
    return DEFAULT_FALLBACK_RESPONSE

async def get_ai_response(message: str, chat_history: List[dict], context: Optional[str] = None) -> tuple[str, bool]:
    """Get response from OpenAI or fallback."""
    
    # Try OpenAI if available
    if OPENAI_AVAILABLE and openai.api_key:
        try:
            # Build messages for OpenAI
            messages = [{"role": "system", "content": HANUMAN_SYSTEM_PROMPT}]
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Current context: The user is working on {context}"
                })
            
            # Add chat history (last 10 messages for context)
            messages.extend(chat_history[-10:])
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call OpenAI API
            response = await openai.ChatCompletion.acreate(
                model=DEFAULT_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
            )
            
            ai_message = response.choices[0].message.content
            return ai_message, False
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fall through to fallback
    
    # Use fallback response
    fallback_message = get_fallback_response(message)
    return fallback_message, True

# API Routes
@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Send a message to Hanuman (AI chatbot) and get a response.
    
    - **message**: User's message (max 1000 characters)
    - **context**: Optional context (e.g., current module being studied)
    """
    # Save user message
    save_chat_message(
        db,
        user_id=current_user.id,
        role="user",
        content=request.message
    )
    
    # Get chat history for context
    history = get_user_chat_history(db, user_id=current_user.id, limit=10)
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(history)  # Reverse to get chronological order
    ]
    
    # Get AI response
    ai_message, is_fallback = await get_ai_response(
        message=request.message,
        chat_history=chat_history,
        context=request.context
    )
    
    # Save assistant message
    save_chat_message(
        db,
        user_id=current_user.id,
        role="assistant",
        content=ai_message
    )
    
    return ChatResponse(
        message=ai_message,
        timestamp=datetime.utcnow(),
        is_fallback=is_fallback
    )

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Get user's chat history with Hanuman.
    
    - **limit**: Maximum number of messages to return (default: 50, max: 50)
    """
    if limit > MAX_HISTORY_LENGTH:
        limit = MAX_HISTORY_LENGTH
    
    messages = get_user_chat_history(db, user_id=current_user.id, limit=limit)
    
    # Reverse to get chronological order
    messages = list(reversed(messages))
    
    return ChatHistoryResponse(
        messages=messages,
        total_messages=len(messages)
    )

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Clear all chat history with Hanuman.
    This action is irreversible.
    """
    delete_user_chat_history(db, user_id=current_user.id)
    return None

@router.get("/status", response_model=dict)
async def get_chatbot_status():
    """
    Get chatbot service status and capabilities.
    """
    return {
        "service": "Hanuman AI Chatbot",
        "status": "online",
        "ai_enabled": OPENAI_AVAILABLE and bool(os.getenv("OPENAI_API_KEY")),
        "model": DEFAULT_MODEL if OPENAI_AVAILABLE else "fallback",
        "max_message_length": MAX_MESSAGE_LENGTH,
        "max_history_length": MAX_HISTORY_LENGTH,
        "features": [
            "Sustainability guidance",
            "Ramayana wisdom",
            "Learning support",
            "Motivational messages",
            "Context-aware responses"
        ]
    }

@router.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_chat_feedback(
    message_id: int,
    helpful: bool,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Submit feedback on a chatbot response.
    Helps improve the AI's responses over time.
    
    - **message_id**: ID of the assistant message
    - **helpful**: Whether the response was helpful
    - **comment**: Optional feedback comment
    """
    # Implement feedback storage
    # This can be used to fine-tune the model or improve fallback responses
    return {"message": "Feedback received. Thank you!"}
