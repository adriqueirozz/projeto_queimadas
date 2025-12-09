import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import plotly.express as px

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
# UPLOAD DO ARQUIVO
# ================================
st.sidebar.header("Upload do Dataset")
uploaded_file = st.sidebar.file_uploader("Envie o arquivo CSV", type=["csv"])


if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df_2023 = df[df["ano"] >= 2023]
    # Garante que as colunas essenciais existam
    col_ano = "ano"
    col_mes = "mes"
    col_uf = "sigla_uf"

    if not all([c in df.columns for c in [col_ano, col_mes, col_uf]]):
        st.error("O CSV precisa conter as colunas: ano, mes, sigla_uf.")
        st.stop()

    st.success("Arquivo carregado com sucesso!")

    # ================================
    # FILTROS
    # ================================
    st.sidebar.header("Filtros")

    anos = st.sidebar.multiselect(
        "Selecione os anos",
        sorted(df[col_ano].unique()),
        default=sorted(df[col_ano].unique())
    )

    estados = st.sidebar.multiselect(
        "Selecione os estados (UF)",
        sorted(df[col_uf].unique()),
        default=sorted(df[col_uf].unique())
    )

    meses = st.sidebar.multiselect(
        "Selecione os meses",
        sorted(df[col_mes].unique()),
        default=sorted(df[col_mes].unique())
    )

    df_filtrado = df[
        (df[col_ano].isin(anos)) &
        (df[col_uf].isin(estados)) &
        (df[col_mes].isin(meses))
    ]

    if df_filtrado.empty:
        st.warning("Nenhum dado após aplicar os filtros.")
        st.stop()

    st.subheader("📌 Dados filtrados")
    st.dataframe(df_filtrado.head(20))

    # ================================
    # 1 — PADRÕES TEMPORAIS
    # ================================
    st.header("1. Padrões Temporais")

    df_serie = df_filtrado.groupby([col_ano, col_mes]).size().reset_index(name="queimadas")
    df_serie["ano_mes"] = df_serie[col_ano].astype(str) + "-" + df_serie[col_mes].astype(str)

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

    # Perfil médio mensal
    sazonalidade_media = df_filtrado.groupby(col_mes).size().reset_index(name="queimadas")

    fig_sazon = px.bar(
        sazonalidade_media,
        x=col_mes,
        y="queimadas",
        title="Sazonalidade média — queimadas por mês"
    )
    st.plotly_chart(fig_sazon, use_container_width=True)

    # Heatmap de meses x anos
    heat = df_filtrado.groupby([col_ano, col_mes]).size().reset_index(name="queimadas")

    fig_heat = px.density_heatmap(
        heat,
        x=col_mes,
        y=col_ano,
        z="queimadas",
        color_continuous_scale="OrRd",
        title="Mapa de calor — Sazonalidade (Mês x Ano)"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # ================================
    # 3 — Relação entre risco de fogo × precipitação
    # ================================
   

    st.header("3. Gráficos após 2023")

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
        ranking_estados = df_filtrado[col_uf].value_counts().reset_index()
        ranking_estados.columns = [col_uf, "queimadas"]
        fig_estados = px.bar(
            ranking_estados,
            x=col_uf,
            y="queimadas",
            title="Estados com mais queimadas"
        )
        st.plotly_chart(fig_estados, use_container_width=True)

    # Municípios (se existir coluna)
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

    # Mapa de calor
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
    st.info("Faça upload de um arquivo CSV para começar.")
