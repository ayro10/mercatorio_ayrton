from flask import Blueprint, request, jsonify
import base64

bp = Blueprint('mock_api', __name__, url_prefix='/api')

@bp.route('/certidoes', methods=['GET'])
def mock_consulta_certidoes():
    cpf_cnpj = request.args.get('cpf_cnpj')
    if not cpf_cnpj:
        return jsonify({'erro': 'Parâmetro cpf_cnpj é obrigatório'}), 400

    fake_base64 = base64.b64encode(f"Certidão mock para {cpf_cnpj}".encode()).decode()

    return jsonify({
        "cpf_cnpj": cpf_cnpj,
        "certidoes": [
            {"tipo": "federal", "status": "negativa", "conteudo_base64": fake_base64},
            {"tipo": "trabalhista", "status": "positiva", "conteudo_base64": fake_base64}
        ]
    })
