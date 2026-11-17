from fastapi import APIRouter, Depends, status

from controllers.security import require_api_key
from models.failure_report import (
    FailureReport,
    FailureReportListResponse,
    FailureReportRequest,
    create_failure_report,
    list_recent_failure_reports,
)

router = APIRouter(
    prefix="/internet-failures",
    tags=["internet-failures"],
    dependencies=[Depends(require_api_key)],
)


@router.post(
    "",
    response_model=FailureReport,
    status_code=status.HTTP_201_CREATED,
)
def submit_internet_failure_report(
    report: FailureReportRequest,
) -> FailureReport:
    return create_failure_report(report)


@router.get("", response_model=FailureReportListResponse)
def get_recent_internet_failure_reports() -> FailureReportListResponse:
    return FailureReportListResponse(reports=list_recent_failure_reports())
