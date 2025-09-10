from fastapi import APIRouter, Depends
from datetime import datetime
from app.depends import get_links_collection
from app.schemas.report import ReportItem, ReportRequest, ReportResponse
from typing import List, Dict

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
):
    query_filter = {}
    urls = await links_collection.distinct("URL", filter=query_filter)
    report_data = []

    for url in urls:
        records = await links_collection.find({**query_filter, "URL": url}).to_list(length=None)
        total_checks = len(records)
        success_count = sum(1 for r in records if r.get("status") and 200 <= r["status"] < 400)
        failure_count = total_checks - success_count
        average_response_time = sum(r.get("response_time", 0) for r in records) / total_checks if total_checks else 0
        redirects_total = sum(r.get("redirects", 0) for r in records if r.get("redirects") is not None)
        ssl_issues = sum(1 for r in records if r.get("ssl") is False)

        report_data.append(
            ReportItem(
                url=url,
                total_checks=total_checks,
                success_count=success_count,
                failure_count=failure_count,
                average_response_time=average_response_time,
                redirects_total=redirects_total,
                ssl_issues=ssl_issues
            )
        )

    return ReportResponse(
        generated_at=datetime.now(),
        summary=report_data
    )
