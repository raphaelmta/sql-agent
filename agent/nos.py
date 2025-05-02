"""
Nós do grafo de fluxo do SQL Agent.

Este módulo contém as funções que representam os nós do grafo de fluxo
do LangGraph, responsáveis por processar a consulta do usuário.
"""
import re
import json
import time
import logging
import pandas as pd
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END

from config.configuracoes import CHAVE_API_OPENAI, MODELO_OPENAI, TEMPERATURA
from database.conexao import rmta_obter_conexao_bd
from database.esquema import ESQUEMA_BD
from agent.estado import EstadoAgente

# Obter logger
logger = logging.getLogger('sql_agent')

def rmta_gerar_sql(estado: EstadoAgente) -> EstadoAgente:
    """
    Gera uma consulta SQL a partir de uma pergunta em linguagem natural.
    
    Esta função utiliza o modelo GPT-4o para converter a pergunta do usuário
    em uma consulta SQL válida para PostgreSQL, baseada no esquema do banco de dados.
    
    Args:
        estado (EstadoAgente): O estado atual do agente contendo a consulta do usuário
        
    Returns:
        EstadoAgente: Estado atualizado com a consulta SQL gerada e sua explicação
        
    Raises:
        Exception: Se ocorrer um erro na geração da consulta SQL
    """
    inicio = time.time()
    consulta = estado["consulta"]
    logger.info(f"Gerando SQL para a consulta: '{consulta}'")
    
    # Prompt do sistema para o modelo
    prompt_sistema = f"""
    Você é um especialista em SQL para PostgreSQL. Sua tarefa é converter perguntas feitas em linguagem natural em consultas SQL válidas.

    O banco de dados possui o seguinte esquema:
    {ESQUEMA_BD}

    Relacionamentos:
    - Um cliente pode ter várias transações (1 para N)
    - Cada transação está associada a um produto (N para 1)

    Diretrizes importantes:
    1. Use JOINs apropriados para relacionar as tabelas
    2. Use aliases para melhorar a legibilidade (ex: c para clientes)
    3. Sempre use consultas parametrizadas para evitar SQL injection
    4. Otimize as consultas para melhor performance
    5. Inclua comentários explicativos no SQL quando necessário
    6. Forneça uma explicação clara do que a consulta faz
    7. Não use funções ou sintaxes específicas que não sejam compatíveis com PostgreSQL
    8. Sempre retorne resultados significativos e bem formatados

    Exemplos de consultas:
    1. "Quais clientes compraram um Notebook?" deve gerar uma consulta que junta clientes, transacoes e produtos, filtrando por produtos com nome contendo "Notebook".
    2. "Quanto cada cliente gastou no total?" deve agrupar transações por cliente e somar os valores.
    3. "Quem tem saldo suficiente para comprar um Smartphone?" deve comparar o saldo dos clientes com o preço dos smartphones.

    Responda apenas com um JSON no seguinte formato:
    {{"query": "A consulta SQL aqui", "explanation": "Explicação da consulta aqui"}}
    """
    
    try:
        modelo = ChatOpenAI(api_key=CHAVE_API_OPENAI, model=MODELO_OPENAI, temperature=TEMPERATURA)
        
        mensagens = [
            SystemMessage(content=prompt_sistema),
            HumanMessage(content=f"Gere uma consulta SQL para responder à seguinte pergunta: '{consulta}'")
        ]
        
        logger.debug("Enviando requisição para o modelo de linguagem")
        resposta = modelo.invoke(mensagens)
        
        # Extrai o JSON da resposta
        conteudo = resposta.content
        try:
            resultado_json = json.loads(conteudo)
            sql = resultado_json.get("query", "")
            explicacao = resultado_json.get("explanation", "")
        except json.JSONDecodeError:
            # Tentar extrair JSON se estiver em formato de código
            logger.warning("Falha ao decodificar JSON diretamente, tentando extrair de bloco de código")
            json_match = re.search(r'```json\s*(.*?)\s*```', conteudo, re.DOTALL)
            if json_match:
                resultado_json = json.loads(json_match.group(1))
                sql = resultado_json.get("query", "")
                explicacao = resultado_json.get("explanation", "")
            else:
                logger.error("Não foi possível extrair JSON da resposta")
                sql = ""
                explicacao = "Erro ao extrair JSON da resposta."
        
        # Atualizar o estado
        estado["sql"] = sql
        estado["explicacao"] = explicacao
        estado["mensagens"] = estado.get("mensagens", []) + [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Gere uma consulta SQL para responder à seguinte pergunta: '{consulta}'"},
            {"role": "assistant", "content": conteudo}
        ]
        
        # Registrar tempo de execução
        fim = time.time()
        tempo_execucao = fim - inicio
        estado["tempo_execucao"] = estado.get("tempo_execucao", {})
        estado["tempo_execucao"]["gerar_sql"] = tempo_execucao
        
        logger.info(f"SQL gerado com sucesso em {tempo_execucao:.2f}s: {sql[:100]}...")
        return estado
    except Exception as e:
        logger.error(f"Erro ao gerar SQL: {str(e)}")
        estado["erro"] = f"Erro ao gerar consulta SQL: {str(e)}"
        
        # Registrar tempo mesmo em caso de erro
        fim = time.time()
        tempo_execucao = fim - inicio
        estado["tempo_execucao"] = estado.get("tempo_execucao", {})
        estado["tempo_execucao"]["gerar_sql"] = tempo_execucao
        
        return estado

