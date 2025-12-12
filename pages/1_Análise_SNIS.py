import streamlit as st
import pandas as pd
import plotly.express as px
import os
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.title("Análises SNIS × Queimadas (2016–2022)")

# ================================
# CARREGAR SNIS
# ================================
path_snis = "data/snis_filtrado.csv"

if os.path.exists(path_snis):
    df_snis = pd.read_csv(path_snis)
    st.success("Dataset SNIS carregado (2016–2022).")
else:
    st.error("Arquivo 'snis_filtrado.csv' não encontrado em /data.")
    st.stop()

# ================================
# UPLOAD DO ARQUIVO DE QUEIMADAS
# ================================

df = pd.read_csv("data/dataset_queimadas_definitivo.csv")

# Filtros
anos_queimadas = sorted(df["ano"].unique())
anos_snis = sorted(df_snis["ano"].unique())

# MERGE
df_merge = df.merge(
    df_snis,
    on=["ano", "sigla_uf", "id_municipio"],
    how="left"
)

st.subheader("Amostra dos dados integrados (SNIS + Queimadas)")
st.dataframe(df_merge.head(20))

# Sidebar filters
st.sidebar.header("Filtros de Análise")
anos = st.sidebar.multiselect("Selecione os anos", anos_queimadas, default=anos_queimadas)
estados = st.sidebar.multiselect(
    "Selecione os estados",
    sorted(df["sigla_uf"].unique()),
    default=sorted(df["sigla_uf"].unique())
)

df_filt = df_merge[
    (df_merge["ano"].isin(anos)) &
    (df_merge["sigla_uf"].isin(estados))
]

if df_filt.empty:
    st.warning("Nenhum dado após filtros.")
    st.stop()

anos_validos = [a for a in anos if a in anos_snis]

if not anos_validos:
    st.info("O SNIS está disponível apenas para 2016–2022. Escolha anos compatíveis.")
    st.stop()

df_cross = df_filt[df_filt["ano"].isin(anos_validos)]

# ============================================================
# 1 — Relação saneamento × queimadas (UF)
# ============================================================
st.header("1 — Relações SNIS × Queimadas por Estado")

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
    color="sigla_uf",
    trendline="ols",
    size="queimadas",
    title="Atendimento Urbano de Água × Queimadas"
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.scatter(
    df_uf, x="indice_coleta_esgoto", y="queimadas",
    color="sigla_uf", trendline="ols",
    title="Coleta de Esgoto × Queimadas (UF)"
)
st.plotly_chart(fig2, use_container_width=True)

fig3 = px.scatter(
    df_uf, x="indice_tratamento_esgoto", y="queimadas",
    color="sigla_uf", trendline="ols",
    title="Tratamento de Esgoto × Queimadas (UF)"
)
st.plotly_chart(fig3, use_container_width=True)

fig4 = px.scatter(
    df_uf, x="indice_perda_distribuicao_agua", y="queimadas",
    color="sigla_uf", trendline="ols",
    title="Perdas de Água × Queimadas (UF)"
)
st.plotly_chart(fig4, use_container_width=True)

fig5 = px.scatter(
    df_uf, x="extensao_rede_agua", y="queimadas",
    color="sigla_uf", trendline="ols",
    title="Extensão da Rede de Água × Queimadas (UF)"
)
st.plotly_chart(fig5, use_container_width=True)

# ============================================================
# 2 — Mapa de calor ponderado pelo SNIS
# ============================================================
st.header("2 — Heatmap ponderado pelo atendimento de água")

if "latitude" in df_cross.columns and "longitude" in df_cross.columns:
    mapa = folium.Map(location=[-15.78, -47.88], zoom_start=4)

    heat_data = df_cross[["latitude", "longitude", "indice_atendimento_urbano_agua"]].dropna()

    HeatMap(
        heat_data.values.tolist(),
        radius=10,
        gradient={0.2: "blue", 0.5: "green", 0.8: "orange", 1: "red"}
    ).add_to(mapa)

    st_folium(mapa, width=1200, height=600)

else:
    st.warning("Colunas de latitude/longitude ausentes no dataset.")
