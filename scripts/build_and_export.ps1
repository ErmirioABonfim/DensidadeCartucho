# ============================================================
# Script de Build e Export das Imagens Docker
# Executar na máquina com acesso à internet
# ============================================================

# 1. Navegar para a pasta do projeto
cd c:\Users\Ermirio\Documents\01-Develloper\densidadeSingle\DensidadeCartucho

# 2. Build de todas as imagens (cada linha gera sua própria imagem)
Write-Host "Building images..." -ForegroundColor Cyan

docker-compose build

# 3. Verificar se as imagens foram criadas
Write-Host "Images built:" -ForegroundColor Green
docker images | Select-String "density-predictor"

# 4. Salvar todas as imagens em um único arquivo .tar
# Como todas usam a mesma imagem base (density-predictor:1.0), salvamos apenas ela
Write-Host "Exporting image to tar file..." -ForegroundColor Cyan

docker save density-predictor:1.0 -o density-predictor-all-lines.tar

# 5. Comprimir para .tar.gz (opcional, reduz tamanho)
Write-Host "Compressing to .tar.gz..." -ForegroundColor Cyan
Compress-Archive -Path "density-predictor-all-lines.tar" -DestinationPath "density-predictor-all-lines.tar.gz" -Force

# 6. Mostrar arquivos gerados
Write-Host "Files created:" -ForegroundColor Green
Get-ChildItem "density-predictor-all-lines.*" | Format-Table Name, @{N='Size(MB)';E={[math]::Round($_.Length/1MB,2)}}

Write-Host "Done! Copy the following files to the offline machine:" -ForegroundColor Yellow
Write-Host "  - density-predictor-all-lines.tar (or .tar.gz)" -ForegroundColor White
Write-Host "  - The entire DensidadeCartucho folder" -ForegroundColor White
