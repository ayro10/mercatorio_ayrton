from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
import requests
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.credor import Credor
from app.models.precatorio import Precatorio
from app.models.documento_pessoal import DocumentoPessoal, TipoDocumento
from app.models.certidao import Certidao, TipoCertidao, StatusCertidao, OrigemCertidao

# Criar blueprint para rotas web sem prefixo para que a home seja acessível em '/'
bp = Blueprint('web', __name__, url_prefix='')

@bp.route('/')
def index():
    """Página inicial com lista de credores"""
    busca = request.args.get('busca', '')
    
    if busca:
        credores = Credor.query.filter(
            (Credor.nome.ilike(f'%{busca}%')) | 
            (Credor.cpf_cnpj.ilike(f'%{busca}%'))
        ).all()
    else:
        credores = Credor.query.all()
    
    return render_template('index.html', credores=credores, request=request)

@bp.route('/credores/novo', methods=['GET', 'POST'])
def novo_credor():
    """Formulário de cadastro de credor"""
    if request.method == 'POST':
        try:
            # Preparar dados para a API
            data = {
                "nome": request.form.get('nome'),
                "cpf_cnpj": request.form.get('cpf_cnpj'),
                "email": request.form.get('email'),
                "telefone": request.form.get('telefone'),
                "precatorio": {
                    "numero_precatorio": request.form.get('precatorio[numero_precatorio]'),
                    "valor_nominal": float(request.form.get('precatorio[valor_nominal]')),
                    "foro": request.form.get('precatorio[foro]'),
                    "data_publicacao": request.form.get('precatorio[data_publicacao]')
                }
            }
            
            # Chamar a API REST com o novo prefixo /api
            response = requests.post(
                f"http://localhost:5000/api/credores",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                response_data = response.json()
                flash(f"Credor cadastrado com sucesso! ID: {response_data['credor_id']}", "success")
                return redirect(url_for('web.detalhes_credor', credor_id=response_data['credor_id']))
            else:
                error_data = response.json()
                flash(f"Erro ao cadastrar credor: {error_data.get('erro', 'Erro desconhecido')}", "danger")
                return render_template('credor/cadastro.html')
                
        except Exception as e:
            flash(f"Erro ao processar requisição: {str(e)}", "danger")
            return render_template('credor/cadastro.html')
    
    return render_template('credor/cadastro.html')

@bp.route('/credores/<int:credor_id>', methods=['GET'])
def detalhes_credor(credor_id):
    """Página de detalhes do credor"""
    credor = db.session.get(Credor, credor_id)
    if not credor:
        flash("Credor não encontrado", "danger")
        return redirect(url_for('web.index'))
    
    return render_template('credor/detalhes.html', credor=credor)

@bp.route('/credores/<int:credor_id>/documentos/novo', methods=['GET', 'POST'])
def novo_documento(credor_id):
    """Formulário de upload de documento"""
    credor = db.session.get(Credor, credor_id)
    if not credor:
        flash("Credor não encontrado", "danger")
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        try:
            if 'arquivo' not in request.files:
                flash("Arquivo não enviado", "danger")
                return render_template('credor/upload_documento.html', credor=credor)
            
            arquivo = request.files['arquivo']
            tipo = request.form.get('tipo')
            
            if not tipo:
                flash("Tipo do documento é obrigatório", "danger")
                return render_template('credor/upload_documento.html', credor=credor)
            
            if arquivo.filename == '':
                flash("Nome do arquivo vazio", "danger")
                return render_template('credor/upload_documento.html', credor=credor)
            
            # Verificar extensão
            allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
            if not ('.' in arquivo.filename and arquivo.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                flash("Extensão de arquivo inválida", "danger")
                return render_template('credor/upload_documento.html', credor=credor)
            
            # Enviar para a API com o novo prefixo /api
            files = {'arquivo': (arquivo.filename, arquivo.stream, arquivo.content_type)}
            data = {'tipo': tipo}
            
            response = requests.post(
                f"http://localhost:5000/api/credores/{credor_id}/documentos",
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                response_data = response.json()
                flash("Documento enviado com sucesso!", "success")
                return redirect(url_for('web.detalhes_credor', credor_id=credor_id))
            else:
                error_data = response.json()
                flash(f"Erro ao enviar documento: {error_data.get('erro', 'Erro desconhecido')}", "danger")
                return render_template('credor/upload_documento.html', credor=credor)
                
        except Exception as e:
            flash(f"Erro ao processar requisição: {str(e)}", "danger")
            return render_template('credor/upload_documento.html', credor=credor)
    
    return render_template('credor/upload_documento.html', credor=credor)

@bp.route('/credores/<int:credor_id>/certidoes/novo', methods=['GET', 'POST'])
def nova_certidao(credor_id):
    """Formulário de upload de certidão"""
    credor = db.session.get(Credor, credor_id)
    if not credor:
        flash("Credor não encontrado", "danger")
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        try:
            tipo = request.form.get('tipo')
            status = request.form.get('status')
            
            if not tipo or not status:
                flash("Campos obrigatórios: tipo e status", "danger")
                return render_template('credor/upload_certidao.html', credor=credor)
            
            # Preparar dados e arquivo
            data = {'tipo': tipo, 'status': status}
            files = {}
            
            if 'arquivo' in request.files and request.files['arquivo'].filename != '':
                arquivo = request.files['arquivo']
                
                # Verificar extensão
                allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg'}
                if not ('.' in arquivo.filename and arquivo.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
                    flash("Extensão de arquivo inválida", "danger")
                    return render_template('credor/upload_certidao.html', credor=credor)
                
                files = {'arquivo': (arquivo.filename, arquivo.stream, arquivo.content_type)}
            
            # Enviar para a API com o novo prefixo /api
            response = requests.post(
                f"http://localhost:5000/api/credores/{credor_id}/certidoes",
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                response_data = response.json()
                flash("Certidão enviada com sucesso!", "success")
                return redirect(url_for('web.detalhes_credor', credor_id=credor_id))
            else:
                error_data = response.json()
                flash(f"Erro ao enviar certidão: {error_data.get('erro', 'Erro desconhecido')}", "danger")
                return render_template('credor/upload_certidao.html', credor=credor)
                
        except Exception as e:
            flash(f"Erro ao processar requisição: {str(e)}", "danger")
            return render_template('credor/upload_certidao.html', credor=credor)
    
    return render_template('credor/upload_certidao.html', credor=credor)

@bp.route('/credores/<int:credor_id>/buscar-certidoes', methods=['POST'])
def buscar_certidoes(credor_id):
    """Buscar certidões automaticamente"""
    credor = db.session.get(Credor, credor_id)
    if not credor:
        flash("Credor não encontrado", "danger")
        return redirect(url_for('web.index'))
    
    try:
        # Chamar a API REST com o novo prefixo /api
        response = requests.post(f"http://localhost:5000/api/credores/{credor_id}/buscar-certidoes")
        
        if response.status_code == 201:
            response_data = response.json()
            flash(f"Certidões buscadas com sucesso! Total: {response_data.get('total', 0)}", "success")
        else:
            error_data = response.json()
            flash(f"Erro ao buscar certidões: {error_data.get('erro', 'Erro desconhecido')}", "danger")
    except Exception as e:
        flash(f"Erro ao processar requisição: {str(e)}", "danger")
    
    return redirect(url_for('web.detalhes_credor', credor_id=credor_id))

# Rota para visualizar imagens
@bp.route('/visualizar-arquivo/<path:arquivo_url>')
def visualizar_arquivo(arquivo_url):
    """Visualizar arquivo (imagem ou PDF)"""
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo_url):
        flash("Arquivo não encontrado", "danger")
        return redirect(url_for('web.index'))
    
    # Verificar extensão
    ext = arquivo_url.rsplit('.', 1)[1].lower() if '.' in arquivo_url else ''
    
    # Se for imagem, renderizar página de visualização
    if ext in ['jpg', 'jpeg', 'png']:
        return render_template('visualizar_imagem.html', arquivo_url=arquivo_url)
    
    # Se for PDF, redirecionar para o arquivo
    return redirect(url_for('static', filename=arquivo_url))
