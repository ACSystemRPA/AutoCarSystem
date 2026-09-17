import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-secret-key-autocar')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'autocarsystem.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scheduler API para backup automático
    SCHEDULER_API_ENABLED = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ('true', '1', 'yes')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    MAIL_MAX_EMAILS = 5
    MAIL_ASCII_ATTACHMENTS = False

    PDF_TITLE_PREFIX = os.environ.get('PDF_TITLE_PREFIX', 'AutoCarSystem')

    PERMISSOES = {
        'admin': ['admin', 'gerente', 'rececionista', 'mecanico'],
        'gerente': ['rececionista', 'mecanico'],
        'rececionista': [],
        'mecanico': []
    }
