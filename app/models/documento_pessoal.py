# app/models/documento_pessoal.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.extensions import db

class TipoDocumento(str, enum.Enum):
    IDENTIDADE = "identidade"
    COMPROVANTE_RESIDENCIA = "comprovante_residencia"
    OUTROS = "outros"
    
class DocumentoPessoal(db.Model):
    __tablename__ = "documentos_pessoais"
    id = Column(Integer, primary_key=True, index=True)
    credor_id = Column(Integer, ForeignKey("credores.id"), nullable=False)
    tipo = Column(Enum(TipoDocumento), nullable=False)
    arquivo_url = Column(String(255), nullable=False)
    enviado_em = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relacionamento
    credor = relationship("Credor", back_populates="documentos")
