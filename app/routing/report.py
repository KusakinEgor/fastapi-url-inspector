from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.depends import get_links_collection
from app.schemas.report import ReportRequest, ReportResponse
from app.services.report_service import build_date_filter, aggregate_records, build_report_data

router = APIRouter(tags=["📊 Report"])

@router.post(
    "/report",
    response_model=ReportResponse,
    summary="📊 Generate aggregated report of URL checks",
    description="Returns aggregated statistics for all URLs or filtered by URL/date range"
)
async def get_report(
    body: ReportRequest,
    links_collection = Depends(get_links_collection)
) -> ReportResponse:
    query_filter = {}
    if body.url:
        query_filter["URL"] = str(body.url)

    date_filter = build_date_filter(body.from_date, body.to_date)
    if date_filter:
        query_filter["inserted_at"] = date_filter

    records = await links_collection.find(query_filter).to_list(length=None)

    aggregated = aggregate_records(records)
    report_data = build_report_data(aggregated)

    return ReportResponse(
        generated_at=datetime.now(timezone.utc),
        summary=report_data
    )
