"""
API Routes for Lead Management
"""
from flask import Blueprint, request, jsonify
from app.models import db, Lead, Conversation
from app.services import WhatsAppService, AILeadAgent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

leads_bp = Blueprint('leads', __name__, url_prefix='/api/leads')


@leads_bp.route('', methods=['GET'])
def list_leads():
    """List leads with filtering"""
    try:
        # Get query parameters
        neighborhood = request.args.get('neighborhood')
        status = request.args.get('status')
        temperature = request.args.get('temperature')
        source = request.args.get('source')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = Lead.query
        
        if neighborhood:
            query = query.filter(Lead.neighborhood == neighborhood)
        if status:
            query = query.filter(Lead.status == status)
        if temperature:
            query = query.filter(Lead.temperature == temperature)
        if source:
            query = query.filter(Lead.source == source)
        
        # Order by most recent
        query = query.order_by(Lead.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'leads': [lead.to_dict() for lead in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error listing leads: {str(e)}")
        return jsonify({'error': str(e)}), 500


@leads_bp.route('/<int:lead_id>', methods=['GET'])
def get_lead(lead_id):
    """Get single lead with full details"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        
        # Include related data
        lead_data = lead.to_dict()
        lead_data['conversations'] = [conv.to_dict() for conv in lead.conversations]
        lead_data['proposals'] = [prop.to_dict() for prop in lead.proposals]
        lead_data['follow_ups'] = [fu.to_dict() for fu in lead.follow_ups]
        
        return jsonify(lead_data)
        
    except Exception as e:
        logger.error(f"Error getting lead: {str(e)}")
        return jsonify({'error': str(e)}), 500


@leads_bp.route('', methods=['POST'])
def create_lead():
    """Create new lead (from landing page form)"""
    try:
        data = request.get_json()
        
        # Check if lead already exists
        existing_lead = Lead.query.filter_by(phone=data['phone']).first()
        if existing_lead:
            return jsonify({
                'message': 'Lead already exists',
                'lead': existing_lead.to_dict()
            }), 200
        
        # Create new lead
        lead = Lead(
            name=data['name'],
            phone=data['phone'],
            email=data.get('email'),
            neighborhood=data.get('neighborhood'),
            city=data.get('city'),
            state=data.get('state'),
            address=data.get('address'),
            source=data.get('source', 'landing_page'),
            utm_source=data.get('utm_source'),
            utm_medium=data.get('utm_medium'),
            utm_campaign=data.get('utm_campaign'),
            utm_content=data.get('utm_content'),
            utm_term=data.get('utm_term'),
            landing_page_id=data.get('landing_page_id'),
            notes=data.get('notes')
        )
        
        db.session.add(lead)
        db.session.commit()
        
        logger.info(f"New lead created: {lead.id}")
        
        return jsonify({
            'message': 'Lead created successfully',
            'lead': lead.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating lead: {str(e)}")
        return jsonify({'error': str(e)}), 500


@leads_bp.route('/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Update lead information"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'name', 'email', 'neighborhood', 'city', 'state', 'address',
            'status', 'score', 'temperature', 'notes', 'assigned_to'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(lead, field, data[field])
        
        lead.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Lead updated: {lead.id}")
        
        return jsonify({
            'message': 'Lead updated successfully',
            'lead': lead.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating lead: {str(e)}")
        return jsonify({'error': str(e)}), 500


@leads_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get lead statistics"""
    try:
        total_leads = Lead.query.count()
        
        # By temperature
        hot_leads = Lead.query.filter_by(temperature='hot').count()
        warm_leads = Lead.query.filter_by(temperature='warm').count()
        cold_leads = Lead.query.filter_by(temperature='cold').count()
        
        # By status
        new_leads = Lead.query.filter_by(status='new').count()
        contacted_leads = Lead.query.filter_by(status='contacted').count()
        qualified_leads = Lead.query.filter_by(status='qualified').count()
        proposal_sent = Lead.query.filter_by(status='proposal_sent').count()
        accepted = Lead.query.filter_by(status='accepted').count()
        
        # By source
        from sqlalchemy import func
        source_stats = db.session.query(
            Lead.source,
            func.count(Lead.id)
        ).group_by(Lead.source).all()
        
        # By neighborhood
        neighborhood_stats = db.session.query(
            Lead.neighborhood,
            func.count(Lead.id)
        ).group_by(Lead.neighborhood).all()
        
        # Conversion rate
        conversion_rate = (accepted / total_leads * 100) if total_leads > 0 else 0
        
        return jsonify({
            'total_leads': total_leads,
            'by_temperature': {
                'hot': hot_leads,
                'warm': warm_leads,
                'cold': cold_leads
            },
            'by_status': {
                'new': new_leads,
                'contacted': contacted_leads,
                'qualified': qualified_leads,
                'proposal_sent': proposal_sent,
                'accepted': accepted
            },
            'by_source': dict(source_stats),
            'by_neighborhood': dict(neighborhood_stats),
            'conversion_rate': round(conversion_rate, 2)
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
