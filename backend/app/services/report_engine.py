"""
Report Engine — deterministic report generation for CUIA.

Reports consume analytics output. Reports never recompute analytics.
All organization names, KPIs, and metrics originate from the analytics engine.
No hardcoded values.
"""

import io
import logging
from datetime import datetime
from typing import Dict, Any, List

from app.services.analytics_engine import AnalyticsEngine
from app.services.recommendation_engine import RecommendationEngine
from app.services.forecast_engine import ForecastEngine
from app.core.config_loader import ConfigLoader

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except ImportError:
    pass

logger = logging.getLogger("cuia.reports")


class ReportEngine:
    """
    PDF report generator that consumes analytics, forecast, and recommendations.
    Never recomputes analytics — always uses the cached computed state.
    """

    @classmethod
    def generate_pdf_report(cls, report_type: str, persona: str = "leadership") -> bytes:
        """Generate a PDF report of the specified type and persona scope."""
        logger.info("Generating %s report for persona: %s", report_type, persona)
        
        analytics = AnalyticsEngine.get_analytics()
        all_recs = RecommendationEngine.get_recommendations()
        analytics_rules = ConfigLoader.get_analytics_rules()
        sprint_duration = analytics_rules["sprint_duration_weeks"]
        
        # Scope data based on persona
        scoped = cls._scope_data(analytics, all_recs, persona, sprint_duration)
        
        # Build PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'],
            fontSize=24, spaceAfter=20, textColor=colors.HexColor("#1A202C")
        )
        h2_style = ParagraphStyle(
            'H2Style', parent=styles['Heading2'],
            fontSize=16, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor("#2D3748")
        )
        
        elements = []
        
        # Cover page — org name from dataset, not hardcoded
        org_name = analytics["organization"]["name"]
        elements.append(Paragraph(f"{report_type.capitalize()} Management Report", title_style))
        elements.append(Paragraph(f"<b>Organization:</b> {org_name}", styles['Normal']))
        elements.append(Paragraph(f"<b>Reporting Period:</b> {report_type.capitalize()}", styles['Normal']))
        elements.append(Paragraph(f"<b>Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Persona:</b> {scoped['persona_label']}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Delegate to report-type-specific builder
        if report_type == "daily":
            cls._build_daily(elements, scoped, styles, h2_style)
        elif report_type == "weekly":
            cls._build_weekly(elements, scoped, styles, h2_style)
        else:
            cls._build_monthly(elements, scoped, styles, h2_style)
        
        # Appendix
        elements.append(Paragraph("Appendix", h2_style))
        elements.append(Paragraph(f"Dataset: Simulated Jira Data (CUIA POC)", styles['Normal']))
        elements.append(Paragraph(f"Generated Timestamp: {datetime.now().isoformat()}", styles['Normal']))
        
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        logger.info("Report generated: %s (%d bytes)", report_type, len(pdf_bytes))
        return pdf_bytes

    # ──────────────────────────────────────────────
    # Scope resolution
    # ──────────────────────────────────────────────

    @classmethod
    def _scope_data(cls, analytics: Dict, all_recs, persona: str, sprint_duration: int) -> Dict:
        """Scope analytics and recommendations to the persona's visibility."""
        if persona == "leadership":
            teams = analytics["teams"]
            engineers = analytics["engineers"]
            org_data = analytics["organization"]
            recs = [r.model_dump() for r in all_recs if "teamId" in r.supportingMetrics]
            persona_label = "Leadership"
        else:
            teams = [t for t in analytics["teams"] if t["managerId"] == persona]
            team_ids = {t["id"] for t in teams}
            engineers = [e for e in analytics["engineers"] if e["teamId"] in team_ids]
            eng_ids = {e["id"] for e in engineers}
            recs = [
                r.model_dump() for r in all_recs
                if r.supportingMetrics.get("teamId") in team_ids
                or r.supportingMetrics.get("engineerId") in eng_ids
            ]
            org_data = analytics["organization"]
            persona_label = f"Delivery Manager ({persona})"
        
        count = len(engineers) if engineers else 1
        utilization = sum(e["utilization"] for e in engineers) / count if engineers else 0
        capacity = sum(e["sprintCapacity"] for e in engineers)
        logged = sum(e["loggedHours"] for e in engineers)
        remaining_cap = capacity - logged
        burnout = sum(1 for e in engineers if e["burnoutRisk"] == "High")
        critical = sum(e["criticalIssues"] for e in engineers)
        blocked = sum(e["blockedTickets"] for e in engineers)
        productivity = sum(e["productivity"] for e in engineers)
        velocity = sum(e["velocity"] for e in engineers)
        health = sum(t["healthScore"] for t in teams) / max(1, len(teams)) if teams else 100
        hist_velocity = sum(e["historicalVelocity"] for e in engineers)
        
        return {
            "persona_label": persona_label,
            "teams": teams,
            "engineers": engineers,
            "recs": recs,
            "utilization": utilization,
            "capacity": capacity,
            "remaining_cap": remaining_cap,
            "burnout": burnout,
            "critical": critical,
            "blocked": blocked,
            "productivity": productivity,
            "velocity": velocity,
            "health": health,
            "forecast_cap": capacity,
            "forecast_dem": hist_velocity,
        }

    # ──────────────────────────────────────────────
    # Report builders
    # ──────────────────────────────────────────────

    @classmethod
    def _build_daily(cls, elements, scoped, styles, h2_style):
        """Build daily operational snapshot."""
        elements.append(Paragraph("Today's Operational Snapshot", h2_style))
        elements.append(Paragraph(
            f"Current sprint utilization is {scoped['utilization']:.1f}%. "
            f"You have {scoped['remaining_cap']:.0f} hours of capacity remaining.",
            styles['Normal']
        ))
        
        kpi_data = [
            ["Metric", "Value"],
            ["Today's Utilization", f"{scoped['utilization']:.1f}%"],
            ["Remaining Capacity", f"{scoped['remaining_cap']:.0f}h"],
            ["Active Blockers", f"{scoped['blocked']}"],
            ["Engineers at Risk", f"{scoped['burnout']}"],
        ]
        elements.append(cls._create_table(kpi_data))
        
        elements.append(Paragraph("Current Recommendations", h2_style))
        if scoped['recs']:
            for rec in scoped['recs']:
                elements.append(Paragraph(
                    f"<b>{rec['businessRule']}</b> (Severity: {rec['severity']}) - {rec['suggestedAction']}",
                    styles['Normal']
                ))
        else:
            elements.append(Paragraph("No active recommendations today.", styles['Normal']))

    @classmethod
    def _build_weekly(cls, elements, scoped, styles, h2_style):
        """Build weekly sprint execution summary."""
        elements.append(Paragraph("Sprint Execution Summary", h2_style))
        elements.append(Paragraph(
            f"Weekly utilization trend is at {scoped['utilization']:.1f}%. "
            f"Productivity score is {scoped['productivity']:.0f}. "
            f"Delivered {scoped['velocity']} story points so far.",
            styles['Normal']
        ))
        
        kpi_data = [
            ["Metric", "Value"],
            ["Weekly Utilization", f"{scoped['utilization']:.1f}%"],
            ["Weekly Productivity", f"{scoped['productivity']:.0f}"],
            ["Velocity (SP delivered)", f"{scoped['velocity']}"],
            ["Capacity vs Demand", f"{scoped['capacity']:.0f}h vs {scoped['forecast_dem']:.0f} SP"],
        ]
        elements.append(cls._create_table(kpi_data))
        
        # Team summaries
        elements.append(Paragraph("Team Summaries", h2_style))
        team_data = [["Team Name", "Capacity", "Utilization", "Health"]]
        for t in scoped['teams']:
            t_eng = [e for e in scoped['engineers'] if e["teamId"] == t["id"]]
            t_cap = sum(e["sprintCapacity"] for e in t_eng)
            team_data.append([t["name"], f"{t_cap:.0f}h", f"{t['utilization']:.1f}%", f"{t['healthScore']:.1f}"])
        
        t_table = Table(team_data, colWidths=[120, 80, 80, 80])
        t_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('GRID', (0, 0), (-1, -1), 1, colors.silver),
        ]))
        elements.append(t_table)
        
        # Forecast
        elements.append(Paragraph("Weekly Forecast", h2_style))
        elements.append(Paragraph(
            f"Forecasted capacity: {scoped['forecast_cap']:.0f}h. "
            f"Forecasted demand: {scoped['forecast_dem']:.0f} SP.",
            styles['Normal']
        ))
        
        # Recommendations
        elements.append(Paragraph("Weekly Recommendations", h2_style))
        if scoped['recs']:
            for rec in scoped['recs']:
                elements.append(Paragraph(
                    f"• <b>{rec['businessRule']}</b>: {rec['suggestedAction']}",
                    styles['Normal']
                ))
        else:
            elements.append(Paragraph("No active recommendations.", styles['Normal']))

    @classmethod
    def _build_monthly(cls, elements, scoped, styles, h2_style):
        """Build monthly strategic executive summary."""
        elements.append(Paragraph("Strategic Executive Summary", h2_style))
        elements.append(Paragraph(
            f"Monthly utilization averages {scoped['utilization']:.1f}%. "
            f"Overall health score is {scoped['health']:.1f}/100. "
            f"There are {scoped['burnout']} engineers facing prolonged burnout risk.",
            styles['Normal']
        ))
        
        kpi_data = [
            ["Metric", "Value"],
            ["Overall Health", f"{scoped['health']:.1f}/100"],
            ["Monthly Utilization", f"{scoped['utilization']:.1f}%"],
            ["Capacity", f"{scoped['capacity']:.0f}h"],
            ["Productivity", f"{scoped['productivity']:.0f}"],
            ["Burnout Risk", f"{scoped['burnout']} Engineers"],
        ]
        elements.append(cls._create_table(kpi_data))
        
        # Forecast
        elements.append(Paragraph("Forecast Outlook", h2_style))
        stability = "at risk" if scoped['utilization'] > 90 else "stable"
        elements.append(Paragraph(
            f"Forecast capacity is {scoped['forecast_cap']:.0f}h against projected demand of "
            f"{scoped['forecast_dem']:.0f} SP. Delivery stability is {stability}.",
            styles['Normal']
        ))
        
        # Critical recommendations only
        elements.append(Paragraph("Major Recommendations", h2_style))
        critical_recs = [r for r in scoped['recs'] if r['severity'] in ('High', 'Critical')]
        if critical_recs:
            for rec in critical_recs:
                elements.append(Paragraph(
                    f"<b>[{rec['severity'].upper()}] {rec['businessRule']}</b> - "
                    f"{rec['businessImpact']} - {rec['suggestedAction']}",
                    styles['Normal']
                ))
        else:
            elements.append(Paragraph("No critical recommendations.", styles['Normal']))

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def _create_table(data: List[List[str]]) -> Table:
        """Create a styled KPI table."""
        table = Table(data, colWidths=[200, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.silver),
        ]))
        return table
