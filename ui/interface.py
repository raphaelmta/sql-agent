"""
Interface do usuário com Streamlit para o SQL Agent.

Este módulo contém as funções para criar a interface do usuário
com Streamlit e exibir os resultados do processamento.
"""
import logging
import streamlit as st
import pandas as pd
from config.configuracoes import TITULO_APP, DESCRICAO_APP, EXEMPLOS_CONSULTAS
from database.conexao import rmta_configurar_banco_dados
from agent.fluxo_trabalho import rmta_processar_consulta

# Obter logger
logger = logging.getLogger('sql_agent')

def rmta_exibir_resultados(estado):
    """
    Exibe os resultados do processamento da consulta na interface.
    
    Esta função exibe a consulta SQL gerada, os resultados da consulta,
    explicações e visualizações na interface do Streamlit.
    
    Args:
        estado (EstadoAgente): Estado final após o processamento da consulta
    """
    logger.debug("Exibindo resultados na interface")
    
    if estado.get("erro"):
        st.error(estado["erro"])
        return
    
    # Exibir a consulta SQL gerada
    st.markdown("### Consulta SQL Gerada")
    st.code(estado["sql"], language="sql")
    
    # Exibir tempos de execução
    if "tempo_execucao" in estado:
        with st.expander("Tempos de Execução"):
            tempos = estado["tempo_execucao"]
            for etapa, tempo in tempos.items():
                st.text(f"{etapa}: {tempo:.4f}s")
    
    # Exibir resultados e explicações
    tab1, tab2, tab3, tab4 = st.tabs(["Resultados", "Explicação da Consulta", "Análise dos Resultados", "Debugging"])
    
    with tab1:
        if estado.get("resultados"):
            st.markdown(f"### Resultados ({len(estado['resultados'])} registros)")
            df = pd.DataFrame(estado["resultados"])
            st.dataframe(df, use_container_width=True)
            
            # Adicionar visualização se houver dados numéricos
            colunas_numericas = df.select_dtypes(include=['float64', 'int64']).columns
            if len(colunas_numericas) > 0 and len(df) > 1:
                st.markdown("### Visualização")
                tipo_grafico = st.selectbox("Tipo de gráfico:", ["Barras", "Linha", "Dispersão"])
                
                if len(colunas_numericas) >= 2:
                    coluna_x = st.selectbox("Eixo X:", df.columns)
                    coluna_y = st.selectbox("Eixo Y:", colunas_numericas)
                    
                    if tipo_grafico == "Barras":
                        st.bar_chart(df, x=coluna_x, y=coluna_y)
                    elif tipo_grafico == "Linha":
                        st.line_chart(df, x=coluna_x, y=coluna_y)
                    else:
                        st.scatter_chart(df, x=coluna_x, y=coluna_y)
                else:
                    st.bar_chart(df)
        else:
            st.info("Nenhum resultado encontrado.")
    
    with tab2:
        st.markdown("### Explicação da Consulta")
        st.markdown(estado["explicacao"])
    
    with tab3:
        if estado.get("explicacao_resultados"):
            st.markdown("### Análise dos Resultados")
            st.markdown(estado["explicacao_resultados"])
        else:
            st.info("Nenhuma análise disponível.")
    
    with tab4:
        st.markdown("### Histórico de Mensagens (Debugging)")
        
        if "mensagens" in estado and estado["mensagens"]:
            for i, msg in enumerate(estado["mensagens"]):
                with st.expander(f"Mensagem {i+1}: {msg['role'].capitalize()}"):
                    if msg['role'] == 'system':
                        st.info(msg['content'])
                    elif msg['role'] == 'user':
                        st.success(msg['content'])
                    else:  # assistant
                        st.warning(msg['content'])
            
            # Botão para exportar o histórico
            if st.button("Exportar Histórico"):
                import json
                json_history = json.dumps(estado["mensagens"], indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_history,
                    file_name="historico_mensagens.json",
                    mime="application/json"
                )
        else:
            st.info("Nenhum histórico de mensagens disponível.")
    
    # Exibir o fluxo de execução
    with st.expander("Ver fluxo de execução"):
        st.markdown("### Fluxo de execução do LangGraph")
        st.mermaid("""
        graph TD
            A[Entrada: Pergunta em Linguagem Natural] --> B[Gerar Consulta SQL]
            B --> C[Validar Consulta SQL]
            C --> D{Consulta Válida?}
            D -->|Sim| E[Executar Consulta SQL]
            D -->|Não| J[Exibir Erro]
            E --> F{Execução Bem-sucedida?}
            F -->|Sim| G[Explicar Resultados]
            F -->|Não| J
            G --> H[Exibir Resultados e Explicações]
            J --> K[Fim]
            H --> K
        """)

def rmta_iniciar_interface():
    """
    Inicia a interface do usuário com Streamlit.
    
    Esta função configura a página Streamlit, cria os elementos da interface
    e processa as consultas do usuário.
    """
    # Configuração da página Streamlit
    st.set_page_config(
        page_title=TITULO_APP,
        page_icon="🤖",
        layout="wide"
    )
    
    st.title(TITULO_APP)
    st.markdown(DESCRICAO_APP)
    
    # Configuração do banco de dados
    with st.expander("Configuração do Banco de Dados"):
        if st.button("Configurar Banco de Dados"):
            rmta_configurar_banco_dados()
    
    # Entrada do usuário
    col1, col2 = st.columns([4, 1])
    with col1:
        entrada_consulta = st.text_input("Digite sua pergunta:", placeholder="Ex: Quais clientes compraram um Notebook?")
    with col2:
        botao_enviar = st.button("Consultar", type="primary")
    
    # Exemplos clicáveis
    st.markdown("### Exemplos de perguntas")
    colunas_exemplos = st.columns(len(EXEMPLOS_CONSULTAS))
    exemplo_selecionado = None
    
    for i, (col, exemplo) in enumerate(zip(colunas_exemplos, EXEMPLOS_CONSULTAS)):
        with col:
            if st.button(exemplo, key=f"exemplo_{i}"):
                exemplo_selecionado = exemplo
    
    # Processar a consulta
    if botao_enviar and entrada_consulta:
        with st.spinner("Processando sua consulta..."):
            resultado = rmta_processar_consulta(entrada_consulta)
            rmta_exibir_resultados(resultado)
    elif exemplo_selecionado:
        st.text_input("Digite sua pergunta:", value=exemplo_selecionado, key="entrada_exemplo")
        with st.spinner("Processando sua consulta..."):
            resultado = rmta_processar_consulta(exemplo_selecionado)
            rmta_exibir_resultados(resultado)