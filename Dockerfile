# Imagem base Python 3.9 slim
FROM python:3.9-slim

# Diretório de trabalho
WORKDIR /app

# Copia requirements
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação (script unificado)
COPY app/density_predictor.py .

# Comando de inicialização
CMD ["python", "density_predictor.py"]
