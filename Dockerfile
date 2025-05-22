# Dockerfile para o projeto Mercatório
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código do projeto
COPY . .

# Criar diretório para uploads
RUN mkdir -p uploads && chmod 777 uploads
RUN mkdir -p instance && chmod 777 instance

# Variáveis de ambiente
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV UPLOAD_FOLDER=/app/uploads

# Expor porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
