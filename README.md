# DensidadeCartucho — fotografia operacional VM71

Fotografia **somente de código** do DensidadeCartucho efetivamente ativo na VM71, coletada pela rota Portainer somente leitura e vinculada ao image ID local imutável:

`sha256:b8500737a3f0209b1c231a67a1ec54d4c7e13521ba30088933df7225adcba703`

Componentes ativos preservados: `density_predictor_L02`, `density_predictor_L06` e `density_predictor_L16`.

## Conteúdo

- `app/density_predictor.py`: fonte recuperado de `/app` na imagem ativa;
- `requirements.txt`: especificação de dependências recuperada da imagem ativa;
- `Dockerfile`: instruções correspondentes ao histórico da imagem e ao Dockerfile do repositório preexistente;
- `docker-compose.yml`: template sanitizado apenas para as linhas ativas;
- `.env.example`: nomes de configuração com valores fictícios;
- `deployment-manifest.json`: proveniência, IDs e escopo da coleta.

A imagem não contém lockfile nem script de inicialização separado. O comando ativo recuperado é `python density_predictor.py` em `/app`.

## Exclusões deliberadas

Não fazem parte desta fotografia: modelos `*.joblib`, volume `models_volume`, dados industriais, `.env` reais, endpoints/tags OPC reais, credenciais, logs e caches. Os modelos devem ser fornecidos externamente no diretório configurado por `MODELS_DIR`.

## Validação local sem produção

```bash
cp .env.example .env
# substitua os placeholders somente em ambiente local protegido
docker compose config
python3 -m py_compile app/density_predictor.py
```

Este branch é espelho de proveniência. Não é autorização para implantar ou alterar a VM71.
