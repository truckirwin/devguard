from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    ppt_files,
    auth,
    bulk_notes,
    ai_prompts,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ppt_files.router, prefix="/ppt-files", tags=["ppt-files"])
api_router.include_router(bulk_notes.router, prefix="", tags=["bulk-processing"])
api_router.include_router(ai_prompts.router, prefix="/ai", tags=["ai-prompts"])
