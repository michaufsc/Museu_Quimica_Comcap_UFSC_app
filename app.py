import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Glossário Química dos Resíduos",
    page_icon="♻️",
    layout="wide"
)

st.title("♻️ Glossário Interativo – Química dos Resíduos e Polímeros")

# Menu lateral de navegação
menu = st.sidebar.radio("📚 Escolha uma seção:", ["Glossário de Resíduos", "Glossário de Polímeros"])

# Função para carregar dados de resíduos
@st.cache_data
def carregar_residuos():
    return pd.read_csv("residuos.csv")

# Função para carregar dados de polímeros
@st.cache_data
def carregar_polimeros():
    return pd.read_csv("polimeros.csv")

# ========================
# SEÇÃO 1: GLOSSÁRIO DE RESÍDUOS
# ========================
if menu == "Glossário de Resíduos":
    df = carregar_residuos()

    busca = st.text_input("🔍 Buscar resíduo:")

    categorias = st.sidebar.multiselect("Categoria", df["Categoria"].unique(), default=df["Categoria"].unique())
    classes = st.sidebar.multiselect("Classe ABNT", df["Classe ABNT"].unique(), default=df["Classe ABNT"].unique())
    reciclavel = st.sidebar.selectbox("Reciclável", ["Todos"] + list(df["Reciclável"].unique()))

    df_filtrado = df[(df["Categoria"].isin(categorias)) & (df["Classe ABNT"].isin(classes))]
    if reciclavel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
    if busca:
        df_filtrado = df_filtrado[df_filtrado.apply(lambda row: busca.lower() in str(row).lower(), axis=1)]

    st.subheader("📘 Resultados filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

# ========================
# SEÇÃO 2: GLOSSÁRIO DE POLÍMEROS
# ========================
elif menu == "Glossário de Polímeros":
    df = carregar_polimeros()

    busca = st.text_input("🔍 Buscar polímero ou aplicação:")

    tipos = st.sidebar.multiselect("Tipo de Polimerização", df["Tipo de Polimerização"].unique(), default=df["Tipo de Polimerização"].unique())
    origem = st.sidebar.multiselect("Origem", df["Aquisição"].unique(), default=df["Aquisição"].unique())
    reciclavel = st.sidebar.selectbox("Reciclável", ["Todos"] + list(df["Reciclável"].unique()))

    df_filtrado = df[(df["Tipo de Polimerização"].isin(tipos)) & (df["Aquisição"].isin(origem))]
    if reciclavel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
    if busca:
        df_filtrado = df_filtrado[df_filtrado.apply(lambda row: busca.lower() in str(row).lower(), axis=1)]

    st.subheader("📘 Polímeros filtrados")
    st.dataframe(df_filtrado, use_container_width=True)

    with st.expander("🔍 Visualização detalhada por polímero"):
        item = st.selectbox("Selecione um polímero:", df_filtrado["Nome"])
        dados = df_filtrado[df_filtrado["Nome"] == item].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Sigla:** {dados['Sigla']}")
            st.markdown(f"**Tipo de Polimerização:** {dados['Tipo de Polimerização']}")
            st.markdown(f"**Tipo de Cadeia:** {dados['Tipo de Cadeia']}")
            st.markdown(f"**Monômero(s):** {dados['Monômero(s)']}")

        with col2:
            st.markdown(f"**Composição Química:** {dados['Composição Química']}")
            st.markdown(f"**Origem:** {dados['Aquisição']}")
            st.markdown(f"**Reciclável:** {dados['Reciclável']}")

        st.markdown("**Aplicações Comuns:**")
        st.info(dados["Aplicações Comuns"])
