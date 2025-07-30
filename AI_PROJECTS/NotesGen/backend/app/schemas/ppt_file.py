from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PPTFileBase(BaseModel):
    filename: str
    path: str
    size: int

class PPTFileCreate(PPTFileBase):
    user_id: int

class PPTFileInDB(PPTFileBase):
    id: int
    user_id: int
    tracking_id: Optional[str] = None  # Add tracking_id field
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NoteVersionBase(BaseModel):
    version_number: int
    content: str
    ai_model: str
    ai_temperature: float

class NoteVersionCreate(NoteVersionBase):
    ppt_file_id: int

class NoteVersionInDB(NoteVersionBase):
    id: int
    ppt_file_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Bulk Processing Schemas
class BulkProcessingRequest(BaseModel):
    slides: Optional[List[int]] = None  # Optional list of specific slide numbers to process
    
class BulkProcessingResponse(BaseModel):
    job_id: str
    status: str
    message: str
    ppt_file_id: int
    optimization_info: Optional[dict] = None 