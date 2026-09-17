from flask import Blueprint

bp = Blueprint('configuracoes', __name__, url_prefix='/configuracoes')

from app.modules.configuracoes import routes