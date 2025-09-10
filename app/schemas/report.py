from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class ReportRequest(BaseModel):
    url: Optional[HttpUrl] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

class ReportItem(BaseModel):
    url: str
    total_checks: int
    success_count: int
    failure_count: int
    average_response_time: float
    redirects_total: int
    ssl_issues: int

class ReportResponse(BaseModel):
    generated_at: datetime
    summary: list[ReportItem]
