import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Relação Desmatamento x Queimadas", layout="wide")
st.title("Análises: O Ciclo do Desmatamento e Fogo")

# ================================
# CARREGAMENTO DOS DADOS
# ================================

@st.cache_data
def carregar_dados():
    # Carregar Queimadas
    df_queimadas = pd.read_csv("data/dataset_queimadas_definitivo.csv")
    
    # Carregar Desmatamento
    df_desmatamento = pd.read_csv("data/inpe_desmatamento_filtrado.csv")
    
    return df_queimadas, df_desmatamento

try:
    df_q, df_d = carregar_dados()
except FileNotFoundError:
    st.error("Arquivos de dados não encontrados. Verifique se 'dataset_queimadas_definitivo.csv' e 'inpe_desmatamento_filtrado.csv' estão na pasta correta.")
    st.stop()

# ====================================
# PREPARAÇÃO E CRUZAMENTO DOS DADOS
# ====================================

# Contar focos de calor por Ano e Município
focos_por_municipio = df_q.groupby(['ano', 'id_municipio']).size().reset_index(name='total_focos_calor')

# Seleção das colunas relevantes do desmatamento
cols_desmat = ['ano', 'id_municipio', 'bioma', 'desmatado', 'area_total'] 
df_d_clean = df_d[cols_desmat].copy()

# MERGE (Cruzamento)
df_final = pd.merge(df_d_clean, focos_por_municipio, on=['ano', 'id_municipio'], how='inner')

dict_uf = df_q[['id_municipio', 'sigla_uf']].drop_duplicates('id_municipio').set_index('id_municipio')['sigla_uf']
df_final['sigla_uf'] = df_final['id_municipio'].map(dict_uf)

# Amostra dos dados cruzados
st.subheader("Amostra dos dados cruzados (Desmatamento + Queimadas)")
st.dataframe(df_final.head(20))

# ================================
# FILTROS NA SIDEBAR
# ================================

st.sidebar.header("Filtros de Análise")

# Filtro de Bioma (Focado na Amazônia por padrão, mas permitindo outros)
biomas_disponiveis = sorted(df_final['bioma'].unique())
biomas_selecionados = st.sidebar.multiselect("Selecione os Biomas", biomas_disponiveis, default=biomas_disponiveis)

# Filtro de Ano
anos_disponiveis = sorted(df_final['ano'].unique())
anos_selecionados = st.sidebar.slider("Intervalo de Anos", min(anos_disponiveis), max(anos_disponiveis), (min(anos_disponiveis), max(anos_disponiveis)))

# Aplicação dos filtros
df_filtrado = df_final[
    (df_final['bioma'].isin(biomas_selecionados)) & (df_final['ano'] >= anos_selecionados[0]) & (df_final['ano'] <= anos_selecionados[1])
]

# ================================
# VISUALIZAÇÕES (DASHBOARDS)
# ================================

# KPI's Gerais
col1, col2, col3 = st.columns(3)
col1.metric("Área Total Desmatada (Seleção)", f"{df_filtrado['desmatado'].sum():,.0f} km²")
col2.metric("Total de Focos de Calor (Seleção)", f"{df_filtrado['total_focos_calor'].sum():,.0f}")

try:
    correlacao = df_filtrado['desmatado'].corr(df_filtrado['total_focos_calor'])
    col3.metric("Correlação (Pearson)", f"{correlacao:.2f}", help="Perto de 1: Forte relação positiva. Perto de 0: Sem relação.")
except:
    col3.metric("Correlação", "N/A")

st.divider()

# GRÁFICO 1: SCATTER PLOT (A PROVA DOS 9)
st.subheader("1. Correlação: Quanto mais desmata, mais queima?")
st.markdown("Cada ponto é um município em um ano específico.")

