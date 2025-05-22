import pytest
import os
import tempfile
import shutil
from app import create_app
from app.extensions import db
from app.models.credor import Credor
from app.models.precatorio import Precatorio
from app.models.documento_pessoal import DocumentoPessoal, TipoDocumento
from app.models.certidao import Certidao, TipoCertidao, OrigemCertidao, StatusCertidao
from datetime import datetime

@pytest.fixture(scope="module")
def test_app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "UPLOAD_FOLDER": tempfile.mkdtemp(),
        "WTF_CSRF_ENABLED": False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    # Limpar diretório de uploads após os testes
    shutil.rmtree(app.config["UPLOAD_FOLDER"], ignore_errors=True)

@pytest.fixture()
def client(test_app):
    return test_app.test_client()

@pytest.fixture()
def session(test_app):
    with test_app.app_context():
        yield db.session

@pytest.fixture()
def credor_exemplo(session):
    credor = Credor(
        nome="Maria Silva",
        cpf_cnpj="12345678900",
        email="maria@example.com",
        telefone="11999999999"
    )
    session.add(credor)
    session.commit()
    return credor

@pytest.fixture()
def precatorio_exemplo(session, credor_exemplo):
    precatorio = Precatorio(
        credor_id=credor_exemplo.id,
        numero_precatorio="0001234-56.2020.8.26.0050",
        valor_nominal=50000.00,
        foro="TJSP",
        data_publicacao=datetime(2023, 10, 1)
    )
    session.add(precatorio)
    session.commit()
    return precatorio

@pytest.fixture()
def documento_exemplo(session, credor_exemplo, test_app):
    # Criar diretório para o arquivo
    upload_dir = os.path.join(test_app.config['UPLOAD_FOLDER'], f"credor_{credor_exemplo.id}")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Criar um arquivo de teste
    filepath = os.path.join(upload_dir, "documento_teste.pdf")
    with open(filepath, 'w') as f:
        f.write("Conteúdo de teste")
    
    documento = DocumentoPessoal(
        credor_id=credor_exemplo.id,
        tipo=TipoDocumento.IDENTIDADE,
        arquivo_url=filepath,
        enviado_em=datetime.utcnow()
    )
    session.add(documento)
    session.commit()
    return documento

@pytest.fixture()
def certidao_exemplo(session, credor_exemplo, test_app):
    # Criar diretório para o arquivo
    upload_dir = os.path.join(test_app.config['UPLOAD_FOLDER'], f"credor_{credor_exemplo.id}", "certidoes")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Criar um arquivo de teste
    filepath = os.path.join(upload_dir, "certidao_teste.pdf")
    with open(filepath, 'w') as f:
        f.write("Conteúdo de teste")
    
    certidao = Certidao(
        credor_id=credor_exemplo.id,
        tipo=TipoCertidao.FEDERAL,
        origem=OrigemCertidao.MANUAL,
        status=StatusCertidao.NEGATIVA,
        arquivo_url=filepath,
        recebida_em=datetime.utcnow()
    )
    session.add(certidao)
    session.commit()
    return certidao
