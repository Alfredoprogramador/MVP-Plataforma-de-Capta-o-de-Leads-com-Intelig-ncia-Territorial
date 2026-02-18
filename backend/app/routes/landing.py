"""
API Routes for Landing Pages
"""
from flask import Blueprint, request, jsonify, render_template
from app.models import db, LandingPage, Lead
import logging

logger = logging.getLogger(__name__)

landing_bp = Blueprint('landing', __name__)


@landing_bp.route('/landing/<slug>', methods=['GET'])
def view_landing_page(slug):
    """View landing page"""
    try:
        page = LandingPage.query.filter_by(slug=slug, is_active=True).first_or_404()
        
        # Get UTM parameters
        utm_params = {
            'utm_source': request.args.get('utm_source'),
            'utm_medium': request.args.get('utm_medium'),
            'utm_campaign': request.args.get('utm_campaign'),
            'utm_content': request.args.get('utm_content'),
            'utm_term': request.args.get('utm_term')
        }
        
        return render_template(
            'landing_page.html',
            page=page,
            utm_params=utm_params
        )
        
    except Exception as e:
        logger.error(f"Error loading landing page: {str(e)}")
        return "Página não encontrada", 404


@landing_bp.route('/api/landing-pages', methods=['GET'])
def list_landing_pages():
    """List all landing pages"""
    try:
        neighborhood = request.args.get('neighborhood')
        
        query = LandingPage.query
        if neighborhood:
            query = query.filter_by(neighborhood=neighborhood)
        
        pages = query.order_by(LandingPage.created_at.desc()).all()
        
        return jsonify({
            'pages': [page.to_dict() for page in pages]
        })
        
    except Exception as e:
        logger.error(f"Error listing landing pages: {str(e)}")
        return jsonify({'error': str(e)}), 500


@landing_bp.route('/api/landing-pages', methods=['POST'])
def create_landing_page():
    """Create new landing page"""
    try:
        data = request.get_json()
        
        # Check if slug already exists
        existing = LandingPage.query.filter_by(slug=data['slug']).first()
        if existing:
            return jsonify({'error': 'Slug already exists'}), 400
        
        page = LandingPage(
            slug=data['slug'],
            title=data['title'],
            neighborhood=data.get('neighborhood'),
            template_name=data.get('template_name', 'default'),
            hero_title=data.get('hero_title'),
            hero_subtitle=data.get('hero_subtitle'),
            hero_image_url=data.get('hero_image_url'),
            content_sections=data.get('content_sections'),
            cta_text=data.get('cta_text', 'Solicitar Orçamento'),
            cta_button_color=data.get('cta_button_color', '#0066cc'),
            meta_description=data.get('meta_description'),
            meta_keywords=data.get('meta_keywords'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(page)
        db.session.commit()
        
        logger.info(f"Landing page created: {page.slug}")
        
        return jsonify({
            'message': 'Landing page created successfully',
            'page': page.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating landing page: {str(e)}")
        return jsonify({'error': str(e)}), 500


@landing_bp.route('/api/landing-pages/<int:page_id>', methods=['PUT'])
def update_landing_page(page_id):
    """Update landing page"""
    try:
        page = LandingPage.query.get_or_404(page_id)
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'title', 'neighborhood', 'template_name', 'hero_title',
            'hero_subtitle', 'hero_image_url', 'content_sections',
            'cta_text', 'cta_button_color', 'meta_description',
            'meta_keywords', 'is_active'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(page, field, data[field])
        
        db.session.commit()
        
        logger.info(f"Landing page updated: {page.slug}")
        
        return jsonify({
            'message': 'Landing page updated successfully',
            'page': page.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating landing page: {str(e)}")
        return jsonify({'error': str(e)}), 500


@landing_bp.route('/api/landing-pages/<int:page_id>', methods=['DELETE'])
def delete_landing_page(page_id):
    """Delete landing page"""
    try:
        page = LandingPage.query.get_or_404(page_id)
        
        db.session.delete(page)
        db.session.commit()
        
        logger.info(f"Landing page deleted: {page.slug}")
        
        return jsonify({'message': 'Landing page deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting landing page: {str(e)}")
        return jsonify({'error': str(e)}), 500
