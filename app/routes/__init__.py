from flask import Blueprint
from .credores import bp as credores_bp
from .documentos import bp as documentos_bp
from .certidoes import bp as certidoes_bp

def register_blueprints(app):
    app.register_blueprint(credores_bp)
    app.register_blueprint(documentos_bp)
    app.register_blueprint(certidoes_bp)
