from datetime import datetime, time, timezone
from app.schemas.report import ReportItem

def build_date_filter(from_date, to_date):
    if not from_date and not to_date:
        return None

    date_filter = {}
    if from_date:
        date_filter["$gte"] = datetime.combine(from_date.date(), time(0, 0, 0, 0), tzinfo=timezone.utc)
    if to_date:
        date_filter["$lte"] = datetime.combine(to_date.date(), time(23, 59, 59, 999999), tzinfo=timezone.utc)
    return date_filter

def aggregate_records(records):
    aggregated = {}

    for record in records:
        url = record["URL"]
        if url not in aggregated:
            aggregated[url] = {
                "total_checks": 0,
                "success_count": 0,
                "failure_count": 0,
                "response_time_sum": 0.0,
                "redirects_total": 0,
                "ssl_issues": 0
            }

        agg = aggregated[url]
        agg["total_checks"] += 1
        status = record.get("status", 0)
        if 200 <= status < 400:
            agg["success_count"] += 1
        else:
            agg["failure_count"] += 1

        agg["response_time_sum"] += record.get("response_time", 0)
        agg["redirects_total"] += record.get("redirects") or 0
        if record.get("ssl") is False:
            agg["ssl_issues"] += 1

    return aggregated

def build_report_data(aggregated):
    report_data = []
    for url, agg in aggregated.items():
        average_response_time = agg["response_time_sum"] / agg["total_checks"] if agg["total_checks"] else 0
        report_data.append(
            ReportItem(
                url=url,
                total_checks=agg["total_checks"],
                success_count=agg["success_count"],
                failure_count=agg["failure_count"],
                average_response_time=average_response_time,
                redirects_total=agg["redirects_total"],
                ssl_issues=agg["ssl_issues"]
            )
        )
    return report_data
