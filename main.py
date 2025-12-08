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

    st.success("Arquivo carregado com sucesso!")

    # ================================
    # FILTROS
    # ================================
    st.sidebar.header("Filtros")

    estados = st.sidebar.multiselect(
        "Selecione os estados (UF)", 
        sorted(df["sigla_uf"].unique()),
        default=sorted(df["sigla_uf"].unique())
    )

    meses = st.sidebar.multiselect(
        "Selecione os meses",
        sorted(df["mes"].unique()),
        default=sorted(df["mes"].unique())
    )

    df_filtrado = df[df["sigla_uf"].isin(estados)]
    df_filtrado = df_filtrado[df_filtrado["mes"].isin(meses)]

    st.subheader("📌 Dados filtrados")
    st.dataframe(df_filtrado.head(20))


    # ================================
    # 1. GRÁFICO — ESTADOS COM MAIS QUEIMADAS
    # ================================
    st.subheader("Estados com mais queimadas")

    contagem_estados = df_filtrado["sigla_uf"].value_counts().reset_index()
    contagem_estados.columns = ["sigla_uf", "queimadas"]

    fig1 = px.bar(
        contagem_estados,
        x="sigla_uf",
        y="queimadas",
        text="queimadas",
        title="Estados com maior número de queimadas"
    )
    st.plotly_chart(fig1, use_container_width=True)


    # ================================
    # 2. GRÁFICO — INTENSIDADE DO FOGO POR ESTADO
    # ================================
    st.subheader("Intensidade média do fogo por estado")

    if "potencia_radiativa_fogo" in df_filtrado.columns:
        intensidade = df_filtrado.groupby("sigla_uf")["potencia_radiativa_fogo"].mean().reset_index()

        fig2 = px.bar(
            intensidade,
            x="sigla_uf",
            y="potencia_radiativa_fogo",
            title="Intensidade média do fogo por estado"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Coluna 'potencia_radiativa_fogo' não encontrada no CSV.")


    # ================================
    # 3. SAZONALIDADE
    # ================================
    st.subheader("Sazonalidade (Queimadas por Mês por Estado)")

    sazonalidade = df_filtrado.groupby(["mes", "sigla_uf"]).size().reset_index(name="queimadas")

    fig3 = px.line(
        sazonalidade,
        x="mes",
        y="queimadas",
        color="sigla_uf",
        markers=True,
        title="Sazonalidade das queimadas"
    )
    st.plotly_chart(fig3, use_container_width=True)


    # ================================
    # 4. MAPA DE CALOR (HEATMAP) — FOLIUM
    # ================================
    st.subheader("Mapa de Calor das Queimadas (Heatmap)")

    if "latitude" in df_filtrado.columns and "longitude" in df_filtrado.columns:
        mapa = folium.Map(location=[-15.78, -47.88], zoom_start=4)

        heat_data = df_filtrado[["latitude", "longitude"]].dropna().values.tolist()

        HeatMap(heat_data, radius=10).add_to(mapa)

        st_folium(mapa, width=1200, height=600)
    else:
        st.warning("Colunas 'latitude' e 'longitude' não encontradas no CSV.")


else:
    st.info("👈 Faça upload de um arquivo CSV para começar.")
