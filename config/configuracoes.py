"""
Configurações globais do aplicativo SQL Agent.

Este módulo contém constantes e configurações utilizadas em todo o aplicativo.
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
CONFIG_BD = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": os.getenv("DB_PORT", "5432")
}

# Configurações da API OpenAI
CHAVE_API_OPENAI = os.getenv("OPENAI_API_KEY")
MODELO_OPENAI = "gpt-4o"
TEMPERATURA = 0.2

# Configurações da aplicação
TITULO_APP = "🤖 SQL Agent Inteligente"
DESCRICAO_APP = "Faça perguntas em linguagem natural sobre seu banco de dados e obtenha respostas precisas."

# Exemplos de consultas para a interface
EXEMPLOS_CONSULTAS = [
    "Quais clientes compraram um Notebook?",
    "Quanto cada cliente gastou no total?",
    "Quem tem saldo suficiente para comprar um Smartphone?"
]