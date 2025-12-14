import streamlit as st

st.set_page_config(
    page_title="Dashboard de Queimadas no Brasil",
    layout="wide"
)

st.title("Dashboard de Queimadas no Brasil")
st.markdown("""
Este dashboard possui três seções principais:

### **1. Análises SNIS × Queimadas (2016–2022)**
Cruza os registros de queimadas com os indicadores do SNIS, permitindo investigar relações entre saneamento, abastecimento de água, esgoto e a ocorrência de queimadas no Brasil.

### **2. Análises Gerais das Queimadas**
Inclui padrões temporais, sazonalidade, biomas, mapas, rankings e indicadores ambientais (dias sem chuva, precipitação, risco de fogo).

### **3. Análises: O Ciclo do Desmatamento e Fogo**
Investiga a hipótese de que **o aumento do desmatamento leva ao aumento das queimadas**, 
especialmente na Amazônia, onde o fogo é usado para limpar áreas recém-desmatadas.

Use o menu lateral esquerdo para navegar entre as páginas.
""")