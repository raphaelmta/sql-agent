"""
Testes unitários para os nós do grafo do SQL Agent.

Este módulo contém testes unitários para as funções que representam
os nós do grafo de fluxo do LangGraph.
"""
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from agent.estado import EstadoAgente
from agent.nos import rmta_validar_sql, rmta_executar_sql, rmta_decidir_proximo_passo

class TesteValidacaoSQL(unittest.TestCase):
    """Testes para a função de validação SQL."""
    
    def test_consulta_valida(self):
        """Testa se uma consulta SELECT válida é aprovada."""
        estado = EstadoAgente(
            consulta="Quais clientes compraram notebooks?",
            sql="SELECT c.nome FROM clientes c JOIN transacoes t ON c.id = t.cliente_id JOIN produtos p ON p.id = t.produto_id WHERE p.nome LIKE '%Notebook%'",
            validacao={},
            resultados=None,
            explicacao="",
            explicacao_resultados=None,
            erro=None,
            mensagens=[],
            tempo_execucao={}
        )
        
        resultado = rmta_validar_sql(estado)
        self.assertTrue(resultado["validacao"]["is_valid"])
        self.assertIsNone(resultado.get("erro"))
    
    def test_consulta_perigosa(self):
        """Testa se uma consulta perigosa é rejeitada."""
        estado = EstadoAgente(
            consulta="Apagar todos os clientes",
            sql="DROP TABLE clientes",
            validacao={},
            resultados=None,
            explicacao="",
            explicacao_resultados=None,
            erro=None,
            mensagens=[],
            tempo_execucao={}
        )
        
        resultado = rmta_validar_sql(estado)
        self.assertFalse(resultado["validacao"]["is_valid"])
        self.assertIsNotNone(resultado.get("erro"))
    
    def test_consulta_vazia(self):
        """Testa se uma consulta vazia é rejeitada."""
        estado = EstadoAgente(
            consulta="Não sei o que perguntar",
            sql="   ",
            validacao={},
            resultados=None,
            explicacao="",
            explicacao_resultados=None,
            erro=None,
            mensagens=[],
            tempo_execucao={}
        )
        
        resultado = rmta_validar_sql(estado)
        self.assertFalse(resultado["validacao"]["is_valid"])
        self.assertIsNotNone(resultado.get("erro"))

class TesteExecutarSQL(unittest.TestCase):
    """Testes para a função de execução SQL."""
    
    @patch('agent.nos.rmta_obter_conexao_bd')
    def test_falha_conexao(self, mock_conexao):
        """Testa o comportamento quando a conexão com o banco falha."""
        mock_conexao.return_value = None
        
        estado = EstadoAgente(
            consulta="Listar todos os clientes",
            sql="SELECT * FROM clientes",
            validacao={"is_valid": True, "message": "Consulta válida"},
            resultados=None,
            explicacao="",
            explicacao_resultados=None,
            erro=None,
            mensagens=[],
            tempo_execucao={}
        )
        
        resultado = rmta_executar_sql(estado)
        self.assertIsNotNone(resultado.get("erro"))
        self.assertIn("Falha na conexão", resultado["erro"])
    
    @patch('agent.nos.rmta_obter_conexao_bd')
    @patch('pandas.read_sql_query')
    def test_execucao_bem_sucedida(self, mock_read_sql, mock_conexao):
        """Testa a execução bem-sucedida de uma consulta."""
        # Mock da conexão
        mock_conn = MagicMock()
        mock_conexao.return_value = mock_conn
        
        # Mock do resultado da consulta
        df = pd.DataFrame({
            'id': [1, 2],
            'nome': ['Ana Silva', 'Bruno Costa'],
            'email': ['ana.silva@email.com', 'bruno.costa@email.com'],
            'saldo': [5000.00, 3500.00]
        })
        mock_read_sql.return_value = df
        
        estado = EstadoAgente(
            consulta="Listar todos os clientes",
            sql="SELECT * FROM clientes",
            validacao={"is_valid": True, "message": "Consulta válida"},
            resultados=None,
            explicacao="",
            explicacao_resultados=None,
            erro=None,
            mensagens=[],
            tempo_execucao={}
        )
        
        resultado = rmta_executar_sql(estado)
        self.assertIsNone(resultado.get("erro"))
        self.assertEqual(len(resultado["resultados"]), 2)
        self.assertEqual(resultado["resultados"][0]["nome"], "Ana Silva")
        
        # Verificar se a conexão foi fechada
        mock_conn.close.assert_called_once()

class TesteDecidirProximoPasso(unittest.TestCase):
    """Testes para a função de decisão do próximo passo."""
    
    def test_continuar_para_explicacao(self):
        """Testa se o fluxo continua para explicação quando tudo está correto."""
        from langgraph.graph import END
        
        estado = EstadoAgente(
            consulta="Listar todos os clientes",
            sql="SELECT * FROM clientes",
            validacao={"is_valid": True, "message": "Consulta válida"},
            resultados=[{"id": 1, "nome": "Ana Silva"}],
            explicacao="Esta consulta lista todos os clientes",
            explicacao_resultados=None,
            erro=None,
            mensagens=[],
            tempo_execucao={}
        )
        
        proximo = rmta_decidir_proximo_passo(estado)
        self.assertEqual(proximo, "explicar_resultados")
    
    def test_encerrar_com_erro(self):
        """Testa se o fluxo é encerrado quando há um erro."""
        from langgraph.graph import END
        
        estado = EstadoAgente(
            consulta="Listar todos os clientes",
            sql="SELECT * FROM clientes",
            validacao={"is_valid": True, "message": "Consulta válida"},
            resultados=None,
            explicacao="Esta consulta lista todos os clientes",
            explicacao_resultados=None,
            erro="Erro ao executar a consulta",
            mensagens=[],
            tempo_execucao={}
        )
        
        proximo = rmta_decidir_proximo_passo(estado)
        self.assertEqual(proximo, END)