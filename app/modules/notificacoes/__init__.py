from flask import Blueprint

bp = Blueprint('notificacoes', __name__, url_prefix='/notificacoes')

from app.modules.notificacoes import routes