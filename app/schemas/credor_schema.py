from app.models.credor import Credor
from app.models.precatorio import Precatorio
from app.models.documento_pessoal import DocumentoPessoal
from app.models.certidao import Certidao
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema as masql

class PrecatorioSchema(masql):
    class Meta:
        model = Precatorio
        include_fk = True
        load_instance = True

class DocumentoPessoalSchema(masql):
    class Meta:
        model = DocumentoPessoal
        include_fk = True
        load_instance = True

class CertidaoSchema(masql):
    class Meta:
        model = Certidao
        include_fk = True
        load_instance = True

class CredorSchema(masql):
    precatorios = fields.Nested(PrecatorioSchema, many=True)
    documentos = fields.Nested(DocumentoPessoalSchema, many=True, dump_only=True)
    certidoes = fields.Nested(CertidaoSchema, many=True, dump_only=True)
    
    class Meta:
        model = Credor
        load_instance = True
