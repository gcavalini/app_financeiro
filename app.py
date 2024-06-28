
import streamlit as st
import pandas as pd
import plotly.express as px

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

# Botão para limpar todos os dados
if st.button('Limpar Todos os Dados'):
    dados = pd.DataFrame(columns=['Data', 'Tipo', 'Subcategoria', 'Valor', 'Descrição'])
    save_data(dados)
    st.success('Todos os dados foram limpos!')

# Carregar os dados
dados = load_data()

# Exibir os dados em uma tabela
st.subheader('Dados Atuais')
st.dataframe(dados)

# Gráfico de barras
st.subheader('Gráfico de Receitas e Despesas')
if not dados.empty:
    dados['Data'] = pd.to_datetime(dados['Data'])
    dados['Mês'] = dados['Data'].dt.to_period('M')

    # Resumo por mês e tipo
    resumo_tipo = dados.groupby(['Mês', 'Tipo'])['Valor'].sum().unstack().fillna(0)
    fig_tipo = px.bar(resumo_tipo, x=resumo_tipo.index.astype(str), y=resumo_tipo.columns, barmode='group',
                      title='Receitas e Despesas Mensais')
    st.plotly_chart(fig_tipo)

    # Resumo por mês e subcategoria
    resumo_subcat = dados.groupby(['Mês', 'Tipo', 'Subcategoria'])['Valor'].sum().unstack().fillna(0)
    fig_subcat = px.bar(resumo_subcat, x=resumo_subcat.index.astype(str), y=resumo_subcat.columns,
                        title='Receitas e Despesas por Subcategorias')
    st.plotly_chart(fig_subcat)

    # Exibir saldo
    saldo = resumo_tipo.sum(axis=1).cumsum().iloc[-1]
    st.subheader(f'Saldo Atual: R$ {saldo:.2f}')
else:
    st.write('Nenhum dado disponível.')

