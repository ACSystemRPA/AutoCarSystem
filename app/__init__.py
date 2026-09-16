from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager, mail
from app import models


def create_app(config_class=Config):
    app = Flask(__name__)
    if isinstance(config_class, dict):
        app.config.from_object(Config)
        app.config.update(config_class)
    elif config_class:
        app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicie sessão para aceder ao sistema.'
    login_manager.login_message_category = 'warning'

    @app.route('/health')
    def health():
        return {"status": "success", "message": "AutoCarSystem operacional!"}

    @app.template_filter('currency_pt')
    def currency_pt(value):
        if value is None:
            return '0,00 €'
        try:
            return f"{value:,.2f} €".replace(",", " ").replace(".", ",").replace(" ", ".")
        except (ValueError, TypeError):
            return '0,00 €'

    @app.template_filter('nif_fmt')
    def nif_fmt(value):
        if not value:
            return '—'
        digits = ''.join(c for c in str(value) if c.isdigit())
        return digits if len(digits) == 9 else value

    from app.modules.auth import auth_bp
    from app.modules.dashboard import dashboard_bp
    from app.modules.clientes import bp as clientes_bp
    from app.modules.veiculos import bp as veiculos_bp
    from app.modules.pecas import bp as pecas_bp
    from app.modules.servicos import bp as servicos_bp
    from app.modules.os import bp as os_bp
    from app.modules.notificacoes import bp as notificacoes_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='')
    app.register_blueprint(clientes_bp)
    app.register_blueprint(veiculos_bp)
    app.register_blueprint(pecas_bp)
    app.register_blueprint(servicos_bp)
    app.register_blueprint(os_bp)
    app.register_blueprint(notificacoes_bp)

    return app