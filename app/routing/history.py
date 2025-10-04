from fastapi import APIRouter, Depends
from app.schemas.history import UrlHistoryResponse, UrlHistory
from app.schemas.analyze import UrlResponse
from app.depends import get_links_collection

router = APIRouter(tags=["📜 History"])

@router.post(
        "/history",
        response_model=UrlHistoryResponse,
        summary="📜 Retrieve the analysis history of a URL",
        description="""Returns a list of past analyses performed on the specified URL,
        including status codes, SSL information, response times, headers, redirects, content type,
        and any additional metadata. You can optionally limit the number of records returned or filter by date range."""
)
async def get_history(
    body: UrlHistory,
    links_collection = Depends(get_links_collection)
):
    url = str(body.link)
    limit = body.limit or 10
    mongo_filter = {"URL": url}

    records = await (
        links_collection
        .find(mongo_filter)
        .sort("inserted_at", -1)
        .limit(limit)
        .to_list(length=limit)
    )

    response_list = [
        UrlResponse(
            status=r.get("status"),
            headers=r.get("headers"),
            response_time=r.get("response_time"),
            ssl=r.get("ssl"),
            redirects=r.get("redirects"),
            content_type=r.get("content_type"),
            meta=r.get("meta"),
        )
        for r in records
    ]
    
    response = UrlHistoryResponse(
        link=url,
        history=response_list
    )

    return response
