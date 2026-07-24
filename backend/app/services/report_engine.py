import io
from datetime import datetime
from typing import Dict, Any
from app.services.analytics_engine import AnalyticsEngine
from app.services.recommendation_engine import RecommendationEngine

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
except ImportError:
    pass

class ReportEngine:
    
    @classmethod
    def generate_pdf_report(cls, report_type: str, persona: str = "leadership") -> bytes:
        analytics = AnalyticsEngine.get_analytics()
        all_recs = RecommendationEngine.get_recommendations()
        
        # Scope Data
        if persona == "leadership":
            teams = analytics["teams"]
            engineers = analytics["engineers"]
            org_data = analytics["organization"]
            recs = [r.model_dump() for r in all_recs if "teamId" in r.supportingMetrics]
            persona_label = "Leadership"
            utilization = org_data.get("overallUtilization", 0)
            capacity = sum(e["availableHours"] * 2 for e in engineers)
            remaining_cap = capacity - sum(e.get("loggedHours", 0) for e in engineers)
            burnout = org_data.get("burnoutRiskCount", 0)
            critical = org_data.get("criticalJiraIssues", 0)
            blocked = org_data.get("blockedIssues", 0)
            deps = org_data.get("dependencyRisks", 0)
            forecast_cap = capacity
            forecast_dem = sum(e.get("historicalVelocity", e.get("velocity", 0)) for e in engineers)
            productivity = org_data.get("overallProductivity", 0)
            health = org_data.get("overallTeamHealth", 100)
            velocity = sum(e.get("velocity", 0) for e in engineers)
        else:
            teams = [t for t in analytics["teams"] if t["managerId"] == persona]
            team_ids = [t["id"] for t in teams]
            engineers = [e for e in analytics["engineers"] if e["teamId"] in team_ids]
            recs = [r.model_dump() for r in all_recs if r.supportingMetrics.get("teamId") in team_ids or r.supportingMetrics.get("engineerId") in [e["id"] for e in engineers]]
            persona_label = f"Delivery Manager ({persona})"
            utilization = sum(e["utilization"] for e in engineers) / max(1, len(engineers))
            capacity = sum(e["availableHours"] * 2 for e in engineers)
            remaining_cap = capacity - sum(e.get("loggedHours", 0) for e in engineers)
            burnout = sum(1 for e in engineers if e["utilization"] > 95)
            critical = sum(e["criticalIssues"] for e in engineers)
            blocked = sum(e.get("blockedTickets", 0) for e in engineers)
            deps = sum(t["dependencyRisk"] for t in teams)
            forecast_cap = capacity
            forecast_dem = sum(e.get("historicalVelocity", e.get("velocity", 0)) for e in engineers)
            productivity = sum(e["productivity"] for e in engineers)
            health = sum(t["healthScore"] for t in teams) / max(1, len(teams))
            velocity = sum(e.get("velocity", 0) for e in engineers)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=24, spaceAfter=20, textColor=colors.HexColor("#1A202C"))
        h2_style = ParagraphStyle('H2Style', parent=styles['Heading2'], fontSize=16, spaceBefore=15, spaceAfter=10, textColor=colors.HexColor("#2D3748"))
        
        elements = []
        
        # Cover Page
        report_title = f"{report_type.capitalize()} Management Report"
        elements.append(Paragraph(report_title, title_style))
        elements.append(Paragraph(f"<b>Organization:</b> Global Engineering Corp", styles['Normal']))
        elements.append(Paragraph(f"<b>Reporting Period:</b> {report_type.capitalize()}", styles['Normal']))
        elements.append(Paragraph(f"<b>Generated At:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"<b>Persona:</b> {persona_label}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        if report_type == "daily":
            # Daily Report
            elements.append(Paragraph("Today's Operational Snapshot", h2_style))
            elements.append(Paragraph(f"Current sprint utilization is {utilization:.1f}%. You have {remaining_cap} hours of capacity remaining.", styles['Normal']))
            
            kpi_data = [
                ["Metric", "Value"],
                ["Today's Utilization", f"{utilization:.1f}%"],
                ["Remaining Capacity", f"{remaining_cap}h"],
                ["Active Blockers", f"{blocked}"],
                ["Engineers at Risk", f"{burnout}"]
            ]
            kpi_table = Table(kpi_data, colWidths=[200, 150])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.silver),
            ]))
            elements.append(kpi_table)
            
            elements.append(Paragraph("Current Recommendations", h2_style))
            if recs:
                for rec in recs:
                    elements.append(Paragraph(f"<b>{rec['businessRule']}</b> (Severity: {rec['severity']}) - {rec['suggestedAction']}", styles['Normal']))
            else:
                elements.append(Paragraph("No active recommendations today.", styles['Normal']))
                
        elif report_type == "weekly":
            # Weekly Report
            elements.append(Paragraph("Sprint Execution Summary", h2_style))
            elements.append(Paragraph(f"Weekly utilization trend is steady at {utilization:.1f}%. Productivity score is {productivity}. Delivered {velocity} story points so far.", styles['Normal']))
            
            kpi_data = [
                ["Metric", "Value"],
                ["Weekly Utilization", f"{utilization:.1f}%"],
                ["Weekly Productivity", f"{productivity}"],
                ["Velocity (SP delivered)", f"{velocity}"],
                ["Capacity vs Demand", f"{capacity}h vs {forecast_dem} SP"]
            ]
            kpi_table = Table(kpi_data, colWidths=[200, 150])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
                ('GRID', (0, 0), (-1, -1), 1, colors.silver),
            ]))
            elements.append(kpi_table)
            
            elements.append(Paragraph("Team Summaries", h2_style))
            team_data = [["Team Name", "Capacity", "Utilization", "Health"]]
            for t in teams:
                t_cap = sum(e["availableHours"] * 2 for e in engineers if e["teamId"] == t["id"])
                team_data.append([t["name"], f"{t_cap}h", f"{t['utilization']:.1f}%", f"{t['healthScore']:.1f}"])
            t_table = Table(team_data, colWidths=[120, 80, 80, 80])
            t_table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")), ('GRID', (0, 0), (-1, -1), 1, colors.silver)]))
            elements.append(t_table)
            
            elements.append(Paragraph("Weekly Forecast", h2_style))
            elements.append(Paragraph(f"Forecasted capacity: {forecast_cap}h. Forecasted demand: {forecast_dem} SP.", styles['Normal']))
            
            elements.append(Paragraph("Weekly Recommendations", h2_style))
            if recs:
                for rec in recs:
                    elements.append(Paragraph(f"• <b>{rec['businessRule']}</b>: {rec['suggestedAction']}", styles['Normal']))
            else:
                elements.append(Paragraph("No active recommendations.", styles['Normal']))
                
        else: # monthly
            # Monthly Report
            elements.append(Paragraph("Strategic Executive Summary", h2_style))
            elements.append(Paragraph(f"Monthly utilization averages {utilization:.1f}%. Overall health score is {health:.1f}/100. There are {burnout} engineers facing prolonged burnout risk. Historical capacity remains aligned with demand trends.", styles['Normal']))
            
            kpi_data = [
                ["Metric", "Value"],
                ["Overall Health", f"{health:.1f}/100"],
                ["Monthly Utilization", f"{utilization:.1f}%"],
                ["Historical Capacity", f"{capacity}h"],
                ["Productivity Trend", f"{productivity}"],
                ["Burnout Evolution", f"{burnout} Engineers"]
            ]
            kpi_table = Table(kpi_data, colWidths=[200, 150])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#1A202C")),
                ('GRID', (0, 0), (-1, -1), 1, colors.silver),
            ]))
            elements.append(kpi_table)
            
            elements.append(Paragraph("Forecast Outlook", h2_style))
            elements.append(Paragraph(f"Long-term forecast capacity is {forecast_cap}h against a projected demand of {forecast_dem} SP. Delivery stability is {'at risk' if utilization > 90 else 'stable'}.", styles['Normal']))
            
            elements.append(Paragraph("Major Recommendations", h2_style))
            if recs:
                for rec in recs:
                    if rec['severity'] in ['High', 'Critical']:
                        elements.append(Paragraph(f"<b>[CRITICAL] {rec['businessRule']}</b> - {rec['businessImpact']} - {rec['suggestedAction']}", styles['Normal']))
            else:
                elements.append(Paragraph("No critical recommendations.", styles['Normal']))

        # Appendix
        elements.append(Paragraph("Appendix", h2_style))
        elements.append(Paragraph("Dataset: Static Simulation (CUIA POC)", styles['Normal']))
        elements.append(Paragraph(f"Generated Timestamp: {datetime.now().isoformat()}", styles['Normal']))
        
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
