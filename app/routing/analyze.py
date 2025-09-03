from fastapi import APIRouter
from app.schemas.analyze import UrlRequest, UrlResponse

router = APIRouter(prefix="/analyze", tags=["Analyze"])

@router.post("", response_model=UrlResponse)
async def inspect_url(request: UrlRequest):
    pass
