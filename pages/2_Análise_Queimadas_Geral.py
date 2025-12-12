import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

st.title("Análises Gerais das Queimadas")
df = df = pd.read_csv("data/dataset_queimadas_definitivo.csv")

# ================================
# FILTROS
# ================================

st.sidebar.header("Filtros de Análise")

anos = st.sidebar.multiselect(
    "Selecione os anos",
    sorted(df["ano"].unique()),
    default=sorted(df["ano"].unique())
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

df_filtrado = df[
    (df["ano"].isin(anos)) &
    (df["sigla_uf"].isin(estados)) &
    (df["mes"].isin(meses))
]

if df_filtrado.empty:
    st.warning("Nenhum dado após filtros.")
    st.stop()

st.subheader("Amostra dos dados filtrados")
st.dataframe(df_filtrado.head(20))

# ============================================================
# 1 — Padrões temporais
# ============================================================
st.header("1. Padrões Temporais")

df_serie = df_filtrado.groupby(["ano", "mes"]).size().reset_index(name="queimadas")
df_serie["ano_mes"] = df_serie["ano"].astype(str) + "-" + df_serie["mes"].astype(str)

fig_serie = px.line(df_serie, x="ano_mes", y="queimadas", markers=True)
st.plotly_chart(fig_serie, use_container_width=True)

# ============================================================
# 2 — Sazonalidade
# ============================================================
st.header("2. Sazonalidade")

df_sazon = df_filtrado.groupby("mes").size().reset_index(name="queimadas")

fig_sazon = px.bar(df_sazon, x="mes", y="queimadas")
st.plotly_chart(fig_sazon, use_container_width=True)

heat = df_filtrado.groupby(["ano", "mes"]).size().reset_index(name="queimadas")

fig_heat = px.density_heatmap(
    heat,
    x="mes",
    y="ano",
    z="queimadas",
    color_continuous_scale="OrRd"
)
st.plotly_chart(fig_heat, use_container_width=True)

# ============================================================
# 3 — Dados ambientais (2023+)
# ============================================================
st.header("3. Indicadores Ambientais (2023+)")

df_2023 = df[df["ano"] >= 2023]

if not df_2023.empty:

    fig_b = px.box(
        df_2023,
        x="sigla_uf",
        y="dias_sem_chuva"
    )
    st.plotly_chart(fig_b, use_container_width=True)

# ============================================================
# 4 — Rankings geográficos
# ============================================================
st.header("4. Rankings Geográficos")

col1, col2 = st.columns(2)

with col1:
    ranking_uf = df_filtrado["sigla_uf"].value_counts().reset_index()
    ranking_uf.columns = ["estado", "queimadas"]
    fig_uf = px.bar(ranking_uf, x="estado", y="queimadas")
    st.plotly_chart(fig_uf, use_container_width=True)

with col2:
    if "municipio" in df_filtrado.columns:
        ranking_mun = df_filtrado["municipio"].value_counts().head(10).reset_index()
        ranking_mun.columns = ["municipio", "queimadas"]
        fig_mun = px.bar(
            ranking_mun,
            x="municipio",
            y="queimadas"
        )
        st.plotly_chart(fig_mun, use_container_width=True)

# ============================================================
# 5 — Biomas
# ============================================================
st.header("5. Distribuição por Bioma")

if "bioma" in df_filtrado.columns:
    biomas = df_filtrado["bioma"].value_counts().reset_index()
    biomas.columns = ["bioma", "queimadas"]

    fig_bio = px.bar(biomas, x="bioma", y="queimadas", color="bioma")
    st.plotly_chart(fig_bio, use_container_width=True)

# ============================================================
# 6 — Heatmap geral
# ============================================================
st.header("6. Mapa de Calor Geral das Queimadas")

if "latitude" in df_filtrado.columns and "longitude" in df_filtrado.columns:
    mapa = folium.Map(location=[-15.78, -47.88], zoom_start=4)

    heat_data = df_filtrado[["latitude", "longitude"]].dropna().values.tolist()

    HeatMap(heat_data, radius=10).add_to(mapa)

    st_folium(mapa, width=1200, height=600)

st.markdown("""
### Como interpretar o Heatmap
- Vermelho → maior concentração de queimadas  
- Amarelo/verde → concentração moderada  
- Azul/transparente → poucos registros  
""")
