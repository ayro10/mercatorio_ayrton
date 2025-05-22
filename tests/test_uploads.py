import json
import pytest
import io
import os
from werkzeug.datastructures import FileStorage
import random
from app.extensions import db

def generate_unique_cpf():
    """Gera um CPF único para testes"""
    return f"{random.randint(10000000000, 99999999999)}"

def test_upload_documento_sucesso(client, credor_exemplo, test_app):
    """Testa o upload de um documento pessoal com sucesso."""
    # Criar um arquivo de teste em memória com conteúdo PDF válido
    file_content = b"%PDF-1.5\nconteudo de teste do documento PDF"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="identidade.pdf",
        content_type="application/pdf",
    )
    
    data = {
        'tipo': 'identidade',
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor_exemplo.id}/documentos',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert "documento_id" in response_data
    
    # Verificar se foi salvo no banco
    from app.models.documento_pessoal import DocumentoPessoal
    # Usando db.session em vez de query.get para evitar warnings
    documento = db.session.get(DocumentoPessoal, response_data["documento_id"])
    assert documento is not None
    # Verificando o valor real retornado pelo enum
    assert documento.tipo.value == "identidade"
    assert documento.credor_id == credor_exemplo.id
    
    # Verificar se o arquivo foi salvo no sistema de arquivos
    assert os.path.exists(documento.arquivo_url)

