"""
SQL Agent Inteligente - Aplicativo principal

Este é o ponto de entrada principal do SQL Agent Inteligente, que utiliza
LangGraph, OpenAI e Streamlit para converter perguntas em linguagem natural
em consultas SQL e executá-las em um banco de dados PostgreSQL.
"""
import os
from dotenv import load_dotenv
from utils.config_log import rmta_configurar_logging
from ui.interface import rmta_iniciar_interface

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logger = rmta_configurar_logging()

if __name__ == "__main__":
    logger.info("Iniciando SQL Agent Inteligente")
    rmta_iniciar_interface()