from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class UrlRequest(BaseModel):
    link: HttpUrl
    checks: Optional[List[str]] = None
    timeout: Optional[int] = 5
    follow_redirects: bool = True
    user_agent: Optional[str] = None

class UrlResponse(BaseModel):
    status: Optional[int] = None
    ssl: Optional[bool] = None
    headers: Optional[dict] = None
    redirects: Optional[List[str]] = None
    response_time: Optional[float] = None
    meta: Optional[dict] = None
    suspicious: Optional[bool] = None
    content_type: Optional[str] = None

