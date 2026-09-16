from flask import Blueprint

bp = Blueprint('pecas', __name__, url_prefix='/pecas')

from app.modules.pecas import routes
