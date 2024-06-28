import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

# Nome do arquivo Excel
FILENAME = 'financas.xlsx'

# Carregar dados do arquivo existente ou criar um novo DataFrame
def load_data():
    try:
        return pd.read_excel(FILENAME)
    except FileNotFoundError:
        return pd.DataFrame(columns=['Data', 'Tipo', 'Subcategoria', 'Valor', 'Descrição'])

# Salvar dados no arquivo Excel
def save_data(data):
    data.to_excel(FILENAME, index=False)

# Streamlit App
st.title('Gestão de Finanças Pessoais')

# Estilo CSS para o botão "Limpar Todos os Dados" e o seletor de tipo
st.markdown("""
    <style>
    .css-1q8dd3e {
        background-color: #8B0000 !important;
        color: white !important;
        float: right;
    }
    .stSelectbox label, .stSelectbox select {
        background-color: inherit;
    }
    .stSelectbox select:focus {
        background-color: inherit;
    }
    .stSelectbox[data-baseweb="select"] .css-1hwfws3 {
        background-color: #DFF2BF !important;  /* Cor verde claro para Receita */
    }
    .stSelectbox[data-baseweb="select"] .css-1hwfws3[data-selected=true] {
        background-color: #C9E2A6 !important;  /* Cor verde um pouco mais escuro para Receita */
    }
    .stSelectbox[data-baseweb="select"]:nth-of-type(1) .css-1hwfws3 {
        background-color: #FFBABA !important;  /* Cor vermelha para Despesa */
    }
    .stSelectbox[data-baseweb="select"]:nth-of-type(1) .css-1hwfws3[data-selected=true] {
        background-color: #E57373 !important;  /* Cor vermelha um pouco mais escuro para Despesa */
    }
    </style>
    """, unsafe_allow_html=True)

# Botão para limpar todos os dados (posicionado no canto superior direito)
if st.button('Limpar Todos os Dados'):
    dados = pd.DataFrame(columns=['Data', 'Tipo', 'Subcategoria', 'Valor', 'Descrição'])
    save_data(dados)
    st.success('Todos os dados foram limpos!')

# Entradas do usuário
tipo = st.selectbox('Tipo', ['Receita', 'Despesa'])
if tipo == 'Receita':
    subcategoria = st.selectbox('Subcategoria', ['Salário', 'Outras'])
else:
    subcategoria = st.selectbox('Subcategoria', ['Cartão de Crédito', 'Gastos Fixos'])

valor = st.number_input('Valor', min_value=0.0, format="%.2f")
data = st.date_input('Data')
descricao = st.text_input('Descrição', '')

# Botão para adicionar a entrada
if st.button('Adicionar'):
    novo_dado = pd.DataFrame({'Data': [data], 'Tipo': [tipo], 'Subcategoria': [subcategoria], 'Valor': [valor], 'Descrição': [descricao]})
    dados = load_data()
    dados = pd.concat([dados, novo_dado], ignore_index=True)
    save_data(dados)
    st.success('Entrada adicionada com sucesso!')

# Carregar os dados
dados = load_data()

# Converter a coluna 'Data' para datetime, ignorando erros
dados['Data'] = pd.to_datetime(dados['Data'], errors='coerce')

# Remover linhas com datas inválidas
dados = dados.dropna(subset=['Data'])

# Certificar que as colunas de data estão em formato inteiro
dados['Data'] = pd.to_datetime(dados['Data'])
dados['Ano'] = dados['Data'].dt.year
dados['Mês'] = dados['Data'].dt.month

# Filtros para seleção de anos e meses
st.sidebar.header('Filtros')
anos_disponiveis = dados['Ano'].unique().astype(int)
ano_selecionado = st.sidebar.selectbox('Ano', sorted(anos_disponiveis))
mes_selecionado = st.sidebar.selectbox('Mês', range(1, 13), format_func=lambda x: calendar.month_name[x])

# Filtrar dados com base na seleção de ano e mês
dados_filtrados = dados[
    (dados['Ano'] == ano_selecionado) &
    (dados['Mês'] == mes_selecionado)
]

# Exibir os dados em uma tabela
st.subheader('Dados Atuais')
st.dataframe(dados_filtrados)

# Gráfico de barras
st.subheader('Gráfico de Receitas e Despesas')
if not dados_filtrados.empty:
    dados_filtrados['Mês_Periodo'] = dados_filtrados['Data'].dt.to_period('M')

    # Resumo por mês e tipo
    resumo_tipo = dados_filtrados.groupby(['Mês_Periodo', 'Tipo'])['Valor'].sum().unstack().fillna(0)
    fig_tipo = px.bar(resumo_tipo, x=resumo_tipo.index.astype(str), y=resumo_tipo.columns, barmode='group',
                      title='Receitas e Despesas Mensais')
    st.plotly_chart(fig_tipo)

    # Resumo por mês e subcategoria
    resumo_subcat = dados_filtrados.groupby(['Mês_Periodo', 'Tipo', 'Subcategoria'])['Valor'].sum().unstack().fillna(0)
    fig_subcat = px.bar(resumo_subcat, x=resumo_subcat.index.astype(str), y=resumo_subcat.columns,
                        title='Receitas e Despesas por Subcategorias')
    st.plotly_chart(fig_subcat)

    # Calcular saldo
    total_receitas = resumo_tipo.get('Receita', 0).sum()
    total_despesas = resumo_tipo.get('Despesa', 0).sum()
    saldo = total_receitas - total_despesas
    st.subheader(f'Saldo Atual: R$ {saldo:.2f}')
else:
    st.write('Nenhum dado disponível.')





