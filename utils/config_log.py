"""
Configuração do sistema de logging para o SQL Agent.

Este módulo contém a função para configurar o sistema de logging
utilizado pelo SQL Agent.
"""
import os
import logging
from datetime import datetime

def rmta_configurar_logging():
    """
    Configura o sistema de logging para o aplicativo.
    
    Esta função configura o logger com handlers para arquivo e console,
    definindo o formato das mensagens e o nível de logging.
    
    Returns:
        Logger: Objeto logger configurado
    """
    # Criar diretório de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar o logger
    logger = logging.getLogger('sql_agent')
    logger.setLevel(logging.INFO)
    
    # Limpar handlers existentes para evitar duplicação
    if logger.handlers:
        logger.handlers.clear()
    
    # Formato do log
    formato = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para arquivo
    data_atual = datetime.now().strftime('%Y-%m-%d')
    arquivo_handler = logging.FileHandler(f'logs/sql_agent_{data_atual}.log')
    arquivo_handler.setFormatter(formato)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)
    
    # Adicionar handlers ao logger
    logger.addHandler(arquivo_handler)
    logger.addHandler(console_handler)
    
    logger.info("Sistema de logging configurado")
    return logger