# app/models/credor.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.extensions import db

class Credor(db.Model):
    __tablename__ = "credores"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    cpf_cnpj = Column(String(14), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=False)
    
    # Relacionamentos
    precatorios = relationship("Precatorio", back_populates="credor", cascade="all, delete-orphan")
    documentos = relationship("DocumentoPessoal", back_populates="credor", cascade="all, delete-orphan")
    certidoes = relationship("Certidao", back_populates="credor", cascade="all, delete-orphan")
