import streamlit as st
import pandas as pd
from PIL import Image
import os

# Configuração da página
st.set_page_config(
    page_title="Glossário com Imagens Específicas",
    page_icon="♻️",
    layout="wide"
)

# Pasta onde as imagens estão armazenadas
IMAGES_DIR = "imagens_materiais"

# Dicionário de mapeamento de material para imagem (atualize com seus arquivos)
MATERIAL_IMAGES = {
    "PET": "pet.jpg",
    "PEAD": "pead.jpg",
    "PVC": "pvc.jpg",
    "PLA": "pla.jpg",
    # Adicione todos os mapeamentos necessários
}

# Função para carregar dados
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

# Função para mostrar material com imagem
def show_material(row):
    # Obter a sigla do material
    sigla = row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']
    
    # Verificar se existe imagem para este material
    image_path = os.path.join(IMAGES_DIR, MATERIAL_IMAGES.get(sigla, ""))
    
    if os.path.exists(image_path):
        img = Image.open(image_path)
        st.image(img, caption=sigla, width=200)
    else:
        st.warning(f"Imagem não encontrada para {sigla}")
    
    st.markdown(f"""
    **Nome:** {row['Nome'] if 'Nome' in row else row['Categoria']}  
    **Tipo:** {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}  
    **Reciclável:** {row.get('Reciclável', '-')}  
    **Aplicações:** {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}
    """)

# Interface principal
def main():
    st.title("♻️ Glossário de Materiais com Imagens")
    
    # Seleção de dataset
    dataset = st.selectbox("Selecione o tipo de material:", ["Polímeros", "Resíduos"])
    
    df = polimeros if dataset == "Polímeros" else residuos
    
    if df.empty:
        st.warning("Dados não carregados corretamente.")
        return
    
    # Filtro por material
    selected_material = st.selectbox(
        "Selecione o material:",
        options=df['Sigla'].unique() if 'Sigla' in df.columns else df['Sigla ou Nome'].unique()
    )
    
    # Obter dados do material selecionado
    material_data = df[df['Sigla'] == selected_material] if 'Sigla' in df.columns else df[df['Sigla ou Nome'] == selected_material]
    
    if not material_data.empty:
        show_material(material_data.iloc[0])
    else:
        st.error("Material não encontrado")

if __name__ == "__main__":
    # Verificar se a pasta de imagens existe
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        st.warning(f"Pasta '{IMAGES_DIR}' criada. Adicione suas imagens lá.")
    
    main()
