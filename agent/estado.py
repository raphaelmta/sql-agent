"""
Definição do estado do agente SQL.

Este módulo contém a definição da classe EstadoAgente que representa
o estado do agente durante o fluxo de execução do LangGraph.
"""
from typing import Dict, List, Any, TypedDict, Optional

class EstadoAgente(TypedDict):
    """
    Representa o estado do agente durante o fluxo de execução.
    
    Attributes:
        consulta (str): Pergunta em linguagem natural do usuário
        sql (str): Consulta SQL gerada a partir da pergunta
        validacao (Dict[str, Any]): Resultado da validação da consulta SQL
        resultados (Optional[List[Dict[str, Any]]]): Resultados da consulta SQL
        explicacao (str): Explicação da consulta SQL gerada
        explicacao_resultados (Optional[str]): Explicação dos resultados da consulta
        erro (Optional[str]): Mensagem de erro, se houver
        mensagens (List[Dict[str, str]]): Histórico de mensagens trocadas com o LLM
        tempo_execucao (Dict[str, float]): Tempos de execução de cada etapa
    """
    consulta: str
    sql: str
    validacao: Dict[str, Any]
    resultados: Optional[List[Dict[str, Any]]]
    explicacao: str
    explicacao_resultados: Optional[str]
    erro: Optional[str]
    mensagens: List[Dict[str, str]]
    tempo_execucao: Dict[str, float]