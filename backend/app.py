"""
Main Flask Application
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
import os
import logging

# Initialize extensions
migrate = Migrate()


def create_app(config_name=None):
    """Application factory"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize extensions
    from app.models import db
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Register blueprints
    from app.routes import leads_bp, whatsapp_bp, landing_bp, proposals_bp
    
    app.register_blueprint(leads_bp)
    app.register_blueprint(whatsapp_bp)
    app.register_blueprint(landing_bp)
    app.register_blueprint(proposals_bp)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    # Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'MVP Lead Capture Platform API',
            'version': '1.0.0',
            'endpoints': {
                'leads': '/api/leads',
                'whatsapp': '/api/whatsapp',
                'landing_pages': '/api/landing-pages',
                'proposals': '/api/proposals',
                'health': '/health'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
