"""
API Routes for Proposals
"""
from flask import Blueprint, request, jsonify, render_template, send_file
from app.models import db, Proposal, Lead
from app.services import ProposalService
from flask import current_app
import logging
import os

logger = logging.getLogger(__name__)

proposals_bp = Blueprint('proposals', __name__)


@proposals_bp.route('/api/proposals', methods=['POST'])
def create_proposal():
    """Create new proposal"""
    try:
        data = request.get_json()
        
        proposal_service = ProposalService(current_app.config)
        
        proposal = proposal_service.create_proposal(
            lead_id=data['lead_id'],
            title=data['title'],
            description=data.get('description', ''),
            service_items=data.get('service_items', []),
            total_value=data['total_value'],
            validity_days=data.get('validity_days', 7)
        )
        
        return jsonify({
            'message': 'Proposal created successfully',
            'proposal': proposal
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating proposal: {str(e)}")
        return jsonify({'error': str(e)}), 500


@proposals_bp.route('/api/proposals/<int:proposal_id>', methods=['GET'])
def get_proposal(proposal_id):
    """Get proposal details"""
    try:
        proposal = Proposal.query.get_or_404(proposal_id)
        return jsonify(proposal.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting proposal: {str(e)}")
        return jsonify({'error': str(e)}), 500


@proposals_bp.route('/proposal/<int:proposal_id>/view', methods=['GET'])
def view_proposal(proposal_id):
    """View proposal in browser"""
    try:
        proposal = Proposal.query.get_or_404(proposal_id)
        lead = proposal.lead
        
        return render_template(
            'proposal_view.html',
            proposal=proposal,
            lead=lead
        )
        
    except Exception as e:
        logger.error(f"Error viewing proposal: {str(e)}")
        return "Proposta não encontrada", 404


@proposals_bp.route('/api/proposals/<int:proposal_id>/accept', methods=['POST'])
def accept_proposal(proposal_id):
    """Accept proposal"""
    try:
        proposal_service = ProposalService(current_app.config)
        proposal = proposal_service.accept_proposal(proposal_id)
        
        # TODO: Send notification via WhatsApp
        
        return jsonify({
            'message': 'Proposal accepted successfully',
            'proposal': proposal
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error accepting proposal: {str(e)}")
        return jsonify({'error': str(e)}), 500


@proposals_bp.route('/api/proposals/<int:proposal_id>/reject', methods=['POST'])
def reject_proposal(proposal_id):
    """Reject proposal"""
    try:
        data = request.get_json()
        
        proposal = Proposal.query.get_or_404(proposal_id)
        
        if proposal.status != 'pending':
            return jsonify({'error': f'Proposal is already {proposal.status}'}), 400
        
        proposal.status = 'rejected'
        proposal.rejection_reason = data.get('reason', '')
        
        # Update lead status
        proposal.lead.status = 'rejected'
        
        db.session.commit()
        
        logger.info(f"Proposal {proposal_id} rejected")
        
        return jsonify({
            'message': 'Proposal rejected',
            'proposal': proposal.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error rejecting proposal: {str(e)}")
        return jsonify({'error': str(e)}), 500


@proposals_bp.route('/uploads/<filename>', methods=['GET'])
def download_file(filename):
    """Download proposal PDF"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        
        if not os.path.exists(filepath):
            return "File not found", 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return "Error", 500
