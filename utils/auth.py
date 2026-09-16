from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def requer_perfil(*perfis_permitidos):
    """Decorator que restringe acesso a rotas conforme o perfil do utilizador.

    Uso:
        @bp.route('/admin')
        @login_required
        @requer_perfil('admin', 'gerente')
        def admin_page():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Por favor, inicie sessão para aceder a esta funcionalidade.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.papel not in perfis_permitidos:
                flash('Não tem permissão para aceder a esta funcionalidade.', 'danger')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def apenas_admin(f):
    """Atalho para @requer_perfil('admin')"""
    return requer_perfil('admin')(f)


def admin_ou_gerente(f):
    """Atalho para @requer_perfil('admin', 'gerente')"""
    return requer_perfil('admin', 'gerente')(f)
