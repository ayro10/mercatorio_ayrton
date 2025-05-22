from flask import Blueprint, request, jsonify, current_app
import requests
from app.extensions import db
from app.models.certidao import Certidao, OrigemCertidao, StatusCertidao, TipoCertidao
from app.models.credor import Credor
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from app.utils.validacao_arquivos import validar_arquivo

# Alterado o prefixo para /api/credores para evitar conflito com rotas web
bp = Blueprint('certidoes', __name__, url_prefix='/api/credores')

@bp.route('/<int:credor_id>/buscar-certidoes', methods=['POST'])
def buscar_certidoes_automaticamente(credor_id):
    # Substituído Model.query.get() por db.session.get() para evitar warning de deprecated
    credor = db.session.get(Credor, credor_id)
    if not credor:
        return jsonify({'erro': 'Credor não encontrado'}), 404

    try:
        response = requests.get(f"http://localhost:5000/api/certidoes", params={"cpf_cnpj": credor.cpf_cnpj})
        data = response.json()
    except Exception as e:
        return jsonify({'erro': 'Erro ao consultar certidões mockadas', 'detalhes': str(e)}), 500

    certidoes_salvas = []
    for cert in data.get("certidoes", []):
        certidao = Certidao(
            credor_id=credor.id,
            tipo=TipoCertidao(cert["tipo"]),
            status=StatusCertidao(cert["status"]),
            origem=OrigemCertidao.API,
            conteudo_base64=cert["conteudo_base64"],
            recebida_em=datetime.utcnow()
        )
        db.session.add(certidao)
        certidoes_salvas.append(certidao)

    db.session.commit()
    return jsonify({'mensagem': 'Certidões buscadas e salvas com sucesso', 'total': len(certidoes_salvas)}), 201


@bp.route('/<int:credor_id>/certidoes', methods=['POST'])
def upload_certidao_manual(credor_id):
    # Substituído Model.query.get() por db.session.get() para evitar warning de deprecated
    credor = db.session.get(Credor, credor_id)
    if not credor:
        return jsonify({'erro': 'Credor não encontrado'}), 404

    tipo = request.form.get('tipo')
    status = request.form.get('status')
    arquivo = request.files.get('arquivo')

    if not tipo or not status:
        return jsonify({'erro': 'Campos obrigatórios: tipo e status'}), 400

    certidao = Certidao(
        credor_id=credor.id,
        tipo=TipoCertidao(tipo),
        status=StatusCertidao(status),
        origem=OrigemCertidao.MANUAL,
        recebida_em=datetime.utcnow()
    )

    if arquivo:
        # Nova validação de arquivo (conteúdo e tamanho)
        valido, mensagem = validar_arquivo(arquivo)
        if not valido:
            return jsonify({'erro': mensagem}), 400

        filename = secure_filename(arquivo.filename)
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"credor_{credor_id}", "certidoes")
        os.makedirs(path, exist_ok=True)

        full_path = os.path.join(path, filename)
        arquivo.save(full_path)
        certidao.arquivo_url = full_path

    db.session.add(certidao)
    db.session.commit()

    return jsonify({'mensagem': 'Certidão manual enviada com sucesso', 'certidao_id': certidao.id}), 201
