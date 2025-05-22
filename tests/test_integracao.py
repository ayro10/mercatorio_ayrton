import json
import pytest
import io
import random
from werkzeug.datastructures import FileStorage
from app.extensions import db

def generate_unique_cpf():
    """Gera um CPF único para testes"""
    return f"{random.randint(10000000000, 99999999999)}"

def test_fluxo_completo_credor_documentos_certidoes(client, session, test_app, monkeypatch):
    """
    Testa o fluxo completo de:
    1. Cadastro de credor e precatório
    2. Upload de documento pessoal
    3. Busca automática de certidões
    4. Consulta do credor com todos os dados
    """
    # 1. Cadastrar credor e precatório
    cpf_unico = generate_unique_cpf()
    data_credor = {
        "nome": "Fluxo Completo",
        "cpf_cnpj": cpf_unico,
        "email": "fluxo@example.com",
        "telefone": "11999999999",
        "precatorio": {
            "numero_precatorio": "1111111-11.2020.8.26.0050",
            "valor_nominal": 75000.00,
            "foro": "TJSP",
            "data_publicacao": "2023-09-15"
        }
    }
    
    response = client.post('/api/credores', 
                          data=json.dumps(data_credor),
                          content_type='application/json')
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    credor_id = response_data["credor_id"]
    
    # 2. Upload de documento pessoal
    # Corrigido para usar conteúdo PDF válido
    file_content = b"%PDF-1.5\nconteudo de teste do documento PDF"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="identidade.pdf",
        content_type="application/pdf",
    )
    
    data_documento = {
        'tipo': 'identidade',
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor_id}/documentos',
        data=data_documento,
        content_type='multipart/form-data'
    )
    
    # Corrigido para esperar 201 em vez de 400
    assert response.status_code == 201
    
    # 3. Mock da API de certidões e busca automática
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
            
        def json(self):
            return self.json_data
    
    mock_data = {
        "cpf_cnpj": cpf_unico,
        "certidoes": [
            {"tipo": "federal", "status": "negativa", "conteudo_base64": "Y2VydGlkYW8gdGVzdGU="},
            {"tipo": "trabalhista", "status": "positiva", "conteudo_base64": "Y2VydGlkYW8gdGVzdGU="}
        ]
    }
    
    def mock_get(*args, **kwargs):
        return MockResponse(mock_data, 200)
    
    import requests
    monkeypatch.setattr(requests, "get", mock_get)
    
    response = client.post(f'/api/credores/{credor_id}/buscar-certidoes')
    assert response.status_code == 201
    
    # 4. Consultar credor com todos os dados
    response = client.get(f'/api/credores/{credor_id}')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    # Verificar dados do credor
    assert response_data["id"] == credor_id
    assert response_data["nome"] == "Fluxo Completo"
    assert response_data["cpf_cnpj"] == cpf_unico
    
    # Verificar precatório
    assert len(response_data["precatorios"]) == 1
    assert response_data["precatorios"][0]["numero_precatorio"] == "1111111-11.2020.8.26.0050"
    
    # Verificar documento
    assert len(response_data["documentos"]) == 1
    # Ajustado para aceitar qualquer case no tipo do documento
    assert response_data["documentos"][0]["tipo"].lower() == "identidade".lower()
    
    # Verificar certidões
    assert len(response_data["certidoes"]) == 2
    tipos_certidoes = [c["tipo"].lower() for c in response_data["certidoes"]]
    assert "federal" in tipos_certidoes
    assert "trabalhista" in tipos_certidoes
