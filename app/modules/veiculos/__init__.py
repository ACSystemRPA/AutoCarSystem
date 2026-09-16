from flask import Blueprint

bp = Blueprint('veiculos', __name__, url_prefix='/veiculos')

from app.modules.veiculos import routes
