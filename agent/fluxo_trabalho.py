"""
Definição do fluxo de trabalho do SQL Agent.

Este módulo contém a função para criar o grafo de fluxo de trabalho
do LangGraph que processa a consulta do usuário.
"""
import logging
import time
from langgraph.graph import StateGraph, END
from agent.estado import EstadoAgente
from agent.nos import (
    rmta_gerar_sql,
    rmta_validar_sql,
    rmta_executar_sql,
    rmta_explicar_resultados,
    rmta_decidir_proximo_passo
)

# Obter logger
logger = logging.getLogger('sql_agent')

def rmta_criar_fluxo_trabalho():
    """
    Cria o grafo de fluxo de trabalho do SQL Agent.
    
    Esta função define o grafo de fluxo de trabalho do LangGraph,
    incluindo os nós, arestas e condições de transição.
    
    Returns:
        object: Grafo de fluxo de trabalho compilado
    """
    logger.info("Criando grafo de fluxo de trabalho")
    inicio = time.time()
    
    # Definir o grafo
    fluxo_trabalho = StateGraph(EstadoAgente)
    
    # Adicionar nós
    fluxo_trabalho.add_node("gerar_sql", rmta_gerar_sql)
    fluxo_trabalho.add_node("validar_sql", rmta_validar_sql)
    fluxo_trabalho.add_node("executar_sql", rmta_executar_sql)
    fluxo_trabalho.add_node("explicar_resultados", rmta_explicar_resultados)
    
    # Definir arestas
    fluxo_trabalho.add_edge("gerar_sql", "validar_sql")
    fluxo_trabalho.add_edge("validar_sql", "executar_sql")
    fluxo_trabalho.add_conditional_edges(
        "executar_sql",
        rmta_decidir_proximo_passo,
        {
            "explicar_resultados": "explicar_resultados",
            END: END
        }
    )
    fluxo_trabalho.add_edge("explicar_resultados", END)
    
    # Definir o nó inicial
    fluxo_trabalho.set_entry_point("gerar_sql")
    
    # Compilar o grafo
    grafo_compilado = fluxo_trabalho.compile()
    
    # Registrar tempo de criação
    fim = time.time()
    logger.debug(f"Grafo de fluxo de trabalho criado em {fim - inicio:.4f}s")
    
    return grafo_compilado

def rmta_processar_consulta(texto_entrada):
    """
    Processa uma consulta em linguagem natural usando o fluxo de trabalho.
    
    Esta função cria o fluxo de trabalho, define o estado inicial e
    executa o fluxo para processar a consulta do usuário.
    
    Args:
        texto_entrada (str): Consulta em linguagem natural do usuário
        
    Returns:
        EstadoAgente: Estado final após o processamento da consulta
    """
    logger.info(f"Processando consulta: '{texto_entrada}'")
    inicio_total = time.time()
    
    # Criar o fluxo de trabalho
    fluxo_trabalho = rmta_criar_fluxo_trabalho()
    
    # Estado inicial
    estado_inicial = {
        "consulta": texto_entrada,
        "sql": "",
        "validacao": {},
        "resultados": None,
        "explicacao": "",
        "explicacao_resultados": None,
        "erro": None,
        "mensagens": [],
        "tempo_execucao": {}
    }
    
    # Executar o fluxo
    try:
        resultado = fluxo_trabalho.invoke(estado_inicial)
        
        # Registrar tempo total
        fim_total = time.time()
        tempo_total = fim_total - inicio_total
        resultado["tempo_execucao"]["total"] = tempo_total
        
        logger.info(f"Consulta processada com sucesso em {tempo_total:.2f}s")
        return resultado
    except Exception as e:
        logger.error(f"Erro ao processar o fluxo: {str(e)}")
        
        # Registrar tempo mesmo em caso de erro
        fim_total = time.time()
        tempo_total = fim_total - inicio_total
        
        return {
            "consulta": texto_entrada,
            "sql": "",
            "validacao": {},
            "resultados": None,
            "explicacao": "",
            "explicacao_resultados": None,
            "erro": f"Erro ao processar o fluxo: {str(e)}",
            "mensagens": [],
            "tempo_execucao": {"total": tempo_total}
        }