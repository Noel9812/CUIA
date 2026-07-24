from fastapi import APIRouter, Response
from app.services.report_engine import ReportEngine

router = APIRouter()

@router.get("/reports/download/{report_type}")
def download_report(report_type: str, persona: str = "leadership"):
    valid_types = ["daily", "weekly", "monthly"]
    if report_type not in valid_types:
        return {"error": "Invalid report type"}
        
    pdf_bytes = ReportEngine.generate_pdf_report(report_type, persona)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename={persona}_{report_type}_report.pdf"
    })
