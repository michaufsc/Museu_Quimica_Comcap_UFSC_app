import streamlit as st
import pandas as pd
import re

# Configuração da página
st.set_page_config(
    page_title="Glossário Científico de Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Função para carregar dados
def load_data(file_path):
    try:
        return pd.read_csv(file_path, sep=";", encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Carregamento de dados
polimeros = load_data("polimeros.csv")
residuos = load_data("residuos.csv")

# Função para formatar fórmulas químicas
def clean_chemical_formula(formula):
    if pd.isna(formula):
        return ""
    return re.sub(r'([0-9]+)', r'<sub>\1</sub>', str(formula))

# Função para renderizar cards de materiais
def render_chemical_info(row):
    nome = row['Nome'] if 'Nome' in row else row['Categoria']
    sigla = row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']
    tipo = row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))
    composicao = clean_chemical_formula(row.get('Composição Química', row.get('Composição Química', '-')))
    reciclavel = row.get('Reciclável', row.get('Reciclável', '-'))
    aplicacoes = row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))

    card_html = f"""
    <div style="
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        background-color: #f8f9fa;
    ">
        <h3>{nome} <small>({sigla})</small></h3>
        <p><strong>Tipo:</strong> {tipo}</p>
        <p><strong>Composição:</strong> {composicao}</p>
        <p><strong>Reciclabilidade:</strong> {reciclavel}</p>
        <p><strong>Aplicações:</strong> {aplicacoes}</p>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

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
    
    # Filtro de busca (VERSÃO CORRIGIDA)
    search_term = st.text_input("Buscar por termo")
    
    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    # Visualização dos dados
    tab1, tab2 = st.tabs(["📋 Tabela de Dados", "🖼️ Visualização em Cards"])
    
    with tab1:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600,
            hide_index=True
        )
    
    with tab2:
        st.subheader("Materiais")
        cols = st.columns(2)
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 2]:
                render_chemical_info(row)

if __name__ == "__main__":
    main()
