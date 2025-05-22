import json
import pytest
from datetime import datetime
import random

def generate_unique_cpf():
    """Gera um CPF único para testes"""
    return f"{random.randint(10000000000, 99999999999)}"

def test_criar_credor_sucesso(client, session):
    """Testa a criação de um credor com precatório com sucesso."""
    # Usando CPF único para evitar conflitos
    cpf_unico = generate_unique_cpf()
    
    data = {
        "nome": "Teste da Silva",
        "cpf_cnpj": cpf_unico,
        "email": "teste@example.com",
        "telefone": "11999999999",
        "precatorio": {
            "numero_precatorio": "0001234-56.2020.8.26.0050",
            "valor_nominal": 50000.00,
            "foro": "TJSP",
            "data_publicacao": "2023-10-01"
        }
    }
    
    response = client.post('/api/credores', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert "credor_id" in response_data
    assert "precatorio_id" in response_data
    assert "mensagem" in response_data
    
    # Verificar se foi salvo no banco
    from app.models.credor import Credor
    # Usando db.session em vez de query para evitar warnings
    credor = Credor.query.filter_by(cpf_cnpj=cpf_unico).first()
    assert credor is not None
    assert credor.nome == "Teste da Silva"
    assert len(credor.precatorios) == 1
    assert credor.precatorios[0].numero_precatorio == "0001234-56.2020.8.26.0050"

def test_criar_credor_dados_incompletos(client):
    """Testa a criação de um credor com dados incompletos."""
    # Dados sem email
    data = {
        "nome": "Teste Incompleto",
        "cpf_cnpj": generate_unique_cpf(),  # CPF único
        "telefone": "11999999999",
        "precatorio": {
            "numero_precatorio": "0001234-56.2020.8.26.0050",
            "valor_nominal": 50000.00,
            "foro": "TJSP",
            "data_publicacao": "2023-10-01"
        }
    }
    
    response = client.post('/api/credores', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "Dados incompletos" in response_data["erro"]

def test_criar_credor_precatorio_incompleto(client):
    """Testa a criação de um credor com dados de precatório incompletos."""
    data = {
        "nome": "Teste Precatorio Incompleto",
        "cpf_cnpj": generate_unique_cpf(),  # CPF único
        "email": "teste@example.com",
        "telefone": "11999999999",
        "precatorio": {
            "numero_precatorio": "0001234-56.2020.8.26.0050",
            # Faltando valor_nominal
            "foro": "TJSP",
            "data_publicacao": "2023-10-01"
        }
    }
    
    response = client.post('/api/credores', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "Dados incompletos para o precatório" in response_data["erro"]

def test_obter_credor_existente(client, credor_exemplo, precatorio_exemplo):
    """Testa a obtenção de um credor existente."""
    response = client.get(f'/api/credores/{credor_exemplo.id}')
    
    assert response.status_code == 200
    response_data = json.loads(response.data)
    
    assert response_data["id"] == credor_exemplo.id
    assert response_data["nome"] == credor_exemplo.nome
    assert response_data["cpf_cnpj"] == credor_exemplo.cpf_cnpj
    assert "precatorios" in response_data
    assert len(response_data["precatorios"]) == 1
    assert response_data["precatorios"][0]["id"] == precatorio_exemplo.id

def test_obter_credor_inexistente(client):
    """Testa a obtenção de um credor que não existe."""
    response = client.get('/api/credores/9999')
    
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "não encontrado" in response_data["erro"]

def test_criar_credor_cpf_duplicado(client, session):
    """Testa a criação de um credor com CPF/CNPJ já existente."""
    # Primeiro, criar um credor para o teste
    cpf_teste = generate_unique_cpf()
    
    # Criar o primeiro credor diretamente no banco
    from app.models.credor import Credor
    credor_inicial = Credor(
        nome="Credor Inicial",
        cpf_cnpj=cpf_teste,
        email="inicial@example.com",
        telefone="11999999999"
    )
    session.add(credor_inicial)
    session.commit()
    
    # Tentar criar outro credor com o mesmo CPF
    data = {
        "nome": "Outro Nome",
        "cpf_cnpj": cpf_teste,  # Mesmo CPF do credor criado acima
        "email": "outro@example.com",
        "telefone": "11888888888",
        "precatorio": {
            "numero_precatorio": "9999999-99.2020.8.26.0050",
            "valor_nominal": 30000.00,
            "foro": "TJSP",
            "data_publicacao": "2023-11-01"
        }
    }
    
    response = client.post('/api/credores', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 500
    response_data = json.loads(response.data)
    assert "erro" in response_data
