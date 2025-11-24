import logging
import sys

def setup_logger(name: str):
    """
    Configura um logger que escreve no terminal e em arquivo.
    """
    # cria o Logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) 

    # evita duplicar logs se a função for chamada mais de uma vez
    if logger.hasHandlers():
        return logger

    # formato do log (Timestamp | Nível | Mensagem)
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | [%(name)s] -> %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # handler para o terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # handler para o arquivo 'app.log', que guarda o histórico
    file_handler = logging.FileHandler('app_logs.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger