# Densidade Cartucho - Predição de Densidade via OPC UA

Sistema de containers Docker para predição de densidade em múltiplas linhas de produção.

## Estrutura

```
DensidadeCartucho/
├── docker-compose.yml          # Build (máquina com internet)
├── docker-compose-offline.yml  # Deploy (máquina offline)
├── Dockerfile                  # Imagem unificada
├── requirements.txt            # Dependências Python
├── models/                     # Modelos de ML (.joblib)
├── L01/, L02/, L06/, L10/, L16/  # Configuração por linha
│   └── app/.env                # Tags OPC específicas
└── DEPLOY_OFFLINE.md           # Guia de deploy offline
```

## Uso Rápido

### Build (máquina com internet)
```bash
docker-compose build
```

### Deploy local
```bash
docker-compose up -d
```

### Deploy offline
Veja [DEPLOY_OFFLINE.md](DEPLOY_OFFLINE.md)

## Configuração

Cada linha tem seu arquivo `.env` em `L{XX}/app/.env`:
- `MODEL_PATH` - Caminho do modelo dentro do container
- `STATUS_TAG` - Tag OPC para status da máquina (valor 10 = rodando)
- `WRITE_TAG` - Tag OPC para escrever a predição
- `OPC_URL` - URL do servidor OPC UA
- `INTERVAL_SECONDS` - Intervalo entre predições

## Atualização de Modelos

Os modelos ficam em `models/` e são montados como volume read-only. Para atualizar:
1. Substitua o arquivo `.joblib` em `models/`
2. Reinicie o container: `docker-compose restart density-predictor-l10`
