"""Reports API routes."""

import logging
from fastapi import APIRouter, Response, HTTPException

from app.services.report_engine import ReportEngine

logger = logging.getLogger("cuia.api.reports")

router = APIRouter()

VALID_REPORT_TYPES = {"daily", "weekly", "monthly"}


@router.get("/reports/download/{report_type}")
def download_report(report_type: str, persona: str = "leadership"):
    """Download a PDF report of the specified type."""
    if report_type not in VALID_REPORT_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error_type": "InvalidReportType",
                "message": f"Invalid report type: '{report_type}'. Must be one of: {', '.join(sorted(VALID_REPORT_TYPES))}"
            }
        )
    
    try:
        pdf_bytes = ReportEngine.generate_pdf_report(report_type, persona)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={persona}_{report_type}_report.pdf"
            }
        )
    except Exception as e:
        logger.error("Report generation error: %s", str(e))
        raise HTTPException(status_code=500, detail={"error_type": "ReportError", "message": str(e)})
