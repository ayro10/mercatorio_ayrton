# app/models/certidao.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.extensions import db

class TipoCertidao(str, enum.Enum):
    FEDERAL = "federal"
    ESTADUAL = "estadual"
    MUNICIPAL = "municipal"
    TRABALHISTA = "trabalhista"

class OrigemCertidao(str, enum.Enum):
    MANUAL = "manual"
    API = "api"

class StatusCertidao(str, enum.Enum):
    NEGATIVA = "negativa"
    POSITIVA = "positiva"
    INVALIDA = "invalida"
    PENDENTE = "pendente"

class Certidao(db.Model):
    __tablename__ = "certidoes"
    id = Column(Integer, primary_key=True, index=True)
    credor_id = Column(Integer, ForeignKey("credores.id"), nullable=False)
    tipo = Column(Enum(TipoCertidao), nullable=False)
    origem = Column(Enum(OrigemCertidao), nullable=False)
    arquivo_url = Column(String(255), nullable=True)
    conteudo_base64 = Column(Text, nullable=True)
    status = Column(Enum(StatusCertidao), nullable=False)
    recebida_em = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relacionamento
    credor = relationship("Credor", back_populates="certidoes")
