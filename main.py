# ================================
# IMPORTS
# ================================
import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px
import os

# ================================
# CONFIG DO DASHBOARD
# ================================
st.set_page_config(
    page_title="Dashboard de Queimadas no Brasil",
    layout="wide"
)

st.title("Dashboard de Análise de Queimadas no Brasil")
st.markdown("Desenvolvido para o projeto de Estatística e Probabilidade.")

# ================================
# CARREGAR SNIS AUTOMATICAMENTE
# ================================
st.sidebar.subheader("Dataset SNIS carregado automaticamente")

path_snis = "data/snis_filtrado.csv"   # coloque aqui o arquivo exportado via SQL

if os.path.exists(path_snis):
    df_snis = pd.read_csv(path_snis)
    st.sidebar.success("SNIS carregado (2016–2022).")
else:
    st.sidebar.error("Arquivo 'snis_filtrado.csv' não encontrado na pasta /data.")
    st.stop()

# ================================
# UPLOAD DO ARQUIVO DE QUEIMADAS
# ================================
st.sidebar.header("Upload do Dataset de Queimadas")
uploaded_file = st.sidebar.file_uploader("Envie o arquivo CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Filtro compatível: somente anos do dataset
    anos_queimadas = sorted(df["ano"].unique())

    # Filtra queimada x SNIS (anos exatos)
    anos_com_snis = sorted(df_snis["ano"].unique())  # 2016–2022

    # ================================
    # MERGE DOS DOIS DATASETS
    # ================================
    df_merge = df.merge(
        df_snis,
        on=["ano", "sigla_uf", "id_municipio"],
        how="left"
    )

    st.success("Base de queimadas carregada e integrada com SNIS (2016–2022).")

    # ================================
    # FILTROS DO DASHBOARD
    # ================================
    st.sidebar.header("Filtros")

    anos = st.sidebar.multiselect(
        "Selecione os anos",
        anos_queimadas,
        default=anos_queimadas
    )

    estados = st.sidebar.multiselect(
        "Selecione os estados",
        sorted(df["sigla_uf"].unique()),
        default=sorted(df["sigla_uf"].unique())
    )

    meses = st.sidebar.multiselect(
        "Selecione os meses",
        sorted(df["mes"].unique()),
        default=sorted(df["mes"].unique())
    )

    df_filtrado = df_merge[
        (df_merge["ano"].isin(anos)) &
        (df_merge["sigla_uf"].isin(estados)) &
        (df_merge["mes"].isin(meses))
    ]

    if df_filtrado.empty:
        st.warning("Nenhum dado após aplicar os filtros.")
        st.stop()

    # Mostra tabela após merge
    st.subheader("📌 Dados filtrados (incluindo SNIS quando disponível)")
    st.dataframe(df_filtrado.head(20))

    # ============================================
    # GRÁFICOS CRUZADOS: SNIS × QUEIMADAS (2016–2022)
    # ============================================
    anos_validos = [a for a in anos if a in anos_com_snis]

    if anos_validos:
        st.header("📊 Análises Cruzadas (Queimadas × Saneamento — 2016 a 2022)")

        df_cross = df_filtrado[df_filtrado["ano"].isin(anos_validos)]

        # ================================================
        # 1 — Relação: Saneamento × Total de Queimadas por UF
        # ================================================
        st.subheader("1 — Saneamento × Total de Queimadas por Estado (UF)")

        df_uf = df_cross.groupby("sigla_uf").agg({
            "indice_atendimento_urbano_agua": "mean",
            "indice_coleta_esgoto": "mean",
            "indice_tratamento_esgoto": "mean",
            "indice_perda_distribuicao_agua": "mean",
            "extensao_rede_agua": "mean",
            "id_municipio": "count"
        }).reset_index().rename(columns={"id_municipio": "queimadas"})

        fig1 = px.scatter(
            df_uf,
            x="indice_atendimento_urbano_agua",
            y="queimadas",
            size="queimadas",
            color="sigla_uf",
            trendline="ols",
            title="Atendimento Urbano de Água × Total de Queimadas (UF)"
        )
        st.plotly_chart(fig1, use_container_width=True)

        # ================================================
        # 2 — Coleta e Tratamento de Esgoto × Queimadas
        # ================================================
        st.subheader("2 — Coleta e Tratamento de Esgoto × Queimadas")

        fig2 = px.scatter(
            df_uf,
            x="indice_coleta_esgoto",
            y="queimadas",
            color="sigla_uf",
            trendline="ols",
            title="Coleta de Esgoto × Queimadas por Estado"
        )
        st.plotly_chart(fig2, use_container_width=True)

        fig3 = px.scatter(
            df_uf,
            x="indice_tratamento_esgoto",
            y="queimadas",
            color="sigla_uf",
            trendline="ols",
            title="Tratamento de Esgoto × Queimadas por Estado"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # ================================================
        # 3 — Perdas de Água × Queimadas
        # ================================================
        st.subheader("3 — Perdas na Distribuição de Água × Queimadas")

        fig4 = px.scatter(
            df_uf,
            x="indice_perda_distribuicao_agua",
            y="queimadas",
            color="sigla_uf",
            trendline="ols",
            title="Perdas na Distribuição de Água × Queimadas por Estado"
        )
        st.plotly_chart(fig4, use_container_width=True)

        # ================================================
        # 4 — Extensão da Rede de Água × Queimadas
        # ================================================
        st.subheader("4 — Extensão da Rede de Água × Queimadas")

        fig5 = px.scatter(
            df_uf,
            x="extensao_rede_agua",
            y="queimadas",
            color="sigla_uf",
            trendline="ols",
            title="Extensão de Rede de Água × Queimadas por Estado"
        )
        st.plotly_chart(fig5, use_container_width=True)

        # ================================================
        # 5 — Heatmap de Queimadas ponderado por Saneamento
        # ================================================
        st.subheader("5 — Heatmap ponderado pela Infraestrutura de Água (2016–2022)")

        if "latitude" in df_cross.columns and "longitude" in df_cross.columns:
            mapa_snis = folium.Map(location=[-15.78, -47.88], zoom_start=4)

            heat_data_snis = df_cross[["latitude", "longitude", "indice_atendimento_urbano_agua"]].dropna().values.tolist()

            # Peso = atendimento de água (normalizado)
            HeatMap(
                heat_data_snis,
                radius=10,
                gradient={0.2: "blue", 0.5: "green", 0.8: "orange", 1.0: "red"}
            ).add_to(mapa_snis)

            st_folium(mapa_snis, width=1200, height=600)
        else:
            st.warning("Colunas 'latitude' e 'longitude' não encontradas para criar o heatmap.")

    else:
        st.info("Não há anos selecionados com dados do SNIS (disponível apenas de 2016 a 2022).")

    # ================================
    # 1 — PADRÕES TEMPORAIS
    # ================================
    st.header("1. Padrões Temporais")

    df_serie = df_filtrado.groupby(["ano", "mes"]).size().reset_index(name="queimadas")
    df_serie["ano_mes"] = df_serie["ano"].astype(str) + "-" + df_serie["mes"].astype(str)

    fig_serie = px.line(
        df_serie,
        x="ano_mes",
        y="queimadas",
        markers=True,
        title="Evolução temporal das queimadas (Ano-Mês)"
    )
    st.plotly_chart(fig_serie, use_container_width=True)

    # ================================
    # 2 — SAZONALIDADE
    # ================================
    st.header("2. Sazonalidade")

    sazonalidade_media = df_filtrado.groupby("mes").size().reset_index(name="queimadas")

    fig_sazon = px.bar(
        sazonalidade_media,
        x="mes",
        y="queimadas",
        title="Sazonalidade média — queimadas por mês"
    )
    st.plotly_chart(fig_sazon, use_container_width=True)

    heat = df_filtrado.groupby(["ano", "mes"]).size().reset_index(name="queimadas")

    fig_heat = px.density_heatmap(
        heat,
        x="mes",
        y="ano",
        z="queimadas",
        color_continuous_scale="OrRd",
        title="Mapa de calor — Sazonalidade (Mês x Ano)"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ================================
    # 3 — Relação entre risco de fogo × precipitação
    # ================================
    st.header("3. Gráficos após 2023")

    df_2023 = df[df["ano"] >= 2023]
    if not df_2023.empty:
        fig_2023_1 = px.scatter(
            df_2023,
            x="precipitacao",
            y="risco_fogo",
            color="sigla_uf",
            trendline="ols",
            title="Relação entre precipitação e risco de fogo (2023+)"
        )
        st.plotly_chart(fig_2023_1, use_container_width=True)
        fig_2023_2 = px.box(
            df_2023,
            x="sigla_uf",
            y="dias_sem_chuva",
            title="Distribuição de dias sem chuva por estado (2023+)"
        )
        st.plotly_chart(fig_2023_2, use_container_width=True)

    # ================================
    # 4 — AGREGAÇÃO GEOGRÁFICA
    # ================================
    st.header("4. Agregação Geográfica")

    col1, col2 = st.columns(2)

    with col1:
        ranking_estados = df_filtrado["sigla_uf"].value_counts().reset_index()
        ranking_estados.columns = ["sigla_uf", "queimadas"]
        fig_estados = px.bar(
            ranking_estados,
            x="sigla_uf",
            y="queimadas",
            title="Estados com mais queimadas"
        )
        st.plotly_chart(fig_estados, use_container_width=True)

    if "municipio" in df_filtrado.columns:
        with col2:
            ranking_mun = df_filtrado["municipio"].value_counts().head(10).reset_index()
            ranking_mun.columns = ["municipio", "queimadas"]
            fig_mun = px.bar(
                ranking_mun,
                x="municipio",
                y="queimadas",
                title="Top 10 municípios com mais queimadas"
            )
            st.plotly_chart(fig_mun, use_container_width=True)

    st.subheader("5. Mapa de Calor das Queimadas (Heatmap)")

    if "latitude" in df_filtrado.columns and "longitude" in df_filtrado.columns:
        mapa = folium.Map(location=[-15.78, -47.88], zoom_start=4)
        heat_data = df_filtrado[["latitude", "longitude"]].dropna().values.tolist()
        HeatMap(heat_data, radius=10).add_to(mapa)
        st_folium(mapa, width=1200, height=600)
    else:
        st.warning("Colunas 'latitude' e 'longitude' não encontradas no CSV.")

    st.markdown("""
    #### Como interpretar o mapa de calor
    - **Vermelho / laranja forte** → maior concentração de queimadas na mesma região.  
    - **Amarelo / verde** → quantidade moderada.  
    - **Azul / transparente** → poucos registros.  
    - O mapa considera **todos os anos e estados filtrados** na barra lateral.
    """)

else:
    st.info("Faça upload do arquivo de queimadas para iniciar.")