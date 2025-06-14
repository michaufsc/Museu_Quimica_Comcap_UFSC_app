import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import re

# Configuração da página (removi o CSS inline para evitar problemas)
st.set_page_config(
    page_title="Glossário Científico de Resíduos",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar dados sem cache (temporariamente)
def load_data(file_path):
    try:
        return pd.read_csv(file_path, sep=";", encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Carregamento de dados
polimeros = load_data("polimeros.csv")
residuos = load_data("residuos.csv")

# Funções auxiliares
def clean_chemical_formula(formula):
    """Converte fórmulas químicas para formato com subscritos"""
    if pd.isna(formula):
        return ""
    return re.sub(r'([0-9]+)', r'<sub>\1</sub>', str(formula))

def render_chemical_info(row):
    """Renderiza card informativo para cada material"""
    with st.container():
        st.markdown(f"""
        <div style="border-radius:10px;padding:15px;margin:10px 0;box-shadow:0 4px 8px rgba(0,0,0,0.1);background:#f8f9fa;">
            <h3>{row['Nome'] if 'Nome' in row else row['Categoria']} 
                <small>({row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']})</small>
            </h3>
            <p><strong>Tipo:</strong> {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}</p>
            <p><strong>Composição:</strong> {clean_chemical_formula(row.get('Composição Química', row.get('Composição Química', '-')))</p>
            <p><strong>Reciclabilidade:</strong> {row.get('Reciclável', row.get('Reciclável', '-'))}</p>
            <p><strong>Aplicações:</strong> {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}</p>
        </div>
        """, unsafe_allow_html=True)

# Interface principal
def main():
    st.title("♻️ Glossário Científico de Polímeros e Resíduos")
    
    # Seleção de dataset
    dataset = st.radio(
        "Selecione o conjunto de dados:",
        ["Polímeros", "Resíduos"],
        horizontal=True
    )
    
    df = polimeros if dataset == "Polímeros" else residuos
    
    if df.empty:
        st.warning("Dados não carregados corretamente. Verifique os arquivos CSV.")
        return
    
    # Filtro simples
    search_term = st.text_input("Buscar por termo")
    
    # Aplicar filtro
    if search_term:
        filtered_df = df[
            df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(axis=1)
        ]
    else:
        filtered_df = df
    
    # Visualização dos dados
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Cards informativos
    st.subheader("Visualização Didática")
    cols = st.columns(2)
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        with cols[idx % 2]:
            render_chemical_info(row)

if __name__ == "__main__":
    main()