def test_upload_documento_credor_inexistente(client):
    """Testa o upload de um documento para um credor que não existe."""
    file_content = b"%PDF-1.5\nconteudo de teste do documento PDF"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="identidade.pdf",
        content_type="application/pdf",
    )
    
    data = {
        'tipo': 'identidade',
        'arquivo': file
    }
    
    response = client.post(
        '/api/credores/9999/documentos',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "não encontrado" in response_data["erro"]

def test_upload_documento_sem_arquivo(client, session):
    """Testa o upload de um documento sem enviar o arquivo."""
    # Criar um credor único para este teste
    from app.models.credor import Credor
    cpf_unico = generate_unique_cpf()
    credor = Credor(
        nome="Teste Upload Sem Arquivo",
        cpf_cnpj=cpf_unico,
        email="upload.sem.arquivo@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    
    data = {
        'tipo': 'identidade'
        # Sem arquivo
    }
    
    response = client.post(
        f'/api/credores/{credor.id}/documentos',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "Arquivo não enviado" in response_data["erro"]

def test_upload_documento_sem_tipo(client, session):
    """Testa o upload de um documento sem especificar o tipo."""
    # Criar um credor único para este teste
    from app.models.credor import Credor
    cpf_unico = generate_unique_cpf()
    credor = Credor(
        nome="Teste Upload Sem Tipo",
        cpf_cnpj=cpf_unico,
        email="upload.sem.tipo@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    
    file_content = b"%PDF-1.5\nconteudo de teste do documento PDF"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="identidade.pdf",
        content_type="application/pdf",
    )
    
    data = {
        # Sem tipo
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor.id}/documentos',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "Tipo do documento é obrigatório" in response_data["erro"]

def test_upload_documento_extensao_invalida(client, session):
    """Testa o upload de um documento com extensão inválida."""
    # Criar um credor único para este teste
    from app.models.credor import Credor
    cpf_unico = generate_unique_cpf()
    credor = Credor(
        nome="Teste Upload Extensão Inválida",
        cpf_cnpj=cpf_unico,
        email="upload.extensao.invalida@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    
    # Conteúdo de texto simples com extensão .exe (inválida)
    file_content = b"Este e um arquivo de texto simples, nao um PDF ou imagem"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="identidade.exe",  # Extensão inválida
        content_type="application/octet-stream",
    )
    
    data = {
        'tipo': 'identidade',
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor.id}/documentos',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    # A mensagem de erro agora vem da validação de tipo MIME
    assert "Tipo de arquivo não permitido" in response_data["erro"] or "Extensão de arquivo não corresponde" in response_data["erro"]

def test_upload_documento_conteudo_invalido(client, session):
    """Testa o upload de um documento com conteúdo inválido (extensão não corresponde ao conteúdo)."""
    # Criar um credor único para este teste
    from app.models.credor import Credor
    cpf_unico = generate_unique_cpf()
    credor = Credor(
        nome="Teste Upload Conteúdo Inválido",
        cpf_cnpj=cpf_unico,
        email="upload.conteudo.invalido@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    
    # Conteúdo de texto simples com extensão .pdf (não corresponde)
    file_content = b"Este e um arquivo de texto simples, nao um PDF"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="identidade.pdf",  # Extensão válida, mas conteúdo não corresponde
        content_type="application/pdf",
    )
    
    data = {
        'tipo': 'identidade',
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor.id}/documentos',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    # A mensagem de erro agora vem da validação de tipo MIME
    assert "Tipo de arquivo não permitido" in response_data["erro"] or "Extensão de arquivo não corresponde" in response_data["erro"]

def test_upload_documento_tamanho_excedido(client, session, monkeypatch):
    """Testa o upload de um documento com tamanho excedido."""
    # Criar um credor único para este teste
    from app.models.credor import Credor
    cpf_unico = generate_unique_cpf()
    credor = Credor(
        nome="Teste Upload Tamanho Excedido",
        cpf_cnpj=cpf_unico,
        email="upload.tamanho.excedido@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    
    # Simular um arquivo PDF válido, mas com tamanho excedido
    file_content = b"%PDF-1.5\n" + b"x" * (11 * 1024 * 1024)  # 11MB (acima do limite de 10MB)
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="documento_grande.pdf",
        content_type="application/pdf",
    )
    
    # Patch para a função de verificação de tamanho para simular um arquivo grande
    from app.utils.validacao_arquivos import verificar_tamanho_arquivo
    def mock_verificar_tamanho(*args, **kwargs):
        return False, "Arquivo muito grande: 11.0MB (máximo: 10.0MB)"
    
    monkeypatch.setattr("app.utils.validacao_arquivos.verificar_tamanho_arquivo", mock_verificar_tamanho)
    
    data = {
        'tipo': 'identidade',
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor.id}/documentos',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "Arquivo muito grande" in response_data["erro"]

def test_upload_certidao_manual_sucesso(client, session, test_app):
    """Testa o upload manual de uma certidão com sucesso."""
    # Criar um credor único para este teste
    from app.models.credor import Credor
    cpf_unico = generate_unique_cpf()
    credor = Credor(
        nome="Teste Upload Certidão",
        cpf_cnpj=cpf_unico,
        email="upload.certidao@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    
    # Criar um arquivo de teste em memória com conteúdo PDF válido
    file_content = b"%PDF-1.5\nconteudo de teste da certidao PDF"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="certidao_federal.pdf",
        content_type="application/pdf",
    )
    
    data = {
        'tipo': 'federal',
        'status': 'negativa',
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor.id}/certidoes',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 201
    response_data = json.loads(response.data)
    assert "certidao_id" in response_data
    
    # Verificar se foi salvo no banco
    from app.models.certidao import Certidao
    # Usando db.session em vez de query.get para evitar warnings
    certidao = db.session.get(Certidao, response_data["certidao_id"])
    assert certidao is not None
    assert certidao.tipo.value == "federal"
    assert certidao.status.value == "negativa"
    assert certidao.origem.value == "manual"
    assert certidao.credor_id == credor.id
    
    # Verificar se o arquivo foi salvo no sistema de arquivos
    assert os.path.exists(certidao.arquivo_url)

def test_upload_certidao_sem_campos_obrigatorios(client, session):
    """Testa o upload de uma certidão sem campos obrigatórios."""
    # Criar um credor único para este teste
    from app.models.credor import Credor
    cpf_unico = generate_unique_cpf()
    credor = Credor(
        nome="Teste Certidão Sem Campos",
        cpf_cnpj=cpf_unico,
        email="certidao.sem.campos@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    
    file_content = b"%PDF-1.5\nconteudo de teste da certidao PDF"
    file = FileStorage(
        stream=io.BytesIO(file_content),
        filename="certidao_federal.pdf",
        content_type="application/pdf",
    )
    
    data = {
        # Sem tipo
        'status': 'negativa',
        'arquivo': file
    }
    
    response = client.post(
        f'/api/credores/{credor.id}/certidoes',
        data=data,
        content_type='multipart/form-data'
    )
    
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "erro" in response_data
    assert "obrigatórios" in response_data["erro"]
