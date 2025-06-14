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
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {arquivo}: {str(e)}")
        return pd.DataFrame()

# Interface principal
st.title("♻️ Glossário Interativo - Química dos Resíduos e Polímeros")

# Menu de navegação
menu = st.sidebar.radio(
    "Selecione a base de dados:",
    ["Resíduos", "Polímeros"]
)

# Seção de Resíduos
if menu == "Resíduos":
    df = carregar_dados("residuos.csv")
    
    if not df.empty:
        st.header("Glossário de Resíduos")
        
        # Filtros
        with st.sidebar:
            st.subheader("Filtros")
            
            # Verifica e cria filtros apenas para colunas existentes
            if 'Categoria' in df.columns:
                categorias = st.multiselect(
                    "Categoria",
                    options=df["Categoria"].unique(),
                    default=df["Categoria"].unique()
                )
            else:
                st.warning("Coluna 'Categoria' não encontrada")
                categorias = []
            
            if 'Classe ABNT' in df.columns:
                classes = st.multiselect(
                    "Classe ABNT",
                    options=df["Classe ABNT"].unique(),
                    default=df["Classe ABNT"].unique()
                )
            else:
                st.warning("Coluna 'Classe ABNT' não encontrada")
                classes = []
            
            if 'Reciclável' in df.columns:
                reciclavel = st.selectbox(
                    "Reciclável",
                    options=["Todos"] + list(df["Reciclável"].unique())
            else:
                st.warning("Coluna 'Reciclável' não encontrada")
                reciclavel = "Todos"
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if categorias and 'Categoria' in df.columns:
            df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias)]
        
        if classes and 'Classe ABNT' in df.columns:
            df_filtrado = df_filtrado[df_filtrado["Classe ABNT"].isin(classes)]
        
        if reciclavel != "Todos" and 'Reciclável' in df.columns:
            df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
        
        # Exibição dos dados
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            height=500
        )
    else:
        st.error("Não foi possível carregar os dados de resíduos")

# Seção de Polímeros
elif menu == "Polímeros":
    df = carregar_dados("polimeros.csv")
    
    if not df.empty:
        st.header("Glossário de Polímeros")
        
        # Filtros
        with st.sidebar:
            st.subheader("Filtros")
            
            if 'Tipo de Polimerização' in df.columns:
                tipos = st.multiselect(
                    "Tipo de Polimerização",
                    options=df["Tipo de Polimerização"].unique(),
                    default=df["Tipo de Polimerização"].unique()
                )
            else:
                st.warning("Coluna 'Tipo de Polimerização' não encontrada")
                tipos = []
            
            if 'Reciclável' in df.columns:
                reciclavel = st.selectbox(
                    "Reciclável",
                    options=["Todos"] + list(df["Reciclável"].unique()
                )
            else:
                st.warning("Coluna 'Reciclável' não encontrada")
                reciclavel = "Todos"
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if tipos and 'Tipo de Polimerização' in df.columns:
            df_filtrado = df_filtrado[df_filtrado["Tipo de Polimerização"].isin(tipos)]
        
        if reciclavel != "Todos" and 'Reciclável' in df.columns:
            df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
        
        # Exibição dos dados
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            height=500
        )
    else:
        st.error("Não foi possível carregar os dados de polímeros")

# Rodapé
st.divider()
st.caption("Desenvolvido para a Prefeitura - Sistema de Gestão de Resíduos")
