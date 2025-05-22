# app/models/precatorio.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.extensions import db

class Precatorio(db.Model):
    __tablename__ = "precatorios"
    id = Column(Integer, primary_key=True, index=True)
    credor_id = Column(Integer, ForeignKey("credores.id"), nullable=False)
    numero_precatorio = Column(String(50), nullable=False, index=True)
    valor_nominal = Column(Float, nullable=False)
    foro = Column(String(100), nullable=False)
    data_publicacao = Column(DateTime, nullable=False)
    
    # Relacionamento
    credor = relationship("Credor", back_populates="precatorios")
