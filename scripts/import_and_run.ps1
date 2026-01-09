# ============================================================
# Script de Import e Deploy em Máquina Offline
# Executar na máquina SEM acesso à internet
# ============================================================

# 1. Navegar para a pasta onde copiou os arquivos
# cd <CAMINHO_PARA_PASTA_DENSIDADECARTUCHO>

# 2. Carregar a imagem Docker do arquivo .tar
Write-Host "Loading Docker image from tar file..." -ForegroundColor Cyan

docker load -i density-predictor-all-lines.tar

# Se usou o .tar.gz, primeiro extraia:
# Expand-Archive -Path "density-predictor-all-lines.tar.gz" -DestinationPath "."
# docker load -i density-predictor-all-lines.tar

# 3. Verificar se a imagem foi carregada
Write-Host "Verifying loaded images:" -ForegroundColor Green
docker images | Select-String "density-predictor"

# 4. Subir os containers
Write-Host "Starting containers..." -ForegroundColor Cyan
docker-compose -f docker-compose-offline.yml up -d

# 5. Verificar status dos containers
Write-Host "Container status:" -ForegroundColor Green
docker-compose -f docker-compose-offline.yml ps

# 6. Ver logs (opcional)
# docker-compose -f docker-compose-offline.yml logs -f
