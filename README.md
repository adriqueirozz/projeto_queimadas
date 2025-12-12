# Dashboard de Queimadas no Brasil

Este projeto consiste em um **dashboard interativo desenvolvido com Streamlit**, voltado para a análise integrada de queimadas no Brasil e sua relação com fatores ambientais e de saneamento.

O sistema possui duas seções principais:

---

# 1. Análises SNIS × Queimadas (2016–2022)

Página voltada para investigar **relações entre saneamento básico (SNIS)** e a ocorrência de queimadas.  
Os dados carregados automaticamente incluem:

- Índices de abastecimento de água  
- Coleta e tratamento de esgoto  
- Perdas na distribuição  
- Extensão de redes  
- Registros de queimadas no mesmo município/ano

### Integração automática dos datasets  
Os arquivos **snis_filtrado.csv** e **dataset_queimadas_definitivo.csv** são carregados da pasta `/data/`.  
Não há necessidade de upload pelo usuário.

### Cruzamento SNIS × queimadas  
Os dados são combinados automaticamente pelos campos:
- ano,
- sigla_uf,
- id_municipio.


### Visualizações incluídas  
- 5 gráficos de dispersão com regressão OLS  
- Análises agregadas por estado (UF)  
- Heatmap georreferenciado ponderado pelo índice de atendimento urbano de água  

Essas análises permitem investigar relações socioambientais, identificar padrões geográficos e discutir vulnerabilidades municipais.

---

# 2. Análises Gerais das Queimadas

Inclui:

- Séries temporais  
- Sazonalidade  
- Padrões mensais  
- Distribuição por bioma  
- Ranking por municípios e estados  
- Mapa de calor nacional  
- Indicadores ambientais modernos (2023+):  
  - Dias sem chuva  
  - Precipitação  
  - Risco de fogo  
  - Potência radiativa do fogo (FRP)

Todos os dados são carregados automaticamente da pasta `/data/`.

---

# Estrutura do Projeto

```bash
dashboard_queimadas/
│
├── main.py
│
├── pages/
│ ├── 1_Análise_SNIS.py
│ └── 2_Análise_Queimadas_Geral.py
│
├── data/
│ ├── dataset_queimadas_definitivo.csv
│ └── snis_filtrado.csv
│
├── requirements.txt
```
---

# Como Rodar o Projeto

## 1. Criar ambiente virtual (opcional, mas recomendado)

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate  # Mac / Linux
```

```bash
✔️ 2. Instalar dependências
pip install -r requirements.txt
```

O projeto abrirá automaticamente no navegador em:
```bash
http://localhost:8501
```

Requisitos (requirements.txt)
```bash
streamlit
pandas
numpy
plotly
folium
streamlit-folium
statsmodels
```

# Resumo das Funcionalidades Técnicas
### Página 1 — SNIS × Queimadas

- Merge automático dos datasets
- Filtros por ano e estado
- Regressão linear OLS em tempo real
- Heatmap ponderado pelo atendimento de água
- Agrupamento por UF

### Página 2 — Análises Gerais das Queimadas

- Gráficos temporais e padrões mensais
- Sazonalidade e distribuição por bioma
- Rankings regionais
- Heatmap nacional
- Indicadores ambientais modernos
- Painel totalmente interativo
