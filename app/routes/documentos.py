from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import Credor, DocumentoPessoal
from datetime import datetime
import os

bp = Blueprint('documentos', __name__, url_prefix='/credores')

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/<int:credor_id>/documentos', methods=['POST'])
def upload_documento_pessoal(credor_id):
    credor = Credor.query.get(credor_id)
    if not credor:
        return jsonify({'erro': 'Credor não encontrado'}), 404

    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Arquivo não enviado'}), 400

    tipo = request.form.get('tipo')
    if not tipo:
        return jsonify({'erro': 'Tipo do documento é obrigatório'}), 400

    arquivo = request.files['arquivo']
    if arquivo.filename == '':
        return jsonify({'erro': 'Nome do arquivo vazio'}), 400

    if not allowed_file(arquivo.filename):
        return jsonify({'erro': 'Extensão de arquivo inválida'}), 400

    filename = secure_filename(arquivo.filename)
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f"credor_{credor_id}")
    os.makedirs(upload_dir, exist_ok=True)

    filepath = os.path.join(upload_dir, filename)
    arquivo.save(filepath)

    documento = DocumentoPessoal(
        credor_id=credor_id,
        tipo=tipo,
        arquivo_url=filepath,
        enviado_em=datetime.utcnow()
    )
    db.session.add(documento)
    db.session.commit()

    return jsonify({'mensagem': 'Documento enviado com sucesso', 'documento_id': documento.id}), 201
