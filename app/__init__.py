from flask import Flask
from app.extensions import db
from app.routes.credores import bp as credores_bp
from app.routes.certidoes import bp as certidoes_bp
from app.routes.mock_api import bp as mock_api_bp
from app.routes.web import bp as web_bp
import os

def create_app(test_config=None):
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configuração padrão
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key_insecure'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///mercatorio.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=os.path.join(os.getcwd(), 'uploads')
    )
    
    # Sobrescrever com configuração de teste se fornecida
    if test_config:
        app.config.update(test_config)
    
    # Garantir que a pasta de uploads exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(credores_bp)
    app.register_blueprint(certidoes_bp)
    app.register_blueprint(mock_api_bp)
    app.register_blueprint(web_bp)
    
    # Criar tabelas do banco de dados
    with app.app_context():
        db.create_all()
    
    return app
