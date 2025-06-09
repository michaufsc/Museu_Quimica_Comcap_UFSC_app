import streamlit as st
import pandas as pd

# Carrega o CSV
df = pd.read_csv("residuos.csv")

st.set_page_config(page_title="Glossário da Química dos Resíduos", layout="wide")
st.title("♻️ Glossário Interativo – Química dos Resíduos")
st.markdown("""
Este glossário interativo visa apoiar **educadores ambientais** no ensino sobre **resíduos sólidos**, suas **características químicas**, **classificação segundo a ABNT**, e formas adequadas de destinação e reaproveitamento.

Use os filtros abaixo para explorar os resíduos por tipo, reciclabilidade ou classe ambiental.
""")

# Filtros
col1, col2, col3 = st.columns(3)

categorias = df["Categoria"].unique()
classes = df["Classe ABNT"].unique()
reciclavel = df["Reciclável"].unique()

with col1:
    categoria_sel = st.multiselect("Categoria", categorias, default=categorias)

with col2:
    classe_sel = st.multiselect("Classe ABNT", classes, default=classes)

with col3:
    reciclavel_sel = st.multiselect("Reciclável", reciclavel, default=reciclavel)

# Filtra os dados
df_filtrado = df[
    (df["Categoria"].isin(categoria_sel)) &
    (df["Classe ABNT"].isin(classe_sel)) &
    (df["Reciclável"].isin(reciclavel_sel))
]

# Mostra os dados
st.dataframe(df_filtrado, use_container_width=True)

# Expansor com detalhes
with st.expander("📘 Saiba mais sobre a Classificação da ABNT NBR 10.004"):
    st.markdown("""
- **Classe I – Perigosos**: inflamáveis, tóxicos, corrosivos, reativos.
- **Classe II A – Não inertes**: resíduos orgânicos e biodegradáveis (restos de alimento, folhas etc.).
- **Classe II B – Inertes**: resíduos que não sofrem transformações físicas, químicas ou biológicas (vidro, certos plásticos, metais).

👉 Esses conceitos são importantes para a **gestão ambiental, separação correta e educação nas escolas.**
""")
