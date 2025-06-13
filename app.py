import streamlit as st

# ✅ Deve ser o primeiro comando Streamlit
st.set_page_config(
    page_title="Glossário de Polímeros",
    page_icon="🧪",
    layout="wide"
)

import pandas as pd

# ✅ Carregar os dados do CSV
@st.cache_data
def carregar_dados():
    return pd.read_csv("polimeros.csv")

df = carregar_dados()

# ✅ Título e introdução
st.title("🧪 Glossário Interativo – Polímeros e Reciclagem")
st.markdown("""
Este glossário interativo apresenta os principais **polímeros utilizados na sociedade**, 
com informações sobre **composição química, origem, tipo de polimerização, reciclabilidade e aplicações**.  
Ideal para educadores ambientais, estudantes e espaços de divulgação científica.
""")

# 🔍 Campo de busca
busca = st.text_input("🔍 Buscar por nome, sigla, monômero, aplicação:")

# 🔧 Filtros interativos
col1, col2, col3 = st.columns(3)

with col1:
    tipos_pol = st.multiselect("Tipo de Polimerização", df["Tipo de Polimerização"].unique(), default=df["Tipo de Polimerização"].unique())

with col2:
    origem = st.multiselect("Origem", df["Aquisição"].unique(), default=df["Aquisição"].unique())

with col3:
    reciclavel = st.selectbox("Reciclável", options=["Todos"] + list(df["Reciclável"].unique()), index=0)

# 📌 Aplicar filtros
df_filtrado = df[
    (df["Tipo de Polimerização"].isin(tipos_pol)) &
    (df["Aquisição"].isin(origem))
]

if reciclavel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]

if busca:
    df_filtrado = df_filtrado[df_filtrado.apply(
        lambda row: busca.lower() in str(row).lower(), axis=1
    )]

# 📋 Exibir tabela
if not df_filtrado.empty:
    st.subheader("📘 Resultados filtrados")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

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

        st.markdown(f"**Aplicações Comuns:**")
        st.info(dados["Aplicações Comuns"])
else:
    st.warning("Nenhum resultado encontrado com os filtros ou busca aplicada.")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido a partir de conteúdo do curso QMC5530 – UFSC | Apoio à Educação Ambiental")

