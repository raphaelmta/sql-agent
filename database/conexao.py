"""
Módulo para gerenciar conexões com o banco de dados PostgreSQL.

Este módulo fornece funções para conectar ao banco de dados PostgreSQL
e configurar o esquema inicial com dados de exemplo.
"""
import logging
import psycopg2
import streamlit as st
from config.configuracoes import CONFIG_BD
from database.esquema import (
    SQL_CRIAR_TABELAS, 
    SQL_INSERIR_CLIENTES, 
    SQL_INSERIR_PRODUTOS, 
    SQL_INSERIR_TRANSACOES
)

# Obter logger
logger = logging.getLogger('sql_agent')

def rmta_obter_conexao_bd():
    """
    Estabelece uma conexão com o banco de dados PostgreSQL.
    
    Returns:
        Connection: Objeto de conexão com o PostgreSQL ou None em caso de erro
    """
    try:
        conexao = psycopg2.connect(
            host=CONFIG_BD["host"],
            database=CONFIG_BD["database"],
            user=CONFIG_BD["user"],
            password=CONFIG_BD["password"],
            port=CONFIG_BD["port"]
        )
        logger.info("Conexão com o banco de dados estabelecida com sucesso")
        return conexao
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def rmta_configurar_banco_dados():
    """
    Configura o banco de dados criando as tabelas e inserindo dados de exemplo.
    
    Esta função cria as tabelas necessárias (se não existirem) e insere dados
    de exemplo se as tabelas estiverem vazias.
    
    Returns:
        bool: True se a configuração foi bem-sucedida, False caso contrário
    """
    logger.info("Iniciando configuração do banco de dados")
    conexao = rmta_obter_conexao_bd()
    if not conexao:
        return False
    
    try:
        cursor = conexao.cursor()
        
        # Criar tabelas
        for sql in SQL_CRIAR_TABELAS:
            cursor.execute(sql)
            logger.debug(f"Executado SQL: {sql[:50]}...")
        
        # Verificar se já existem dados
        cursor.execute("SELECT COUNT(*) FROM clientes")
        contagem = cursor.fetchone()[0]
        
        # Inserir dados de exemplo se não existirem
        if contagem == 0:
            logger.info("Inserindo dados de exemplo no banco de dados")
            
            # Inserir clientes
            cursor.execute(SQL_INSERIR_CLIENTES)
            
            # Inserir produtos
            cursor.execute(SQL_INSERIR_PRODUTOS)
            
            # Inserir transações
            cursor.execute(SQL_INSERIR_TRANSACOES)
        
        conexao.commit()
        logger.info("Banco de dados configurado com sucesso")
        st.success("Banco de dados configurado com sucesso!")
        return True
    except Exception as e:
        conexao.rollback()
        logger.error(f"Erro ao configurar o banco de dados: {e}")
        st.error(f"Erro ao configurar o banco de dados: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()