if not df_filtrado.empty:
    fig_scatter = px.scatter(
        df_filtrado,
        x="desmatado",
        y="total_focos_calor",
        color="bioma",
        hover_data=["sigla_uf", "ano", "id_municipio"],
        trendline="ols", # Adiciona linha de tendência
        labels={"desmatado": "Área Desmatada (km²)", "total_focos_calor": "Focos de Queimada"},
        title="Relação Desmatamento vs. Queimadas",
        opacity=0.6
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("Sem dados suficientes para gerar o gráfico de dispersão com os filtros atuais.")

# GRÁFICO 2: EVOLUÇÃO TEMPORAL (EIXOS DUPLOS)
st.subheader("2. Evolução Temporal: As curvas andam juntas?")

# Agrupando por ano
df_ano = df_filtrado.groupby('ano')[['desmatado', 'total_focos_calor']].sum().reset_index()

fig_dual = go.Figure()

# Linha de Desmatamento (Eixo Y da esquerda)
fig_dual.add_trace(go.Scatter(
    x=df_ano['ano'], 
    y=df_ano['desmatado'], 
    name='Área Desmatada (km²)',
    line=dict(color='green', width=3)
))

# Linha de Queimadas (Eixo Y da direita)
fig_dual.add_trace(go.Scatter(
    x=df_ano['ano'], 
    y=df_ano['total_focos_calor'], 
    name='Focos de Calor',
    line=dict(color='red', width=3, dash='dot'),
    yaxis='y2'
))

# Layout com dois eixos Y
fig_dual.update_layout(
    title="Linha do Tempo: Desmatamento e Fogo",
    xaxis=dict(title="Ano"),
    
    # EIXO Y DA ESQUERDA (VERDE - DESMATAMENTO)
    yaxis=dict(
        title=dict(
            text="Área Desmatada (km²)",
            font=dict(color="green")
        ),
        tickfont=dict(color="green")
    ),
    
    # EIXO Y DA DIREITA (VERMELHO - QUEIMADAS)
    yaxis2=dict(
        title=dict(
            text="Qtd Focos",
            font=dict(color="red")
        ),
        tickfont=dict(color="red"),
        overlaying='y',
        side='right'
    ),
    
    legend=dict(x=0.1, y=1.1, orientation="h")
)

st.plotly_chart(fig_dual, use_container_width=True)

# GRÁFICO 3: RANKING
st.subheader("3. Top 10 Municípios: Comparativo (Logarítmico)")

# Agrupar por município e ordenar os 10 maiores
df_rank = df_filtrado.groupby(['id_municipio', 'sigla_uf'])[['desmatado', 'total_focos_calor']].sum().reset_index()
top_10_desmat = df_rank.sort_values(by='desmatado', ascending=False).head(10)
top_10_desmat['label'] = top_10_desmat['id_municipio'].astype(str) + " (" + top_10_desmat['sigla_uf'] + ")"
fig_bar = go.Figure()

# Barra 1: Desmatamento (Verde)
fig_bar.add_trace(go.Bar(
    x=top_10_desmat['label'],
    y=top_10_desmat['desmatado'],
    name='Área Desmatada (km²)',
    marker_color='forestgreen',
    yaxis='y',
    offsetgroup=1 # Força a separação das barras
))

# Barra 2: Queimadas (Vermelho)
fig_bar.add_trace(go.Bar(
    x=top_10_desmat['label'],
    y=top_10_desmat['total_focos_calor'],
    name='Focos de Queimada',
    marker_color='firebrick',
    yaxis='y2',
    offsetgroup=2 # Força a separação das barras
))

fig_bar.update_layout(
    title="Top 10 Municípios: Comparativo Desmatamento vs Queimadas",
    xaxis=dict(title="Município"),
    
    # Eixo Esquerdo (Verde - Desmatamento)
    yaxis=dict(
        title=dict(text="Área Desmatada (km²)", font=dict(color="forestgreen")),
        tickfont=dict(color="forestgreen"),
        type="linear"
    ),
    
    # Eixo Direito (Vermelho - Focos)
    yaxis2=dict(
        title=dict(text="Qtd Focos de Queimada", font=dict(color="firebrick")),
        tickfont=dict(color="firebrick"),
        overlaying='y',
        side='right',
        type="linear"
    ),
    
    legend=dict(x=0.1, y=1.1, orientation="h"),
    barmode='group'
)

st.plotly_chart(fig_bar, use_container_width=True)