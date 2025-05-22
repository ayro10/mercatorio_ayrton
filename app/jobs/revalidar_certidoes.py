from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import joinedload
from app.extensions import db
from app.models.certidao import Certidao, OrigemCertidao, StatusCertidao, TipoCertidao
from app.models.credor import Credor
from datetime import datetime
import requests

def revalidar_certidoes():
    print("[JOB] Revalidando certidões...")

    credores = Credor.query.options(joinedload(Credor.certidoes)).all()

    for credor in credores:
        certs_api = [c for c in credor.certidoes if c.origem == OrigemCertidao.API]

        if not certs_api:
            continue

        try:
            res = requests.get("http://localhost:5000/api/certidoes", params={"cpf_cnpj": credor.cpf_cnpj})
            dados = res.json()
        except Exception as e:
            print(f"[JOB] Erro ao consultar certidões de {credor.cpf_cnpj}: {str(e)}")
            continue

        for nova in dados.get("certidoes", []):
            tipo = TipoCertidao(nova["tipo"])
            status = StatusCertidao(nova["status"])

            for cert in certs_api:
                if cert.tipo == tipo:
                    cert.status = status
                    cert.conteudo_base64 = nova["conteudo_base64"]
                    cert.recebida_em = datetime.utcnow()

    db.session.commit()
    print("[JOB] Certidões revalidadas com sucesso")

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=revalidar_certidoes, trigger="interval", hours=24)
    scheduler.start()
    app.scheduler = scheduler