def rmta_validar_sql(estado: EstadoAgente) -> EstadoAgente:
    """
    Valida a consulta SQL gerada para garantir que seja segura.
    
    Esta função verifica se a consulta SQL contém comandos perigosos como
    DROP, DELETE, UPDATE, etc., e se não está vazia.
    
    Args:
        estado (EstadoAgente): O estado atual do agente contendo a consulta SQL
        
    Returns:
        EstadoAgente: Estado atualizado com o resultado da validação
    """
    inicio = time.time()
    sql = estado["sql"]
    logger.info(f"Validando consulta SQL: {sql[:100]}...")
    
    # Validação básica para evitar consultas perigosas
    padroes_proibidos = [
        r"DROP\s+",
        r"DELETE\s+",
        r"UPDATE\s+",
        r"INSERT\s+",
        r"ALTER\s+",
        r"TRUNCATE\s+",
        r"CREATE\s+",
        r"GRANT\s+",
        r"REVOKE\s+"
    ]
    
    resultado_validacao = {"is_valid": True, "message": "Consulta válida"}
    
    for padrao in padroes_proibidos:
        if re.search(padrao, sql, re.IGNORECASE):
            logger.warning(f"Consulta SQL contém padrão proibido: {padrao}")
            resultado_validacao = {
                "is_valid": False,
                "message": "Consulta não permitida. Apenas consultas SELECT são permitidas."
            }
            break
    
    # Verificar se a consulta está vazia
    if not sql.strip():
        logger.warning("Consulta SQL está vazia")
        resultado_validacao = {
            "is_valid": False,
            "message": "A consulta SQL gerada está vazia."
        }
    
    estado["validacao"] = resultado_validacao
    
    if not resultado_validacao["is_valid"]:
        estado["erro"] = resultado_validacao["message"]
        logger.error(f"Validação falhou: {resultado_validacao['message']}")
    else:
        logger.info("Consulta SQL validada com sucesso")
    
    # Registrar tempo de execução
    fim = time.time()
    tempo_execucao = fim - inicio
    estado["tempo_execucao"] = estado.get("tempo_execucao", {})
    estado["tempo_execucao"]["validar_sql"] = tempo_execucao
    
    return estado

def rmta_executar_sql(estado: EstadoAgente) -> EstadoAgente:
    """
    Executa a consulta SQL validada no banco de dados.
    
    Esta função conecta ao banco de dados PostgreSQL, executa a consulta SQL
    e armazena os resultados no estado do agente.
    
    Args:
        estado (EstadoAgente): O estado atual do agente contendo a consulta SQL validada
        
    Returns:
        EstadoAgente: Estado atualizado com os resultados da consulta
        
    Raises:
        Exception: Se ocorrer um erro na execução da consulta
    """
    inicio = time.time()
    sql = estado["sql"]
    logger.info(f"Executando consulta SQL: {sql[:100]}...")
    
    conexao = rmta_obter_conexao_bd()
    if not conexao:
        estado["erro"] = "Falha na conexão com o banco de dados."
        logger.error("Falha na conexão com o banco de dados")
        
        # Registrar tempo mesmo em caso de erro
        fim = time.time()
        tempo_execucao = fim - inicio
        estado["tempo_execucao"] = estado.get("tempo_execucao", {})
        estado["tempo_execucao"]["executar_sql"] = tempo_execucao
        
        return estado
    
    try:
        df = pd.read_sql_query(sql, conexao)
        estado["resultados"] = df.to_dict('records')
        estado["erro"] = None
        logger.info(f"Consulta executada com sucesso. {len(df)} registros retornados.")
    except Exception as e:
        estado["erro"] = f"Erro ao executar a consulta: {str(e)}"
        estado["resultados"] = None
        logger.error(f"Erro ao executar a consulta: {str(e)}")
    finally:
        conexao.close()
    
    # Registrar tempo de execução
    fim = time.time()
    tempo_execucao = fim - inicio
    estado["tempo_execucao"] = estado.get("tempo_execucao", {})
    estado["tempo_execucao"]["executar_sql"] = tempo_execucao
    
    return estado

