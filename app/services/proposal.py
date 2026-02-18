from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime, timedelta
import qrcode
from io import BytesIO
import os
from typing import Dict, Any
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ProposalService:
    """Service for generating proposals"""
    
    def __init__(self):
        self.media_dir = "/app/media/proposals"
        os.makedirs(self.media_dir, exist_ok=True)
    
    def generate_proposal_pdf(
        self,
        proposal_id: int,
        lead_name: str,
        lead_neighborhood: str,
        title: str,
        description: str,
        amount: float,
        expires_in_days: int = 7
    ) -> str:
        """Generate proposal PDF"""
        filename = f"proposal_{proposal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.media_dir, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a472a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2d5f3d'),
            spaceAfter=12
        )
        
        # Title
        story.append(Paragraph("PROPOSTA COMERCIAL", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Client info
        story.append(Paragraph("Dados do Cliente", header_style))
        client_data = [
            ["Cliente:", lead_name],
            ["Bairro:", lead_neighborhood],
            ["Data:", datetime.now().strftime("%d/%m/%Y")],
            ["Validade:", (datetime.now() + timedelta(days=expires_in_days)).strftime("%d/%m/%Y")]
        ]
        
        client_table = Table(client_data, colWidths=[2*inch, 4*inch])
        client_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(client_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Proposal details
        story.append(Paragraph("Detalhes da Proposta", header_style))
        story.append(Paragraph(f"<b>{title}</b>", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(description, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Amount
        amount_style = ParagraphStyle(
            'Amount',
            parent=styles['Normal'],
            fontSize=20,
            textColor=colors.HexColor('#1a472a'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(f"Valor Total: R$ {amount:,.2f}", amount_style))
        story.append(Spacer(1, 0.4*inch))
        
        # QR Code for acceptance link
        acceptance_link = f"{settings.BASE_URL}/api/proposals/{proposal_id}/accept"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(acceptance_link)
        qr.make(fit=True)
        
        story.append(Paragraph("Aceite da Proposta", header_style))
        story.append(Paragraph(
            "Escaneie o QR Code abaixo ou acesse o link para aceitar esta proposta:",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"Link: {acceptance_link}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        logger.info(f"Proposal PDF generated: {filepath}")
        
        return filepath
    
    def generate_proposal_link(self, proposal_id: int) -> str:
        """Generate web link for proposal acceptance"""
        return f"{settings.BASE_URL}/proposals/{proposal_id}"
    
    def generate_acceptance_page(
        self,
        proposal_id: int,
        lead_name: str,
        title: str,
        amount: float
    ) -> str:
        """Generate HTML for proposal acceptance page"""
        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aceitar Proposta</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #1a472a;
                    text-align: center;
                }}
                .info {{
                    margin: 20px 0;
                    padding: 15px;
                    background-color: #f9f9f9;
                    border-left: 4px solid #1a472a;
                }}
                .amount {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #1a472a;
                    text-align: center;
                    margin: 30px 0;
                }}
                .button {{
                    display: block;
                    width: 100%;
                    padding: 15px;
                    background-color: #1a472a;
                    color: white;
                    text-align: center;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 18px;
                    border: none;
                    cursor: pointer;
                }}
                .button:hover {{
                    background-color: #2d5f3d;
                }}
                .success {{
                    display: none;
                    text-align: center;
                    color: #1a472a;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Proposta Comercial</h1>
                <div class="info">
                    <p><strong>Cliente:</strong> {lead_name}</p>
                    <p><strong>Proposta:</strong> {title}</p>
                </div>
                <div class="amount">
                    R$ {amount:,.2f}
                </div>
                <button class="button" onclick="acceptProposal()">
                    ✓ ACEITAR PROPOSTA
                </button>
                <div class="success" id="success">
                    <h2>✓ Proposta Aceita!</h2>
                    <p>Obrigado! Entraremos em contato em breve.</p>
                </div>
            </div>
            <script>
                async function acceptProposal() {{
                    try {{
                        const response = await fetch('/api/proposals/{proposal_id}/accept', {{
                            method: 'POST',
                            headers: {{'Content-Type': 'application/json'}}
                        }});
                        if (response.ok) {{
                            document.querySelector('.info').style.display = 'none';
                            document.querySelector('.amount').style.display = 'none';
                            document.querySelector('.button').style.display = 'none';
                            document.getElementById('success').style.display = 'block';
                        }}
                    }} catch (error) {{
                        alert('Erro ao aceitar proposta. Tente novamente.');
                    }}
                }}
            </script>
        </body>
        </html>
        """
        return html


# Singleton instance
proposal_service = ProposalService()
