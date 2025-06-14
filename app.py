import streamlit as st
import pandas as pd
from PIL import Image
import os

# Configuração da página
st.set_page_config(
    page_title="Glossário de Resíduos com Imagens",
    page_icon="♻️",
    layout="wide"
)

# Configuração de caminhos
IMAGES_DIR = "imagens_materiais"

# Função para carregar dados com cache
@st.cache_data
def load_data(file_path):
    try:
        return pd.read_csv(file_path, sep=";", encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

# Carregar dados
polimeros = load_data("polimeros.csv")
residuos = load_data("residuos.csv")

# Função para exibir material com imagem
def display_material(row):
    sigla = row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']
    image_path = os.path.join(IMAGES_DIR, f"{sigla.lower()}.jpg")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if os.path.exists(image_path):
            st.image(Image.open(image_path), 
                   caption=f"Imagem de {sigla}",
                   width=200)
        else:
            st.warning("Imagem não disponível")
    
    with col2:
        st.markdown(f"""
        ### {row['Nome'] if 'Nome' in row else row['Categoria']} ({sigla})
        
        **Tipo:** {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}  
        **Composição:** {row.get('Composição Química', '-')}  
        **Reciclável:** {row.get('Reciclável', '-')}  
        **Aplicações:** {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}  
        **Impacto Ambiental:** {row.get('Impacto Ambiental', row.get('Perigo Potencial', '-'))}
        """)

# Interface principal
def main():
    st.title("🔍 Glossário Interativo de Resíduos")
    
    # Seleção do dataset
    dataset = st.radio(
        "Selecione a base de dados:",
        ["Polímeros", "Resíduos"],
        horizontal=True
    )
    
    df = polimeros if dataset == "Polímeros" else residuos
    
    if df.empty:
        st.warning("Dados não carregados corretamente.")
        return
    
    # Sistema de busca
    search_term = st.text_input("Buscar por material, aplicação ou característica:")
    
    # Filtragem dos dados
    if search_term:
        mask = df.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False).any(),
            axis=1
        )
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    # Exibição dos resultados
    if filtered_df.empty:
        st.warning("Nenhum material encontrado com os critérios de busca.")
    else:
        st.subheader(f"Resultados ({len(filtered_df)} encontrados)")
        
        for _, row in filtered_df.iterrows():
            display_material(row)
            st.divider()

# Verificação e execução
if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        st.warning(f"Pasta '{IMAGES_DIR}' criada. Adicione suas imagens lá.")
    
    main()
