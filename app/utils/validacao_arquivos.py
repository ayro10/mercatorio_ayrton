"""
Utilitários para validação de arquivos no projeto Mercatório.
Inclui funções para verificar tipo MIME e tamanho de arquivos.
"""
import os
import magic

# Tipos MIME permitidos e suas extensões correspondentes
TIPOS_PERMITIDOS = {
    'application/pdf': ['.pdf'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png']
}

# Tamanho máximo de arquivo (10MB)
TAMANHO_MAXIMO = 10 * 1024 * 1024

def verificar_tipo_arquivo(arquivo):
    """
    Verifica se o tipo MIME do arquivo é permitido.
    
    Args:
        arquivo: Objeto de arquivo do Flask (FileStorage)
        
    Returns:
        tuple: (bool, str) - (é válido, mensagem)
    """
    # Obter o tipo MIME real do arquivo
    mime = magic.Magic(mime=True)
    conteudo = arquivo.read(2048)  # Ler apenas os primeiros bytes para detecção
    tipo_mime = mime.from_buffer(conteudo)
    
    # Importante: resetar o ponteiro do arquivo após a leitura
    arquivo.seek(0)
    
    # Verificar se o tipo MIME é permitido
    if tipo_mime not in TIPOS_PERMITIDOS:
        extensoes_validas = []
        for tipo, exts in TIPOS_PERMITIDOS.items():
            extensoes_validas.extend(exts)
        return False, f"Tipo de arquivo não permitido: {tipo_mime}. Extensões válidas: {', '.join(extensoes_validas)}"
    
    # Verificar se a extensão corresponde ao tipo MIME
    nome_arquivo = arquivo.filename
    extensao = os.path.splitext(nome_arquivo)[1].lower() if nome_arquivo else ''
    
    if extensao not in TIPOS_PERMITIDOS[tipo_mime]:
        return False, f"Extensão de arquivo não corresponde ao conteúdo. Extensões válidas para {tipo_mime}: {', '.join(TIPOS_PERMITIDOS[tipo_mime])}"
    
    return True, "Arquivo válido"

def verificar_tamanho_arquivo(arquivo, tamanho_maximo=TAMANHO_MAXIMO):
    """
    Verifica se o tamanho do arquivo está dentro do limite.
    
    Args:
        arquivo: Objeto de arquivo do Flask (FileStorage)
        tamanho_maximo: Tamanho máximo em bytes (padrão: 10MB)
        
    Returns:
        tuple: (bool, str) - (é válido, mensagem)
    """
    # Obter o tamanho do arquivo
    arquivo.seek(0, 2)  # Move para o final do arquivo
    tamanho = arquivo.tell()  # Obtém a posição atual (tamanho)
    arquivo.seek(0)  # Volta para o início
    
    if tamanho > tamanho_maximo:
        return False, f"Arquivo muito grande: {tamanho/1024/1024:.1f}MB (máximo: {tamanho_maximo/1024/1024:.1f}MB)"
    
    return True, "Tamanho válido"

def validar_arquivo(arquivo, tamanho_maximo=TAMANHO_MAXIMO):
    """
    Realiza todas as validações de arquivo em uma única função.
    
    Args:
        arquivo: Objeto de arquivo do Flask (FileStorage)
        tamanho_maximo: Tamanho máximo em bytes (padrão: 10MB)
        
    Returns:
        tuple: (bool, str) - (é válido, mensagem)
    """
    # Verificar se o arquivo existe
    if not arquivo or arquivo.filename == '':
        return False, "Nenhum arquivo selecionado"
    
    # Verificar tamanho
    valido, mensagem = verificar_tamanho_arquivo(arquivo, tamanho_maximo)
    if not valido:
        return False, mensagem
    
    # Verificar tipo MIME
    valido, mensagem = verificar_tipo_arquivo(arquivo)
    if not valido:
        return False, mensagem
    
    return True, "Arquivo válido"
