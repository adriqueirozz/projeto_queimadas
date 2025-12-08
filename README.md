# projeto_queimadas

Explicação do Código — Dashboard de Queimadas no Brasil
Este código implementa um dashboard interativo usando a biblioteca Streamlit para analisar dados de queimadas no Brasil. O objetivo é facilitar a visualização e análise dos dados de queimadas por estado, mês, intensidade do fogo e localização geográfica.

## Principais Funcionalidades
### Configuração do Dashboard
- Define o título, layout e informações iniciais do dashboard.
###Upload do Arquivo CSV

- Permite ao usuário enviar um arquivo CSV com os dados das queimadas.
- Após o upload, os dados são carregados em um DataFrame do Pandas.
### Filtros Interativos

- O usuário pode filtrar os dados por estados (UF) e meses do ano usando a barra lateral.
- Os dados filtrados são exibidos em uma tabela.
### Visualizações Gráficas

- Gráfico de Barras: Mostra os estados com maior número de queimadas.
- Gráfico de Intensidade: Exibe a intensidade média do fogo por estado, se a coluna estiver presente.
- Gráfico de Sazonalidade: Apresenta a quantidade de queimadas por mês para cada estado.
### Mapa de Calor (Heatmap)

- Utiliza as coordenadas de latitude e longitude para mostrar um mapa de calor das queimadas no Brasil.
- O mapa é interativo e permite visualizar as regiões com maior concentração de queimadas.
## Tecnologias Utilizadas
- Streamlit: Para criar a interface web interativa.
- Pandas: Para manipulação e filtragem dos dados.
- Plotly: Para geração dos gráficos interativos.
- Folium: Para criação do mapa de calor.
- streamlit-folium: Para integrar o mapa Folium ao Streamlit.
## Como Usar
- Execute o código com o comando streamlit run main.py.
- Faça o upload do arquivo CSV com os dados das queimadas.
- Utilize os filtros na barra lateral para explorar os dados.
- Analise os gráficos e o mapa de calor gerados automaticamente.
