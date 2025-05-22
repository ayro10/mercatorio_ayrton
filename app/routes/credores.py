import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.credor import Credor
from app.models.precatorio import Precatorio
from app.models.documento_pessoal import DocumentoPessoal, TipoDocumento
from app.schemas.credor_schema import CredorSchema
from app.utils.validacao_arquivos import validar_arquivo, TAMANHO_MAXIMO

# Alterado o prefixo para /api/credores para evitar conflito com rotas web
bp = Blueprint('credores', __name__, url_prefix='/api/credores')

@bp.route('', methods=['POST'])
def criar_credor():
    data = request.json
    
    # Validar dados recebidos
    if not data or not all(k in data for k in ('nome', 'cpf_cnpj', 'email', 'telefone')):
        return jsonify({'erro': 'Dados incompletos para o credor'}), 400
    
    if 'precatorio' not in data or not all(k in data['precatorio'] for k in 
                                          ('numero_precatorio', 'valor_nominal', 'foro', 'data_publicacao')):
        return jsonify({'erro': 'Dados incompletos para o precatório'}), 400
    
    # Criar credor
    credor = Credor(
        nome=data['nome'],
        cpf_cnpj=data['cpf_cnpj'],
        email=data['email'],
        telefone=data['telefone']
    )
    
    try:
        db.session.add(credor)
        db.session.flush()  # Para obter o ID do credor
        
        # Criar precatório
        precatorio_data = data['precatorio']
        data_publicacao = datetime.strptime(precatorio_data['data_publicacao'], '%Y-%m-%d')
        
        precatorio = Precatorio(
            credor_id=credor.id,
            numero_precatorio=precatorio_data['numero_precatorio'],
            valor_nominal=float(precatorio_data['valor_nominal']),
            foro=precatorio_data['foro'],
            data_publicacao=data_publicacao
        )
        
        db.session.add(precatorio)
        db.session.commit()
        
        return jsonify({
            'mensagem': 'Credor e precatório cadastrados com sucesso',
            'credor_id': credor.id,
            'precatorio_id': precatorio.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': f'Erro ao cadastrar: {str(e)}'}), 500

@bp.route('/<int:credor_id>', methods=['GET'])
def obter_credor(credor_id):
    # Substituído Model.query.get() por db.session.get() para evitar warning de deprecated
    credor = db.session.get(Credor, credor_id)
    
    if not credor:
        return jsonify({'erro': 'Credor não encontrado'}), 404
    
    # Criar schema para serialização
    credor_schema = CredorSchema()
    
    # Serializar dados do credor e relacionamentos
    result = credor_schema.dump(credor)
    
    return jsonify(result), 200

@bp.route('/<int:credor_id>/documentos', methods=['POST'])
def upload_documento_pessoal(credor_id):
    # Substituído Model.query.get() por db.session.get() para evitar warning de deprecated
    credor = db.session.get(Credor, credor_id)
    if not credor:
        return jsonify({'erro': 'Credor não encontrado'}), 404
    
    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Arquivo não enviado'}), 400
    
    tipo = request.form.get('tipo')
    if not tipo:
        return jsonify({'erro': 'Tipo do documento é obrigatório'}), 400
    
    arquivo = request.files['arquivo']
    
    # Nova validação de arquivo (conteúdo e tamanho)
    valido, mensagem = validar_arquivo(arquivo)
    if not valido:
        return jsonify({'erro': mensagem}), 400
    
    filename = secure_filename(arquivo.filename)
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], f"credor_{credor_id}")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    arquivo.save(filepath)
    
    documento = DocumentoPessoal(
        credor_id=credor_id,
        tipo=TipoDocumento(tipo),
        arquivo_url=filepath,
        enviado_em=datetime.utcnow()
    )
    
    db.session.add(documento)
    db.session.commit()
    
    return jsonify({'mensagem': 'Documento enviado com sucesso', 'documento_id': documento.id}), 201
