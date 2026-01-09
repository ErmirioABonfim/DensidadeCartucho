import argparse
import asyncio
import time
from asyncua import Client, ua
import joblib
import numpy as np
from dotenv import load_dotenv
import os
from datetime import datetime
import logging
import warnings

# Suprime avisos de versão inconsistente do scikit-learn
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.base")

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Reduz o ruído do log do asyncua
logging.getLogger('asyncua').setLevel(logging.WARNING)

async def main():
    parser = argparse.ArgumentParser(description="Serviço Async OPC UA para Predição de Densidade")
    
    # Este argumento permite especificar um .env, mas se não for passado
    # (como no Docker), 'default=None' fará o load_dotenv() procurar
    # por um arquivo chamado '.env' no mesmo diretório.
    parser.add_argument('--env_file', default=None, help="Caminho para o arquivo .env específico")
    
    # Lê apenas o argumento --env_file primeiro
    args, remaining_argv = parser.parse_known_args()
    
    # Carrega o .env especificado ou o padrão ('.env')
    load_dotenv(dotenv_path=args.env_file) 
    
    # Agora, o restante dos argumentos usará os valores do .env carregado como padrão
    parser.add_argument('--model_path', default=os.getenv('MODEL_PATH'), help="Caminho para o arquivo do modelo .joblib")
    parser.add_argument('--status_tag', default=os.getenv('STATUS_TAG'), help="Tag OPC UA para o status da máquina")
    parser.add_argument('--write_tag', default=os.getenv('WRITE_TAG'), help="Tag OPC UA para escrever o resultado da predição")
    parser.add_argument('--opc_url', default=os.getenv('OPC_URL'), help="URL do servidor OPC UA")
    parser.add_argument('--interval_seconds', default=int(os.getenv('INTERVAL_SECONDS', 30)), type=int, help="Intervalo em segundos entre predições")
    
    # Faz o parse dos argumentos restantes
    args = parser.parse_args(remaining_argv, namespace=args) 

    if not args.model_path:
        raise ValueError("MODEL_PATH deve ser definido via --model_path ou no arquivo .env")
    
    model = None
    model_features = None
    model_exists = False

    # Verifica se o modelo existe antes de tentar carregar
    if not os.path.exists(args.model_path):
        logger.warning(f"MODELO INEXISTENTE: {args.model_path}. O serviço continuará rodando, escrevendo 0 no OPC.")
        model_exists = False
    else:
        # Carrega o modelo
        try:
            logger.info(f"Carregando modelo do caminho: {args.model_path}")
            loaded_data = joblib.load(args.model_path)
            if isinstance(loaded_data, dict) and 'model' in loaded_data and 'features' in loaded_data:
                model = loaded_data['model']
                model_features = loaded_data['features']
                if not model_features:
                    raise ValueError("A lista de 'features' no arquivo do modelo está vazia.")
                logger.info(f"Modelo carregado. Features esperadas (em ordem): {model_features}")
                model_exists = True
            else:
                raise ValueError("Arquivo de modelo inválido. Esperado um dicionário com 'model' e 'features'.")
            
            if not hasattr(model, 'predict'):
                raise AttributeError("O objeto 'model' carregado não possui um método 'predict'.")

        except FileNotFoundError:
            logger.warning(f"Arquivo de modelo não encontrado em {args.model_path}. O serviço continuará escrevendo 0.")
            model_exists = False
        except Exception as e:
            logger.error(f"Falha ao carregar o modelo: {e}. O serviço continuará escrevendo 0.")
            model_exists = False

    # Conecta ao servidor OPC UA
    client = Client(args.opc_url)
    client.session_timeout = 3600000 
    
    connected = False
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await client.connect()
            connected = True
            logger.info(f"Conectado ao servidor OPC UA em {args.opc_url}")
            break
        except Exception as e:
            logger.warning(f"Tentativa de conexão {attempt + 1}/{max_retries} falhou: {e}. Tentando novamente em 10 segundos...")
            await asyncio.sleep(10)
    
    if not connected:
        raise ConnectionError("Falha ao conectar ao servidor OPC UA após múltiplas tentativas.")
    
    try:
        interval_seconds = args.interval_seconds
        while True:
            start_time = time.time()
            prediction = 0.0  # Valor padrão
            
            try:
                # Se o modelo não existe, apenas escreve 0 e loga
                if not model_exists:
                    logger.info("Modelo inexistente. Escrita de 0 realizada.")
                    prediction = 0.0
                else:
                    # Lê o status da máquina
                    status_node = client.get_node(args.status_tag)
                    status = await status_node.read_value()
                    
                    # A predição só será executada se o valor do status for exatamente 10.
                    if status != 10:
                        logger.info(f"Status da máquina é {status} (esperado: 10). Máquina considerada parada. Predição definida como 0.0.")
                        prediction = 0.0
                    else:
                        # Se a máquina estiver ligada (status == 10), lê as features e faz a predição
                        logger.info("Status da máquina é 10. Iniciando ciclo de predição.")
                        features_values = []
                        all_tags_read_successfully = True

                        for tag in model_features:
                            try:
                                node = client.get_node(tag)
                                value = await node.read_value()
                                if value is None:
                                    raise ValueError(f"Valor lido da tag {tag} é Nulo (None)")
                                features_values.append(float(value))
                            except Exception as tag_error:
                                logger.error(f"Erro ao ler a tag {tag}: {tag_error}. Abortando ciclo de predição.")
                                all_tags_read_successfully = False
                                break
                        
                        if all_tags_read_successfully:
                            features_array = np.array(features_values).reshape(1, -1)
                            prediction = model.predict(features_array)[0]
                            logger.info(f"Features lidas: {features_values}")
                
                # Escreve a predição na tag OPC
                write_node = client.get_node(args.write_tag)
                await write_node.write_value(ua.DataValue(ua.Variant(prediction, ua.VariantType.Float)))
                
                logger.info(f"Predição: {prediction:.4f} escrita em {args.write_tag} às {datetime.now()}")
            
            except Exception as e:
                logger.error(f"Erro durante o ciclo de predição/escrita: {e}")
            
            elapsed_time = time.time() - start_time
            sleep_duration = max(0, interval_seconds - elapsed_time)
            
            logger.info(f"Ciclo concluído em {elapsed_time:.2f} segundos. Aguardando {sleep_duration:.2f} segundos para o próximo.")
            await asyncio.sleep(sleep_duration)
            
    finally:
        try:
            await client.disconnect()
            logger.info("Desconectado do servidor OPC UA")
        except Exception as de:
            logger.warning(f"Erro durante a desconexão: {de}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, FileNotFoundError, ConnectionError) as e:
        logger.critical(f"Execução encerrada devido a um erro crítico: {e}")
