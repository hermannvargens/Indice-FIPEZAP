import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard FipeZap - Completo", layout="wide")

st.title("📈 Dashboard Imobiliário FipeZap - Curitiba")
st.markdown("Dados extraídos diretamente das Séries Históricas do FipeZap.")

URL_FIPE = "https://downloads.fipe.org.br/indices/fipezap/fipezap-serieshistoricas.xlsx"

@st.cache_data
def carregar_dados_completos():
    try:
        # Carrega a aba 'Curitiba' com cabeçalho na linha 4 (index 3)
        df = pd.read_excel(URL_FIPE, sheet_name='Curitiba', header=3)
        
        # Coluna B (Data) é o índice 1
        # Vamos extrair a data e limpar
        data_col = df.iloc[:, 1]
        data_col = pd.to_datetime(data_col, errors='coerce')
        
        # Remove linhas onde a data é inválida (NaT)
        valid_indices = data_col.dropna().index
        df_limpo = df.loc[valid_indices].copy()
        df_limpo.iloc[:, 1] = data_col.dropna() # Atualiza a coluna de data limpa
        
        # Renomeia coluna de data para padronizar
        nome_data = df_limpo.columns[1]
        df_limpo.rename(columns={nome_data: 'Data'}, inplace=True)
        
        return df_limpo
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def plotar_secao(df_principal, col_inicio, col_fim, titulo_grafico, key_suffix):
    """
    Função auxiliar para recortar o dataframe e plotar o gráfico.
    col_inicio e col_fim são índices baseados em 0 (A=0, B=1, etc)
    """
    # Recorta: Coluna Data (índice 1) + Intervalo desejado
    # Nota: iloc no python é excludente no final, então somamos +1 no fim
    cols_indices = [1] + list(range(col_inicio, col_fim + 1))
    
    df_slice = df_principal.iloc[:, cols_indices].copy()
    
    # Limpeza de nomes de colunas (Pandas pode adicionar .1, .2 se houver nomes repetidos)
    df_slice.columns = [c.split('.')[0] for c in df_slice.columns]
    
    # Interface de Seleção
    opcoes = df_slice.columns.tolist()
    opcoes.remove('Data') # Remove a data da lista de seleção
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        st.markdown(f"**Filtros: {titulo_grafico}**")
        selecao = st.multiselect(
            "Selecione as Séries:",
            opcoes,
            default=opcoes,
            key=f"multi_{key_suffix}" # Chave única para não conflitar com outros gráficos
        )
    
    with col2:
        if selecao:
            fig = px.line(
                df_slice, 
                x='Data', 
                y=selecao, 
                title=titulo_grafico,
                markers=True
            )
            fig.update_xaxes(rangeslider_visible=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Selecione pelo menos uma série.")

# --- Execução Principal ---

with st.spinner('Processando todas as séries históricas...'):
    df_full = carregar_dados_completos()

if df_full is not None:
    # Criação das Abas
    tab1, tab2, tab3, tab4 = st.tabs([
        "Número-Índice", 
        "Variação Mensal (%)", 
        "Var. em 12 Meses (%)", 
        "Preço Médio (R$/m²)"
    ])

    # Mapeamento de Colunas (Excel A=0, B=1, C=2...)
    # C=2, G=6
    # H=7, L=11
    # M=12, Q=16
    # R=17, V=21

    with tab1:
        plotar_secao(df_full, 2, 6, "Número-Índice", "idx")
    
    with tab2:
        plotar_secao(df_full, 7, 11, "Variação Mensal (%)", "mes")
        
    with tab3:
        plotar_secao(df_full, 12, 16, "Variação Acumulada em 12 Meses (%)", "ano")
        
    with tab4:
        plotar_secao(df_full, 17, 21, "Preço Médio de Venda (R$/m²)", "prc")
