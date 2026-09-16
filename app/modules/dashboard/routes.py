from flask import render_template
from flask_login import login_required, current_user
from app.modules.dashboard import dashboard_bp

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    return render_template(
        'dashboard/index.html',
        usuario=current_user,
        empresa=current_user.empresa
    )
