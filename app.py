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

# Estilo CSS para o botão "Limpar Todos os Dados"
st.markdown("""
    <style>
    .css-1q8dd3e {
        background-color: #8B0000 !important;
        color: white !important;
        float: right;
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
    cor_input = '#DFF2BF'
else:
    subcategoria = st.selectbox('Subcategoria', ['Cartão de Crédito', 'Gastos Fixos'])
    cor_input = '#FFBABA'

valor = st.number_input('Valor', min_value=0.0, format="%.2f")
data = st.date_input('Data')
descricao = st.text_input('Descrição', '')

# Aplicar cor ao campo selecionado
st.markdown(f"""
    <style>
    .st-bb {{
        background-color: {cor_input} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# Botão para adicionar a entrada
if st.button('Adicionar'):
    novo_dado = pd.DataFrame({'Data': [data], 'Tipo': [tipo], 'Subcategoria': [subcategoria], 'Valor': [valor], 'Descrição': [descricao]})
    dados = load_data()
    dados = pd.concat([dados, novo_dado], ignore_index=True)
    save_data(dados)
    st.success('Entrada adicionada com sucesso!')

# Carregar os dados
dados = load_data()

# Filtros para seleção de meses e dias
st.sidebar.header('Filtros')
mes_selecionado = st.sidebar.selectbox('Mês', range(1, 13), format_func=lambda x: calendar.month_name[x])
dia_selecionado = st.sidebar.slider('Dia', 1, 31, 1)

# Filtrar dados com base na seleção do mês e dia
dados['Data'] = pd.to_datetime(dados['Data'])
dados_filtrados = dados[(dados['Data'].dt.month == mes_selecionado) & (dados['Data'].dt.day == dia_selecionado)]

# Exibir os dados em uma tabela
st.subheader('Dados Atuais')
st.dataframe(dados_filtrados)

# Gráfico de barras
st.subheader('Gráfico de Receitas e Despesas')
if not dados_filtrados.empty:
    dados_filtrados['Mês'] = dados_filtrados['Data'].dt.to_period('M')

    # Resumo por mês e tipo
    resumo_tipo = dados_filtrados.groupby(['Mês', 'Tipo'])['Valor'].sum().unstack().fillna(0)
    fig_tipo = px.bar(resumo_tipo, x=resumo_tipo.index.astype(str), y=resumo_tipo.columns, barmode='group',
                      title='Receitas e Despesas Mensais')
    st.plotly_chart(fig_tipo)

    # Resumo por mês e subcategoria
    resumo_subcat = dados_filtrados.groupby(['Mês', 'Tipo', 'Subcategoria'])['Valor'].sum().unstack().fillna(0)
    fig_subcat = px.bar(resumo_subcat, x=resumo_subcat.index.astype(str), y=resumo_subcat.columns,
                        title='Receitas e Despesas por Subcategorias')
    st.plotly_chart(fig_subcat)

    # Exibir saldo
    saldo = resumo_tipo.sum(axis=1).cumsum().iloc[-1]
    st.subheader(f'Saldo Atual: R$ {saldo:.2f}')
else:
    st.write('Nenhum dado disponível.')
