# ============================================================
# GUIA DE DEPLOY OFFLINE - Densidade Cartucho
# ============================================================

## PASSO 1: BUILD E EXPORT (Máquina COM Internet)

### 1.1 Build da imagem
```powershell
cd c:\Users\Ermirio\Documents\01-Develloper\densidadeSingle\DensidadeCartucho
docker-compose build density-predictor-l01
```

### 1.2 Export da imagem para arquivo .tar
```powershell
docker save density-predictor:1.0 -o density-predictor-all-lines.tar
```

### 1.3 (Opcional) Comprimir para reduzir tamanho
```powershell
# PowerShell
Compress-Archive -Path "density-predictor-all-lines.tar" -DestinationPath "density-predictor-all-lines.zip" -Force

# Ou usando gzip (se disponível)
# gzip density-predictor-all-lines.tar
```

### 1.4 Arquivos para copiar para máquina offline:
- `density-predictor-all-lines.tar` (ou .zip)
- Pasta `DensidadeCartucho/` completa (ou apenas):
  - `docker-compose-offline.yml`
  - `models/` (com todos os modelos .joblib)
  - `L01/app/.env`, `L02/app/.env`, etc (arquivos .env de cada linha)

---

## PASSO 2: IMPORT E RUN (Máquina SEM Internet)

### 2.1 Copiar arquivos
Copie os arquivos listados acima para a máquina offline.

### 2.2 (Se comprimiu) Descomprimir
```powershell
Expand-Archive -Path "density-predictor-all-lines.zip" -DestinationPath "."
```

### 2.3 Carregar a imagem Docker
```powershell
cd <CAMINHO_PARA_PASTA>
docker load -i density-predictor-all-lines.tar
```

Saída esperada:
```
Loaded image: density-predictor:1.0
```

### 2.4 Verificar se a imagem foi carregada
```powershell
docker images | Select-String "density-predictor"
```

### 2.5 Subir os containers
```powershell
docker-compose -f docker-compose-offline.yml up -d
```

### 2.6 Verificar status
```powershell
docker-compose -f docker-compose-offline.yml ps
```

### 2.7 Ver logs
```powershell
# Todos os containers
docker-compose -f docker-compose-offline.yml logs -f

# Apenas L10
docker-compose -f docker-compose-offline.yml logs -f density-predictor-l10
```

---

## COMANDOS ÚTEIS

### Reiniciar um container específico
```powershell
docker-compose -f docker-compose-offline.yml restart density-predictor-l10
```

### Parar todos os containers
```powershell
docker-compose -f docker-compose-offline.yml down
```

### Atualizar modelo (sem rebuild)
1. Copie o novo modelo para `models/`
2. Reinicie o container: `docker-compose -f docker-compose-offline.yml restart density-predictor-l10`

---

## ESTRUTURA MÍNIMA PARA MÁQUINA OFFLINE

```
DensidadeCartucho/
├── docker-compose-offline.yml
├── density-predictor-all-lines.tar
├── models/
│   ├── L01_density_model.joblib
│   ├── L06_density_model.joblib
│   ├── L10_density_model.joblib
│   └── L16_density_model.joblib
├── L01/app/.env
├── L02/app/.env
├── L06/app/.env
├── L10/app/.env
└── L16/app/.env
```
