import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Glossário Química dos Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Função para carregar dados
@st.cache_data
def carregar_dados(arquivo):
    try:
        return pd.read_csv(arquivo, encoding='utf-8', quotechar='"', sep=';')  # sep ajustável
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
        st.header("📘 Glossário de Resíduos")
        
        # Filtros
        with st.sidebar:
            st.subheader("Filtros")

            categorias = df["Categoria"].unique() if "Categoria" in df.columns else []
            classes = df["Classe ABNT"].unique() if "Classe ABNT" in df.columns else []
            reciclaveis = df["Reciclável"].unique() if "Reciclável" in df.columns else []

            categorias_sel = st.multiselect("Categoria", options=categorias, default=categorias) if categorias.size > 0 else []
            classes_sel = st.multiselect("Classe ABNT", options=classes, default=classes) if classes.size > 0 else []
            reciclavel_sel = st.selectbox("Reciclável", ["Todos"] + list(reciclaveis)) if len(reciclaveis) > 0 else "Todos"
        
        # Aplicar filtros
        df_filtrado = df.copy()

        if categorias_sel:
            df_filtrado = df_filtrado[df_filtrado["Categoria"].isin(categorias_sel)]
        if classes_sel:
            df_filtrado = df_filtrado[df_filtrado["Classe ABNT"].isin(classes_sel)]
        if reciclavel_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel_sel]
        
        # Exibição
        st.dataframe(df_filtrado, use_container_width=True, height=500)

# Seção de Polímeros
elif menu == "Polímeros":
    df = carregar_dados("polimeros.csv")
    
    if not df.empty:
        st.header("🧪 Glossário de Polímeros")
        
        # Filtros
        with st.sidebar:
            st.subheader("Filtros")

            tipos = df["Tipo de Polimerização"].unique() if "Tipo de Polimerização" in df.columns else []
            reciclaveis = df["Reciclável"].unique() if "Reciclável" in df.columns else []

            tipos_sel = st.multiselect("Tipo de Polimerização", options=tipos, default=tipos) if tipos.size > 0 else []
            reciclavel_sel = st.selectbox("Reciclável", ["Todos"] + list(reciclaveis)) if len(reciclaveis) > 0 else "Todos"
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if tipos_sel:
            df_filtrado = df_filtrado[df_filtrado["Tipo de Polimerização"].isin(tipos_sel)]
        if reciclavel_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel_sel]
        
        # Exibição
        st.dataframe(df_filtrado, use_container_width=True, height=500)

# Rodapé
st.divider()
st.caption("Desenvolvido para a Prefeitura - Sistema de Gestão de Resíduos")
