"""
Admin dashboard route
"""
from flask import render_template
from app.routes.landing import landing_bp


@landing_bp.route('/admin')
def admin_dashboard():
    """Admin dashboard view"""
    return render_template('admin_dashboard.html')
