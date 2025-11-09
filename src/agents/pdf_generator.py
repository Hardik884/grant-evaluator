from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from io import BytesIO
from datetime import datetime
import re


def generate_evaluation_report_pdf(evaluation_data: dict) -> BytesIO:
    """
    Generate a comprehensive PDF report for grant evaluation
    Returns a BytesIO buffer containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#1f2937'),
        alignment=TA_JUSTIFY,
        leading=14
    )
    
    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#6b7280'),
        leading=11
    )
    
    # ============================================================
    # SECTION 1: COVER PAGE
    # ============================================================
    
    # Title
    elements.append(Paragraph("Grant Evaluation Report", title_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f"<i>Domain: {evaluation_data.get('domain', 'Not Specified')}</i>", 
                              ParagraphStyle('DomainStyle', parent=normal_style, alignment=TA_CENTER, textColor=colors.HexColor('#6366f1'))))
    elements.append(Spacer(1, 1*cm))
    
    # Table of Contents
    elements.append(Paragraph("Table of Contents", heading_style))
    toc_data = [
        ['1.', 'Executive Summary'],
        ['2.', 'Narrative Summary'],
        ['3.', 'Detailed Score Breakdown'],
        ['4.', 'Critique Domains Analysis'],
        ['5.', 'Comprehensive Critique'],
        ['6.', 'Budget Analysis'],
    ]
    
    if evaluation_data.get('plagiarism_check'):
        toc_data.append(['7.', 'Plagiarism Check'])
    
    toc_table = Table(toc_data, colWidths=[1.5*cm, 15.5*cm])
    toc_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
    ]))
    elements.append(toc_table)
    elements.append(Spacer(1, 1*cm))
    
    # File Information
    elements.append(Paragraph("Document Information", heading_style))
    file_info_data = [
        ['File Name:', evaluation_data.get('file_name', 'N/A')],
        ['File Size:', f"{evaluation_data.get('file_size', 0) / 1024:.2f} KB"],
        ['Evaluation Date:', datetime.fromisoformat(evaluation_data.get('created_at', datetime.now().isoformat())).strftime('%Y-%m-%d %H:%M:%S')],
    ]
    
    file_info_table = Table(file_info_data, colWidths=[4*cm, 13*cm])
    file_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ]))
    elements.append(file_info_table)
    elements.append(Spacer(1, 1*cm))
    
    # Final Decision Banner
    decision = evaluation_data.get('decision', 'PENDING')
    decision_colors = {
        'ACCEPT': colors.HexColor('#10b981'),
        'REJECT': colors.HexColor('#ef4444'),
        'REVISE': colors.HexColor('#f59e0b'),
        'CONDITIONALLY ACCEPT': colors.HexColor('#06b6d4')
    }
    decision_color = decision_colors.get(decision, colors.grey)
    
    decision_data = [[Paragraph(f"<b>DECISION: {decision}</b>", ParagraphStyle(
        'DecisionStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.white,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))]]
    
    decision_table = Table(decision_data, colWidths=[17*cm])
    decision_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), decision_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    elements.append(decision_table)
    elements.append(Spacer(1, 1*cm))
    
    # Overall Score
    overall_score = evaluation_data.get('overall_score', 0)
    elements.append(Paragraph(f"Overall Score: {overall_score:.1f}/10", heading_style))
    
    # Score visualization
    # Determine color based on score
    if overall_score >= 8:
        bar_color = colors.HexColor('#10b981')
    elif overall_score >= 6:
        bar_color = colors.HexColor('#f59e0b')
    else:
        bar_color = colors.HexColor('#ef4444')
    
    # Draw filled score bar using drawing primitives
    score_percentage = max(0.0, min(overall_score / 10, 1.0))
    bar_width = 17 * cm
    bar_height = 0.8 * cm
    score_bar = Drawing(bar_width, bar_height)
    score_bar.add(Rect(0, 0, bar_width, bar_height, fillColor=colors.HexColor('#e5e7eb'), strokeColor=None))
    if score_percentage > 0:
        score_bar.add(Rect(0, 0, bar_width * score_percentage, bar_height, fillColor=bar_color, strokeColor=None))

    elements.append(score_bar)
    elements.append(Spacer(1, 0.3*cm))
    
    # Score text
    elements.append(Paragraph(f"<i>{overall_score:.1f}/10 — {get_score_description(overall_score)}</i>", normal_style))
    elements.append(Spacer(1, 1*cm))
    
    elements.append(PageBreak())
    
    # ============================================================
    # SECTION 2: NARRATIVE SUMMARY
    # ============================================================
    
    elements.append(Paragraph("2. Narrative Summary", heading_style))
    elements.append(Paragraph("Structured breakdown of grant proposal sections", small_style))
    elements.append(Spacer(1, 0.5*cm))
    
    summary_data = evaluation_data.get('summary', {})
    if summary_data and isinstance(summary_data, dict):
        for section_name, section_content in summary_data.items():
            if not isinstance(section_content, dict):
                continue
                
            # Format section name (e.g., "ExpectedOutcomes" -> "Expected Outcomes")
            formatted_section = re.sub(r'([a-z])([A-Z])', r'\1 \2', section_name) if isinstance(section_name, str) else section_name
            formatted_section = ' '.join([word.capitalize() if word.lower() not in ['and', 'of', 'the'] else word for word in formatted_section.split()])
            
            section_box = []
            section_box.append(Paragraph(f"<b>{formatted_section}</b>", subheading_style))
            
            # Text content
            text = section_content.get('text', '')
            if text and text != 'Not provided':
                section_box.append(Paragraph(text, normal_style))
                section_box.append(Spacer(1, 0.3*cm))
            
            # Pages
            pages = section_content.get('pages', [])
            if pages:
                pages_text = f"<b>Pages:</b> {', '.join(map(str, pages))}"
                section_box.append(Paragraph(pages_text, small_style))
                section_box.append(Spacer(1, 0.2*cm))
            
            # References
            references = section_content.get('references', [])
            if references and isinstance(references, list):
                section_box.append(Paragraph("<b>Key References:</b>", small_style))
                for ref in references[:5]:  # Limit to first 5 references
                    section_box.append(Paragraph(f"• {ref}", small_style))
                if len(references) > 5:
                    section_box.append(Paragraph(f"<i>... and {len(references) - 5} more</i>", small_style))
                section_box.append(Spacer(1, 0.2*cm))
            
            # Notes
            notes = section_content.get('notes', '')
            if notes:
                if isinstance(notes, list):
                    section_box.append(Paragraph("<b>Notes:</b>", small_style))
                    for note in notes:
                        section_box.append(Paragraph(f"• {note}", small_style))
                elif isinstance(notes, str) and notes:
                    section_box.append(Paragraph(f"<b>Notes:</b> {notes}", small_style))
            
            # Add the section as a KeepTogether block
            elements.append(KeepTogether(section_box))
            elements.append(Spacer(1, 0.5*cm))
    else:
        elements.append(Paragraph("<i>No narrative summary available for this evaluation.</i>", normal_style))
    
    elements.append(PageBreak())
    
    # ============================================================
    # SECTION 3: DETAILED SCORES
    # ============================================================
    
    # Detailed Scores
    elements.append(Paragraph("3. Detailed Score Breakdown", heading_style))
    scores = evaluation_data.get('scores', [])
    
    if scores:
        score_data = [['Category', 'Score', 'Max', 'Percentage']]
        for score_item in scores:
            category = score_item.get('category', 'N/A')
            score = score_item.get('score', 0)
            max_score = score_item.get('maxScore', 10)
            percentage = (score / max_score * 100) if max_score > 0 else 0
            score_data.append([category, str(score), str(max_score), f"{percentage:.1f}%"])
        
        score_table = Table(score_data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        elements.append(score_table)
        
        # Add strengths and weaknesses
        elements.append(Spacer(1, 0.8*cm))
        for score_item in scores:
            category = score_item.get('category', 'N/A')
            elements.append(Paragraph(f"<b>{category}</b>", subheading_style))
            
            strengths = score_item.get('strengths') or []
            if not strengths:
                strengths = ['No standout strengths recorded.']
            if strengths:
                elements.append(Paragraph("<b>Strengths:</b>", normal_style))
                for strength in strengths:
                    elements.append(Paragraph(f"• {strength}", normal_style))
            
            weaknesses = score_item.get('weaknesses') or []
            if not weaknesses:
                weaknesses = ['No critical weaknesses identified.']
            if weaknesses:
                elements.append(Paragraph("<b>Weaknesses:</b>", normal_style))
                for weakness in weaknesses:
                    elements.append(Paragraph(f"• {weakness}", normal_style))
            
            elements.append(Spacer(1, 0.5*cm))
    
    elements.append(PageBreak())
    
    # ============================================================
    # SECTION 4: CRITIQUE DOMAINS ANALYSIS
    # ============================================================
    
    elements.append(Paragraph("4. Critique Domains Analysis", heading_style))
    critique_domains = evaluation_data.get('critique_domains', [])
    
    if critique_domains:
        domains_data = [['Domain', 'Score']]
        for domain in critique_domains:
            domain_name = domain.get('domain') or domain.get('name', 'N/A')
            domain_score = domain.get('score', 0)
            domains_data.append([domain_name, f"{domain_score:.2f}/10"])
        
        domains_table = Table(domains_data, colWidths=[12*cm, 5*cm])
        domains_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        elements.append(domains_table)
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph("<i>These domain scores reflect comprehensive evaluation across scientific rigor, feasibility, clarity, alignment, persuasiveness, ethics, and innovation.</i>", small_style))
    else:
        elements.append(Paragraph("<i>No critique domain data available.</i>", normal_style))
    
    elements.append(Spacer(1, 1*cm))
    elements.append(PageBreak())
    
    # ============================================================
    # SECTION 5: COMPREHENSIVE CRITIQUE
    # ============================================================
    
    # Full Critique
    elements.append(Paragraph("5. Comprehensive Critique", heading_style))
    full_critique = evaluation_data.get('full_critique', {})
    
    if full_critique:
        # Summary
        summary = full_critique.get('summary') if isinstance(full_critique, dict) else None
        if not isinstance(summary, str) or not summary.strip():
            summary = 'No executive summary was generated.'
        elements.append(Paragraph("<b>Executive Summary:</b>", subheading_style))
        elements.append(Paragraph(summary, normal_style))
        elements.append(Spacer(1, 0.8*cm))
        
        # Issues
        issues = full_critique.get('issues', [])
        if issues:
            elements.append(Paragraph("<b>Issues Identified:</b>", subheading_style))
            for issue in issues:
                severity = issue.get('severity', 'medium')
                severity_colors_map = {
                    'high': colors.HexColor('#ef4444'),
                    'medium': colors.HexColor('#f59e0b'),
                    'low': colors.HexColor('#3b82f6')
                }
                severity_color = severity_colors_map.get(severity, colors.grey)
                
                category = issue.get('category', 'General')
                description = issue.get('description', 'No description.')
                
                issue_text = f"<b>[{severity.upper()}]</b> <b>{category}:</b> {description}"
                elements.append(Paragraph(issue_text, normal_style))
                elements.append(Spacer(1, 0.3*cm))
            
            elements.append(Spacer(1, 0.5*cm))
        
        # Recommendations
        recommendations = full_critique.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("<b>Recommendations:</b>", subheading_style))
            for rec in recommendations:
                priority = rec.get('priority', 'medium')
                recommendation = rec.get('recommendation', 'No recommendation.')
                
                rec_text = f"<b>[{priority.upper()} Priority]</b> {recommendation}"
                elements.append(Paragraph(rec_text, normal_style))
                elements.append(Spacer(1, 0.3*cm))
    
    elements.append(Spacer(1, 1*cm))
    
    # ============================================================
    # SECTION 6: BUDGET ANALYSIS
    # ============================================================
    
    # Budget Analysis
    elements.append(Paragraph("6. Budget Analysis", heading_style))
    budget_analysis = evaluation_data.get('budget_analysis', {})
    
    if budget_analysis:
        total_budget = budget_analysis.get('totalBudget', 0)
        elements.append(Paragraph(f"<b>Total Budget:</b> ${total_budget:,.2f}", normal_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Budget breakdown
        breakdown = budget_analysis.get('breakdown', [])
        if breakdown:
            budget_data = [['Category', 'Amount', 'Percentage']]
            for item in breakdown:
                category = item.get('category', 'N/A')
                amount = item.get('amount', 0)
                percentage = item.get('percentage', 0)
                budget_data.append([category, f"${amount:,.2f}", f"{percentage:.1f}%"])
            
            budget_table = Table(budget_data, colWidths=[8*cm, 5*cm, 4*cm])
            budget_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            elements.append(budget_table)
            elements.append(Spacer(1, 0.8*cm))
        
        # Budget flags
        flags = budget_analysis.get('flags', [])
        if flags:
            elements.append(Paragraph("<b>Budget Flags:</b>", subheading_style))
            for flag in flags:
                flag_type = flag.get('type', 'info')
                message = flag.get('message', 'No message.')
                
                flag_colors_map = {
                    'error': colors.HexColor('#ef4444'),
                    'warning': colors.HexColor('#f59e0b'),
                    'info': colors.HexColor('#3b82f6')
                }
                
                flag_text = f"<b>[{flag_type.upper()}]</b> {message}"
                elements.append(Paragraph(flag_text, normal_style))
                elements.append(Spacer(1, 0.3*cm))
            
            elements.append(Spacer(1, 0.5*cm))
        
        # Budget summary
        budget_summary = budget_analysis.get('summary', '')
        if budget_summary:
            elements.append(Paragraph("<b>Budget Summary:</b>", subheading_style))
            elements.append(Paragraph(budget_summary, normal_style))
    
    # ============================================================
    # SECTION 7: PLAGIARISM CHECK (if available)
    # ============================================================
    
    plagiarism_check = evaluation_data.get('plagiarism_check')
    if plagiarism_check:
        elements.append(Spacer(1, 1*cm))
        elements.append(PageBreak())
        elements.append(Paragraph("7. Plagiarism Check", heading_style))
        
        risk_level = plagiarism_check.get('risk_level', 'UNKNOWN')
        similarity_score = plagiarism_check.get('similarity_score')
        matched_text = plagiarism_check.get('matched_reference_text')
        error = plagiarism_check.get('error')
        
        # Risk level indicator
        risk_colors = {
            'HIGH': colors.HexColor('#ef4444'),
            'MEDIUM': colors.HexColor('#f59e0b'),
            'LOW': colors.HexColor('#10b981'),
            'UNKNOWN': colors.HexColor('#6b7280')
        }
        risk_color = risk_colors.get(risk_level, colors.grey)
        
        risk_data = [[Paragraph(f"<b>Risk Level: {risk_level}</b>", ParagraphStyle(
            'RiskStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))]]
        
        risk_table = Table(risk_data, colWidths=[17*cm])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), risk_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(risk_table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Similarity score
        if similarity_score is not None:
            elements.append(Paragraph(f"<b>Similarity Score:</b> {similarity_score:.2%}", normal_style))
            elements.append(Spacer(1, 0.3*cm))
        
        # Matched reference text
        if matched_text:
            elements.append(Paragraph("<b>Matched Reference Text:</b>", subheading_style))
            elements.append(Paragraph(matched_text, normal_style))
            elements.append(Spacer(1, 0.5*cm))
        
        # Error message
        if error:
            elements.append(Paragraph(f"<b>Note:</b> {error}", ParagraphStyle(
                'ErrorStyle',
                parent=normal_style,
                textColor=colors.HexColor('#ef4444')
            )))
        
        # Interpretation
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph("<b>Interpretation:</b>", subheading_style))
        
        if risk_level == 'LOW':
            interpretation = "The content shows minimal similarity to reference materials. This is within acceptable range for original work."
        elif risk_level == 'MEDIUM':
            interpretation = "The content shows moderate similarity to reference materials. Review recommended to ensure proper citation and attribution."
        elif risk_level == 'HIGH':
            interpretation = "The content shows significant similarity to reference materials. Detailed review required to assess originality and proper citation."
        else:
            interpretation = "Plagiarism check could not be completed or data is unavailable."
        
        elements.append(Paragraph(interpretation, normal_style))
    
    # ============================================================
    # FOOTER: Report Generation Info
    # ============================================================
    
    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph(
        f"<i>Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</i>",
        ParagraphStyle('FooterStyle', parent=small_style, alignment=TA_CENTER, textColor=colors.HexColor('#9ca3af'))
    ))
    elements.append(Paragraph(
        "<i>Powered by AI Grant Evaluator</i>",
        ParagraphStyle('PoweredStyle', parent=small_style, alignment=TA_CENTER, textColor=colors.HexColor('#9ca3af'))
    ))
    
    # Build PDF
    doc.build(elements)
    
    # Reset buffer position to beginning
    buffer.seek(0)
    return buffer


def get_score_description(score: float) -> str:
    """Get a text description based on the score"""
    if score >= 9:
        return "Excellent - Highly Recommended"
    elif score >= 8:
        return "Very Good - Recommended"
    elif score >= 7:
        return "Good - Consider with Minor Revisions"
    elif score >= 6:
        return "Satisfactory - Major Revisions Needed"
    elif score >= 5:
        return "Below Average - Significant Concerns"
    else:
        return "Poor - Not Recommended"
