"""
Proposal generation service with PDF and web view
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import os

logger = logging.getLogger(__name__)


class ProposalService:
    """Service for generating and managing proposals"""
    
    def __init__(self, config):
        self.upload_folder = config.UPLOAD_FOLDER
        self.backend_url = config.BACKEND_URL
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def generate_proposal_pdf(
        self,
        proposal_id: int,
        lead_data: Dict[str, Any],
        proposal_data: Dict[str, Any]
    ) -> str:
        """
        Generate PDF proposal
        Returns: filepath to generated PDF
        """
        try:
            filename = f"proposal_{proposal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(self.upload_folder, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Container for PDF elements
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#0066cc'),
                spaceAfter=30,
                alignment=1  # Center
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#333333'),
                spaceAfter=12
            )
            
            # Title
            story.append(Paragraph("PROPOSTA COMERCIAL", title_style))
            story.append(Spacer(1, 0.5*cm))
            
            # Client info
            story.append(Paragraph("Dados do Cliente", heading_style))
            client_data = [
                ["Nome:", lead_data.get('name', 'N/A')],
                ["Telefone:", lead_data.get('phone', 'N/A')],
                ["Email:", lead_data.get('email', 'N/A')],
                ["Localização:", f"{lead_data.get('neighborhood', '')}, {lead_data.get('city', '')}"],
            ]
            
            client_table = Table(client_data, colWidths=[4*cm, 12*cm])
            client_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            
            story.append(client_table)
            story.append(Spacer(1, 1*cm))
            
            # Proposal details
            story.append(Paragraph(proposal_data.get('title', 'Proposta de Serviço'), heading_style))
            
            if proposal_data.get('description'):
                story.append(Paragraph(proposal_data['description'], styles['BodyText']))
                story.append(Spacer(1, 0.5*cm))
            
            # Service items
            story.append(Paragraph("Itens do Serviço", heading_style))
            
            service_items = proposal_data.get('service_items', [])
            if service_items:
                items_data = [["Item", "Descrição", "Valor"]]
                
                for item in service_items:
                    items_data.append([
                        item.get('name', ''),
                        item.get('description', ''),
                        f"R$ {item.get('value', 0):.2f}"
                    ])
                
                items_table = Table(items_data, colWidths=[4*cm, 8*cm, 4*cm])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
                ]))
                
                story.append(items_table)
                story.append(Spacer(1, 0.5*cm))
            
            # Total value
            total_data = [
                ["VALOR TOTAL:", f"R$ {proposal_data.get('total_value', 0):.2f}"]
            ]
            
            total_table = Table(total_data, colWidths=[12*cm, 4*cm])
            total_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0066cc')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            story.append(total_table)
            story.append(Spacer(1, 1*cm))
            
            # Validity
            if proposal_data.get('valid_until'):
                valid_until = datetime.fromisoformat(proposal_data['valid_until'].replace('Z', '+00:00'))
                validity_text = f"<b>Validade:</b> Esta proposta é válida até {valid_until.strftime('%d/%m/%Y')}"
                story.append(Paragraph(validity_text, styles['BodyText']))
                story.append(Spacer(1, 0.5*cm))
            
            # Footer
            footer_text = """
            <br/><br/>
            Para aceitar esta proposta, clique no link de aceitação enviado via WhatsApp.<br/>
            <br/>
            Obrigado pela preferência!
            """
            story.append(Paragraph(footer_text, styles['BodyText']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF proposal generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate PDF proposal: {str(e)}")
            raise
    
    def create_proposal(
        self,
        lead_id: int,
        title: str,
        description: str,
        service_items: List[Dict[str, Any]],
        total_value: float,
        validity_days: int = 7
    ) -> Dict[str, Any]:
        """
        Create a new proposal with PDF and web view
        """
        from app.models import db, Proposal, Lead
        
        try:
            # Get lead data
            lead = Lead.query.get(lead_id)
            if not lead:
                raise ValueError(f"Lead {lead_id} not found")
            
            # Calculate validity
            valid_until = datetime.utcnow() + timedelta(days=validity_days)
            
            # Create proposal record
            proposal = Proposal(
                lead_id=lead_id,
                title=title,
                description=description,
                service_items=service_items,
                total_value=total_value,
                valid_until=valid_until,
                status='pending'
            )
            
            db.session.add(proposal)
            db.session.flush()  # Get proposal ID
            
            # Generate PDF
            pdf_filename = self.generate_proposal_pdf(
                proposal.id,
                lead.to_dict(),
                {
                    'title': title,
                    'description': description,
                    'service_items': service_items,
                    'total_value': total_value,
                    'valid_until': valid_until.isoformat()
                }
            )
            
            # Set URLs
            proposal.pdf_url = f"{self.backend_url}/uploads/{pdf_filename}"
            proposal.view_url = f"{self.backend_url}/proposal/{proposal.id}/view"
            
            db.session.commit()
            
            logger.info(f"Proposal created successfully: {proposal.id}")
            return proposal.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create proposal: {str(e)}")
            raise
    
    def accept_proposal(self, proposal_id: int) -> Dict[str, Any]:
        """Mark proposal as accepted"""
        from app.models import db, Proposal
        
        try:
            proposal = Proposal.query.get(proposal_id)
            if not proposal:
                raise ValueError(f"Proposal {proposal_id} not found")
            
            if proposal.status != 'pending':
                raise ValueError(f"Proposal is already {proposal.status}")
            
            # Check if expired
            if proposal.valid_until and datetime.utcnow() > proposal.valid_until:
                proposal.status = 'expired'
                db.session.commit()
                raise ValueError("Proposal has expired")
            
            proposal.status = 'accepted'
            proposal.accepted_at = datetime.utcnow()
            
            # Update lead status
            proposal.lead.status = 'accepted'
            proposal.lead.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Proposal {proposal_id} accepted")
            return proposal.to_dict()
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to accept proposal: {str(e)}")
            raise
