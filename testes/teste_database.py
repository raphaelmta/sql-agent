"""
Testes unitários para as funções de banco de dados.

Este módulo contém testes unitários para as funções de conexão
e manipulação do banco de dados.
"""
import unittest
from unittest.mock import patch, MagicMock
from database.conexao import rmta_obter_conexao_bd

class TesteConexaoBancoDados(unittest.TestCase):
    """Testes para as funções de conexão com o banco de dados."""
    
    @patch('psycopg2.connect')
    def test_conexao_bem_sucedida(self, mock_connect):
        """Testa se a conexão é estabelecida com sucesso."""
        # Mock da conexão bem-sucedida
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        conn = rmta_obter_conexao_bd()
        self.assertIsNotNone(conn)
        mock_connect.assert_called_once()
    
    @patch('psycopg2.connect')
    @patch('streamlit.error')
    def test_falha_conexao(self, mock_st_error, mock_connect):
        """Testa o comportamento quando a conexão falha."""
        # Mock da conexão falhando
        mock_connect.side_effect = Exception("Erro de conexão")
        
        conn = rmta_obter_conexao_bd()
        self.assertIsNone(conn)
        mock_connect.assert_called_once()
        mock_st_error.assert_called_once()