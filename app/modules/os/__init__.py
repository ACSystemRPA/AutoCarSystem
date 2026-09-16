from flask import Blueprint

bp = Blueprint('os', __name__, url_prefix='/os')

from app.modules.os import routes
