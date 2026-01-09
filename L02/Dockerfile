# Imagem base Python 3.9 slim
FROM python:3.9-slim

# Diretório de trabalho
WORKDIR /app

# Copia requirements da raiz do contexto
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação da pasta da linha
COPY ./L02/app .

# Comando de inicialização
CMD ["python", "density_predictor.py"]
