import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.api_v1.api import api_router
from app.api.slide_images import router as slide_images_router
from app.api.tab_order_analysis import router as tab_order_router
from app.api import ppt_analysis  # Only import modules that exist
from app.api.ppt_text_editor import router as ppt_text_editor_router
from app.api.v1.ai import router as ai_router
from app.core.config import get_settings
from app.db.database import engine, Base, SessionLocal
from app.models.models import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title="NotesGen API",
    description="API for PowerPoint Note Generation Application",
    version="1.0.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create default user if it doesn't exist
def create_default_user():
    db = SessionLocal()
    try:
        default_user = db.query(User).filter(User.id == 1).first()
        if not default_user:
            user = User(
                id=1,
                username="default",
                hashed_password=get_password_hash("default"),
                home_directory="/uploads"
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

create_default_user()

# Include API routers - only include existing ones
app.include_router(api_router, prefix="/api/v1")
app.include_router(slide_images_router)
app.include_router(tab_order_router)
app.include_router(ppt_analysis.router)
app.include_router(ppt_text_editor_router)
# AI router - separate endpoint for AI functionality
app.include_router(ai_router, prefix="/api/v1/ai")

@app.get("/")
async def root():
    return {"message": "Welcome to NotesGen API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Run startup tasks."""
    logger.info("🚀 Starting NotesGen API server...")
    
    logger.info("✅ NotesGen API server startup complete")
