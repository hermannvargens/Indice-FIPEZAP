import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard FipeZap - Curitiba", layout="wide")

st.title("📈 Séries Históricas FipeZap - Curitiba")
st.markdown("Dados extraídos diretamente da planilha oficial do FipeZap.")

# URL fixa conforme fornecido
URL_FIPE = "https://downloads.fipe.org.br/indices/fipezap/fipezap-serieshistoricas.xlsx"

@st.cache_data
def carregar_dados():
    try:
        # Lê a aba 'Curitiba'. 
        # header=3 significa que a linha 4 do Excel (índice 3 do Python) contém os títulos
        df = pd.read_excel(URL_FIPE, sheet_name='Curitiba', header=3)
        
        # Seleção de Colunas baseada na descrição:
        # Coluna B é o índice 1 (Data)
        # Colunas C até G são índices 2, 3, 4, 5, 6
        colunas_interesse = [1, 2, 3, 4, 5, 6]
        
        # Filtra apenas as colunas desejadas usando iloc (seleção por posição)
        df_limpo = df.iloc[:, colunas_interesse].copy()
        
        # Renomeia a primeira coluna (antiga coluna B) para 'Data' para padronizar
        nome_coluna_data = df_limpo.columns[0]
        df_limpo.rename(columns={nome_coluna_data: 'Data'}, inplace=True)
        
        # Converte a coluna Data para formato de data e remove linhas vazias/inválidas
        df_limpo['Data'] = pd.to_datetime(df_limpo['Data'], errors='coerce')
        df_limpo = df_limpo.dropna(subset=['Data'])
        
        return df_limpo
        
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
        return None

# Carrega os dados
with st.spinner('Baixando planilha do FipeZap...'):
    df = carregar_dados()

if df is not None:
    # Barra lateral ou topo para filtros
    st.subheader("Visualização dos Índices")
    
    # Pega todas as colunas menos a 'Data'
    opcoes_series = df.columns.tolist()
    opcoes_series.remove('Data')
    
    # Multiselect: Usuário escolhe quais séries quer ver (Padrão: seleciona todas)
    series_selecionadas = st.multiselect(
        "Escolha as séries para visualizar:",
        options=opcoes_series,
        default=opcoes_series
    )
    
    if series_selecionadas:
        # Gráfico de Linha Interativo com Plotly
        fig = px.line(
            df, 
            x='Data', 
            y=series_selecionadas,
            title='Evolução Histórica - Curitiba',
            labels={'value': 'Índice', 'variable': 'Série'},
            markers=True
        )
        
        # Melhora o layout do eixo X para datas
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1a", step="year", stepmode="backward"),
                    dict(count=5, label="5a", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Exibir dados tabulares (opcional)
        with st.expander("Ver dados em tabela"):
            st.dataframe(df[['Data'] + series_selecionadas].sort_values(by='Data', ascending=False))
            
    else:
        st.warning("Por favor, selecione pelo menos uma série para visualizar o gráfico.")
