import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Glossário Química dos Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Função segura para carregar dados
@st.cache_data
def carregar_dados(arquivo):
    try:
        df = pd.read_csv(arquivo, encoding='utf-8', quotechar='"')
        
        # Verifica colunas essenciais para resíduos
        if arquivo == "residuos.csv":
            colunas_necessarias = {'Categoria', 'Sigla ou Nome', 'Classe ABNT', 'Reciclável'}
            if not colunas_necessarias.issubset(df.columns):
                st.error(f"Colunas faltantes no arquivo {arquivo}. Esperado: {colunas_necessarias}")
                return None
        
        # Verifica colunas essenciais para polímeros
        elif arquivo == "polimeros.csv":
            colunas_necessarias = {'Nome', 'Sigla', 'Tipo de Polimerização', 'Reciclável'}
            if not colunas_necessarias.issubset(df.columns):
                st.error(f"Colunas faltantes no arquivo {arquivo}. Esperado: {colunas_necessarias}")
                return None
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar {arquivo}: {str(e)}")
        return None

# Interface principal
st.title("♻️ Glossário Interativo")

# Menu de navegação
menu = st.sidebar.radio(
    "Selecione a base de dados:",
    ["Resíduos", "Polímeros"]
)

# Seção de Resíduos
if menu == "Resíduos":
    df = carregar_dados("residuos.csv")
    
    if df is not None:
        st.header("Glossário de Resíduos")
        
        # Verifica colunas antes de usar
        colunas_disponiveis = set(df.columns)
        
        # Filtros (com fallback para colunas disponíveis)
        with st.sidebar:
            st.subheader("Filtros")
            
            # Categoria (com verificação)
            if 'Categoria' in colunas_disponiveis:
                categorias = st.multiselect(
                    "Categoria",
                    options=df["Categoria"].unique(),
                    default=df["Categoria"].unique()
                )
            else:
                st.warning("Coluna 'Categoria' não encontrada")
                categorias = []
            
            # Classe ABNT (com verificação)
            if 'Classe ABNT' in colunas_disponiveis:
                classes = st.multiselect(
                    "Classe ABNT",
                    options=df["Classe ABNT"].unique(),
                    default=df["Classe ABNT"].unique()
                )
            else:
                st.warning("Coluna 'Classe ABNT' não encontrada")
                classes = []
            
            # Reciclável (com verificação)
            if 'Reciclável' in colunas_disponiveis:
                reciclavel = st.selectbox(
                    "Reciclável",
                    options=["Todos"] + list(df["Reciclável"].unique())
            else:
                st.warning("Coluna 'Reciclável' não encontrada")
                reciclavel = "Todos"
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if categorias and 'Categoria' in colunas_disponiveis:
            df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias)]
        
        if classes and 'Classe ABNT' in colunas_disponiveis:
            df_filtrado = df_filtrado[df_filtrado["Classe ABNT"].isin(classes)]
        
        if reciclavel != "Todos" and 'Reciclável' in colunas_disponiveis:
            df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
        
        # Exibição dos dados
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            height=500
        )

# Seção de Polímeros
elif menu == "Polímeros":
    df = carregar_dados("polimeros.csv")
    
    if df is not None:
        st.header("Glossário de Polímeros")
        
        # Verifica colunas antes de usar
        colunas_disponiveis = set(df.columns)
        
        # Filtros (com fallback para colunas disponíveis)
        with st.sidebar:
            st.subheader("Filtros")
            
            if 'Tipo de Polimerização' in colunas_disponiveis:
                tipos = st.multiselect(
                    "Tipo de Polimerização",
                    options=df["Tipo de Polimerização"].unique(),
                    default=df["Tipo de Polimerização"].unique()
                )
            else:
                st.warning("Coluna 'Tipo de Polimerização' não encontrada")
                tipos = []
            
            if 'Reciclável' in colunas_disponiveis:
                reciclavel = st.selectbox(
                    "Reciclável",
                    options=["Todos"] + list(df["Reciclável"].unique())
                )
            else:
                st.warning("Coluna 'Reciclável' não encontrada")
                reciclavel = "Todos"
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if tipos and 'Tipo de Polimerização' in colunas_disponiveis:
            df_filtrado = df_filtrado[df_filtrado["Tipo de Polimerização"].isin(tipos)]
        
        if reciclavel != "Todos" and 'Reciclável' in colunas_disponiveis:
            df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
        
        # Exibição dos dados
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            height=500
        )

# Mensagem se nenhum dado for carregado
if menu in ["Resíduos", "Polímeros"] and df is None:
    st.error("Não foi possível carregar os dados. Verifique os arquivos CSV.")
