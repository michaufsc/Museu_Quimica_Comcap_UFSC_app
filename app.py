import streamlit as st
import pandas as pd

# Carregar os dados
df = pd.read_csv("plasticos.csv")

st.set_page_config(page_title="Glossário da Química do Lixo", layout="wide")

st.title("🔬 Glossário Interativo – Química do Lixo")
st.markdown("""
Este glossário ajuda educadores a explorar os principais tipos de plásticos e resíduos, com foco em **química, reciclabilidade e aplicações**.
""")

# Filtros interativos
col1, col2 = st.columns(2)
with col1:
    categoria = st.selectbox("Filtrar por categoria", ["Todas"] + sorted(df["Categoria"].unique().tolist()))
with col2:
    reciclavel = st.selectbox("Reciclável?", ["Todos", "Sim", "Não", "Sim (limitado)"])

# Aplicar filtros
filtered_df = df.copy()
if categoria != "Todas":
    filtered_df = filtered_df[filtered_df["Categoria"] == categoria]
if reciclavel != "Todos":
    filtered_df = filtered_df[filtered_df["Reciclável"] == reciclavel]

# Mostrar tabela com clique para detalhes
st.subheader("📘 Lista de Materiais")
for i, row in filtered_df.iterrows():
    with st.expander(f"{row['Sigla']} – {row['Nome Completo']}"):
        st.markdown(f"""
        **Nome completo:** {row['Nome Completo']}  
        **Categoria:** {row['Categoria']}  
        **Reciclável:** {row['Reciclável']}  
        **Aplicações comuns:** {row['Aplicações Comuns']}
        """)

# Rodapé
st.markdown("---")
st.caption("Dados coletados e organizados com base em fontes confiáveis para fins educativos.")
