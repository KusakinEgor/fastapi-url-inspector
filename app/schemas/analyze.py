from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class UrlRequest(BaseModel):
    link: HttpUrl
    checks: Optional[List[str]] = None
    timeout: Optional[int] = 5
    follow_redirects: bool = True
    user_agent: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "link": "https://example.com",
                "checks": ["status", "ssl", "meta"],
                "timeout": 5,
                "follow_redirects": True,
                "user_agent": "MyTestAgent"
            }
        }

class UrlResponse(BaseModel):
    status: Optional[int] = None
    ssl: Optional[bool] = None
    headers: Optional[dict] = None
    redirects: Optional[List[str]] = None
    response_time: Optional[float] = None
    meta: Optional[dict] = None
    suspicious: Optional[bool] = None
    content_type: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": 200,
                "ssl": True,
                "headers": {
                    "content-type": "text/html; charset=UTF-8",
                    "server": "nginx"
                },
                "redirects": ["https://example.com/redirect1"],
                "response_time": 0.123,
                "meta": {
                    "ssl_information": {
                        "valid": True,
                        "expires": "2026-09-06T12:00:00Z",
                        "issuer": {"CN": "Example CA"},
                        "subject": {"CN": "example.com"}
                    }
                },
                "suspicious": False,
                "content_type": "text/html"
            }
        }

