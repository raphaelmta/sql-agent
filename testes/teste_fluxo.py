"""
Testes unitários para o fluxo de trabalho do SQL Agent.

Este módulo contém testes unitários para as funções que definem
o fluxo de trabalho do LangGraph.
"""
import unittest
from unittest.mock import patch, MagicMock
from agent.fluxo_trabalho import rmta_criar_fluxo_trabalho, rmta_processar_consulta

class TesteFluxoTrabalho(unittest.TestCase):
    """Testes para as funções de fluxo de trabalho."""
    
    def test_criar_fluxo_trabalho(self):
        """Testa se o grafo de fluxo de trabalho é criado corretamente."""
        grafo = rmta_criar_fluxo_trabalho()
        self.assertIsNotNone(grafo)
    
    @patch('agent.fluxo_trabalho.rmta_criar_fluxo_trabalho')
    def test_processar_consulta_sucesso(self, mock_criar_fluxo):
        """Testa o processamento bem-sucedido de uma consulta."""
        # Mock do grafo
        mock_grafo = MagicMock()
        mock_criar_fluxo.return_value = mock_grafo
        
        # Mock do resultado
        mock_resultado = {
            "consulta": "Listar clientes",
            "sql": "SELECT * FROM clientes",
            "validacao": {"is_valid": True},
            "resultados": [{"id": 1, "nome": "Ana"}],
            "explicacao": "Esta consulta lista todos os clientes",
            "explicacao_resultados": "Encontrado 1 cliente",
            "erro": None,
            "mensagens": [],
            "tempo_execucao": {"gerar_sql": 0.5}
        }
        mock_grafo.invoke.return_value = mock_resultado
        
        resultado = rmta_processar_consulta("Listar clientes")
        self.assertEqual(resultado["consulta"], "Listar clientes")
        self.assertIsNone(resultado["erro"])
        self.assertIn("total", resultado["tempo_execucao"])
    
    @patch('agent.fluxo_trabalho.rmta_criar_fluxo_trabalho')
    def test_processar_consulta_erro(self, mock_criar_fluxo):
        """Testa o comportamento quando ocorre um erro no processamento."""
        # Mock do grafo
        mock_grafo = MagicMock()
        mock_criar_fluxo.return_value = mock_grafo
        
        # Mock do erro
        mock_grafo.invoke.side_effect = Exception("Erro no processamento")
        
        resultado = rmta_processar_consulta("Consulta com erro")
        self.assertEqual(resultado["consulta"], "Consulta com erro")
        self.assertIsNotNone(resultado["erro"])
        self.assertIn("total", resultado["tempo_execucao"])