def rmta_explicar_resultados(estado: EstadoAgente) -> EstadoAgente:
    """
    Explica os resultados da consulta SQL em linguagem natural.
    
    Esta função utiliza o modelo GPT-4o para gerar uma explicação dos resultados
    da consulta SQL em linguagem natural, facilitando a compreensão pelo usuário.
    
    Args:
        estado (EstadoAgente): O estado atual do agente contendo os resultados da consulta
        
    Returns:
        EstadoAgente: Estado atualizado com a explicação dos resultados
        
    Raises:
        Exception: Se ocorrer um erro na geração da explicação
    """
    inicio = time.time()
    
    if estado.get("erro") or not estado.get("resultados"):
        logger.warning("Não há resultados para explicar ou ocorreu um erro")
        
        # Registrar tempo mesmo em caso de erro
        fim = time.time()
        tempo_execucao = fim - inicio
        estado["tempo_execucao"] = estado.get("tempo_execucao", {})
        estado["tempo_execucao"]["explicar_resultados"] = tempo_execucao
        
        return estado
    
    resultados = estado["resultados"]
    sql = estado["sql"]
    logger.info(f"Explicando resultados da consulta. {len(resultados)} registros para analisar.")
    
    prompt_sistema = """
    Você é um especialista em análise de dados e SQL. Sua tarefa é explicar os resultados de uma consulta SQL
    de forma clara e concisa. Forneça insights sobre os dados e explique o que os resultados significam no contexto
    da pergunta original. Seja objetivo e direto.
    """
    
    try:
        modelo = ChatOpenAI(api_key=CHAVE_API_OPENAI, model=MODELO_OPENAI, temperature=TEMPERATURA)
        
        mensagens = [
            SystemMessage(content=prompt_sistema),
            HumanMessage(content=f"""
            Consulta SQL: {sql}
            
            Resultados (em formato JSON):
            {json.dumps(resultados, indent=2)}
            
            Por favor, explique estes resultados de forma clara e concisa.
            """)
        ]
        
        logger.debug("Enviando requisição para o modelo de linguagem")
        resposta = modelo.invoke(mensagens)
        
        # Adicionar a explicação dos resultados ao estado
        estado["explicacao_resultados"] = resposta.content
        estado["mensagens"] = estado.get("mensagens", []) + [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Explique os resultados da consulta SQL: {sql}"},
            {"role": "assistant", "content": resposta.content}
        ]
        
        logger.info("Explicação dos resultados gerada com sucesso")
    except Exception as e:
        estado["erro"] = f"Erro ao explicar resultados: {str(e)}"
        logger.error(f"Erro ao explicar resultados: {str(e)}")
    
    # Registrar tempo de execução
    fim = time.time()
    tempo_execucao = fim - inicio
    estado["tempo_execucao"] = estado.get("tempo_execucao", {})
    estado["tempo_execucao"]["explicar_resultados"] = tempo_execucao
    
    return estado

def rmta_decidir_proximo_passo(estado: EstadoAgente) -> str:
    """
    Decide qual deve ser o próximo passo no fluxo de execução.
    
    Esta função analisa o estado atual do agente e decide se o fluxo deve
    continuar para a explicação dos resultados ou ser encerrado.
    
    Args:
        estado (EstadoAgente): O estado atual do agente
        
    Returns:
        str: Nome do próximo nó ou END para encerrar o fluxo
    """
    logger.debug("Decidindo próximo passo no fluxo")
    
    # Se houver erro na geração SQL, encerrar o fluxo
    if "sql" not in estado or not estado["sql"]:
        logger.warning("SQL não gerado. Encerrando fluxo.")
        return END
    
    # Se a validação falhar, encerrar o fluxo
    if "validacao" in estado and not estado["validacao"]["is_valid"]:
        logger.warning("Validação falhou. Encerrando fluxo.")
        return END
    
    # Se houver erro na execução, encerrar o fluxo
    if "erro" in estado and estado["erro"]:
        logger.warning(f"Erro encontrado: {estado['erro']}. Encerrando fluxo.")
        return END
    
    # Se não houver resultados, encerrar o fluxo
    if "resultados" not in estado or not estado["resultados"]:
        logger.warning("Sem resultados. Encerrando fluxo.")
        return END
    
    # Se chegou até aqui, continuar para explicação dos resultados
    logger.info("Continuando para explicação dos resultados")
    return "explicar_resultados"