from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.schemas.analyze import UrlResponse

class UrlHistory(BaseModel):
    link: HttpUrl
    limit: Optional[int] = 10
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

class UrlHistoryResponse(BaseModel):
    link: HttpUrl
    history: List[UrlResponse]
