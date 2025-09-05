from fastapi import APIRouter, Depends
from app.schemas.analyze import UrlRequest, UrlResponse
from app.depends import get_inspector
from app.services.url_checks import URLInspector

router = APIRouter(tags=["Analyze"])

@router.post("/analyze", response_model=UrlResponse)
async def inspect_url(
    request: UrlRequest,
    inspector: URLInspector = Depends(get_inspector)
):
    status_headers = await inspector.check_status(request.link)

    if status_headers is not None:
      status_code, headers = status_headers
    else:
       status_code, headers = None, None


    response_time = await inspector.measure_response_time(request.link)
    ssl_information = await inspector.check_ssl(request.link)

    return UrlResponse(
      status=status_code,
      headers=headers,
      response_time=response_time,
      ssl=ssl_information is not None and ssl_information.get("valid"),
      meta={"ssl_information": ssl_information},
    )
