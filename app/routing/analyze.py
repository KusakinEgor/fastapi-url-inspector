from fastapi import APIRouter, Depends, Request
from app.schemas.analyze import UrlRequest, UrlResponse
from app.depends import get_inspector
from app.depends import get_links_collection
from app.services.url_checks import URLInspector
from app.repositories.redis_cache import redis_client
from app.repositories.rabbitmq_manager import send_to_queue
import pymongo
import asyncio
import json

router = APIRouter(tags=["🔍 Analyze"])

@router.post(
        "/analyze",
        response_model=UrlResponse,
        summary="🔍 Perform comprehensive URL analysis",
        description="""
        Analyzes a URL by checking availability ✅, status code ✅, response time ⏱,
        SSL certificate 🔒, headers and meta tags 📝, suspicious query parameters ⚠️,
        redirects 🔁, and content type 📋. Results are stored in MongoDB and can be cached in Redis for faster access.
        """
)
async def inspect_url(
    request: Request,
    url_request: UrlRequest,
    inspector: URLInspector = Depends(get_inspector),
    links_collection = Depends(get_links_collection),
):
    cache_key = f"url:{url_request.link}"
    chached = await redis_client.get(cache_key)

    if chached:
        return UrlResponse(**json.loads(chached)) 

    status_headers, response_time, ssl_information, redirects = await asyncio.gather(
        inspector.check_status(url_request.link),
        inspector.measure_response_time(url_request.link),
        inspector.check_ssl(url_request.link),
        inspector.get_redirects(url_request.link, follow_redirects=url_request.follow_redirects)
    )

    status_code, headers = status_headers if status_headers is not None else (None, None)
    content_type = headers.get("content-type") if headers else None

    get_ssl_information = ssl_information is not None and ssl_information.get("valid")

    mongo_request = {
       "URL": str(url_request.link),
       "status": status_code,
       "headers": headers,
       "response_time": response_time,
       "ssl": get_ssl_information,
       "meta": {
          "ssl_information": ssl_information
       },
       "user_agent": request.headers.get("user-agent"),
       "content_type": content_type
    }

    try:
        await links_collection.insert_one(mongo_request)
    except pymongo.errors.DuplicateKeyError as e:
        print(f"Error: {e}")
    except pymongo.errors.PyMongoError as e:
        print(f"Error: {e}")
    
    response = UrlResponse(
      status=status_code,
      headers=headers,
      redirects=redirects,
      response_time=response_time,
      ssl=get_ssl_information,
      meta={"ssl_information": ssl_information},
      content_type=content_type,
    )

    await redis_client.set(cache_key, response.json(), ex=300)

    return response
