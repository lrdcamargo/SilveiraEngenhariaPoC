# Primeiro, instale as bibliotecas necessárias, caso ainda não tenham sido instaladas:
# pip install streamlit plotly pandas seaborn

import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar e preparar os dados
@ st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.replace('\d+', '', regex=True).str.replace(' \(R\)', '', regex=True).str.lstrip('. ')
    data['Mes'] = pd.to_datetime(data['Mes'], format='%Y-%m-%d')
    data['Ano'] = data['Mes'].dt.year
    data.rename(columns={
        'Receita Operacional Liquida': 'Receita Líquida',
        'Mes': 'Mês',
        'Custo dos Produtos/Servicos Vendidos': 'CPV',
        'Lucro Liquido': 'Lucro Líquido',
        'Despesas Administrativas': 'Despesas Operacionais'
    }, inplace=True)
    return data

data = load_data('DRE_2023_2024_Concatenado.csv')
# Após carregar e preparar os dados, adicione uma coluna para indicar se os dados são realizados ou previstos
data['Status'] = data['Mês'].apply(lambda x: 'Previsto' if x.year >= 2024 and x.month >= 2 and x.day >=27 else 'Realizado')
# Dashboard layout
st.title('Dashboard Estratégico e Tático')
st.sidebar.title('Filtros')

# Filtros dinâmicos no sidebar
ano_filtro = st.sidebar.multiselect('Selecione o Ano', options=data['Ano'].unique(), default=data['Ano'].unique())
status_filtro = st.sidebar.multiselect('Selecione o Status', options=data['Status'].unique(), default=data['Status'].unique())

# Filtrando os dados
data_filtrada = data[data['Ano'].isin(ano_filtro) & data['Status'].isin(status_filtro)]


# Filtrando os dados
data_filtrada = data[data['Ano'].isin(ano_filtro) & data['Status'].isin(status_filtro)]
# Gráficos e KPIs
## KPIs
st.header('KPIs Principais')
col1, col2, col3 = st.columns(3)
col1.metric("EBITDA Médio Anual", f"R$ {data_filtrada['EBITDA'].mean():,.2f}")
col2.metric("Margem EBITDA Média", f"{(data_filtrada['EBITDA'] / data_filtrada['Receita Líquida']).mean() * 100:.2f}%")
col3.metric("Lucro Líquido Anual", f"R$ {data_filtrada['Lucro Líquido'].sum():,.2f}")

dados_agregados = data_filtrada.groupby(['Mês', 'ID Empreendimento']).agg({
    'Receita Líquida': 'sum',
    'Lucro Líquido': 'sum'
}).reset_index()

# Calcular a Margem de Lucro após a agregação
dados_agregados['Margem de Lucro'] = dados_agregados['Lucro Líquido'] / dados_agregados['Receita Líquida']

id_para_nome = {
    1: "Usina Solar Vista Alegre",
    2: "Condomínio Parque das Flores",
    3: "Usina Solar Sol Nascente",
    4: "Condomínio Jardim Europa",
    5: "Usina Solar Horizonte"
}

# Substituindo IDs pelos nomes correspondentes
dados_agregados['Nome Empreendimento'] = dados_agregados['ID Empreendimento'].map(id_para_nome)

# Atualizando os gráficos para utilizar os dados agregados

# Gráfico de Receita Líquida por ID Empreendimento ao Longo do Tempo
fig_receita_liquida = px.line(dados_agregados, x='Mês', y='Receita Líquida', color='Nome Empreendimento',
                              title='Evolução da Receita Líquida por Empreendimento')
st.plotly_chart(fig_receita_liquida, use_container_width=True)

# Gráfico de Lucro Líquido por ID Empreendimento ao Longo do Tempo
fig_lucro_liquido = px.line(dados_agregados, x='Mês', y='Lucro Líquido', color='Nome Empreendimento',
                            title='Evolução do Lucro Líquido por Empreendimento')
st.plotly_chart(fig_lucro_liquido, use_container_width=True)

# Gráfico de Margem de Lucro por ID Empreendimento
fig_margem_lucro = px.bar(dados_agregados, x='Mês', y='Margem de Lucro', color='Nome Empreendimento',
                          title='Margem de Lucro por Empreendimento')
st.plotly_chart(fig_margem_lucro, use_container_width=True)