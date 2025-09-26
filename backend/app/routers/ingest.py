
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

router = APIRouter()

class IngestItem(BaseModel):
    platform: str = Field(..., examples=["instagram","youtube","blog","news"])
    brand: str
    text: str
    url: Optional[str] = None
    published_at: Optional[datetime] = None
    meta: Optional[dict] = None

@router.post("/ingest")
def ingest(items: List[IngestItem]):
    return {"ingested": len(items)}
