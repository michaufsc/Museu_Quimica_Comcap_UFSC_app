import streamlit as st
import pandas as pd
import re
from PIL import Image
import os

# Configuração da página
st.set_page_config(
    page_title="Glossário Científico de Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Pasta com as imagens (crie uma pasta 'images' no mesmo diretório do script)
IMAGES_DIR = "images"

# Função para carregar imagens
def load_image(image_name):
    try:
        image_path = os.path.join(IMAGES_DIR, image_name)
        return Image.open(image_path)
    except:
        return None

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

# Dicionário de imagens padrão (substitua pelos seus arquivos)
DEFAULT_IMAGES = {
    "PET": "pet.jpg",
    "PEAD": "pead.jpg",
    "PVC": "pvc.jpg",
    "PLA": "pla.jpg",
    # Adicione mais mapeamentos conforme necessário
}

# Função para renderizar cards com imagens
def render_chemical_info(row):
    nome = row['Nome'] if 'Nome' in row else row['Categoria']
    sigla = row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']
    
    # Tenta carregar imagem específica ou padrão
    img = load_image(f"{sigla.lower()}.jpg") or load_image(DEFAULT_IMAGES.get(sigla, ""))
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if img:
            st.image(img, width=150, caption=f"Exemplo de {sigla}")
        else:
            st.warning("Imagem não disponível")
    
    with col2:
        st.markdown(f"""
        <div style="
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            background-color: #f8f9fa;
        ">
            <h3>{nome} <small>({sigla})</small></h3>
            <p><strong>Tipo:</strong> {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}</p>
            <p><strong>Composição:</strong> {row.get('Composição Química', '-')}</p>
            <p><strong>Reciclabilidade:</strong> {row.get('Reciclável', '-')}</p>
            <p><strong>Aplicações:</strong> {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}</p>
        </div>
        """, unsafe_allow_html=True)

# Interface principal
def main():
    st.title("♻️ Glossário Visual de Polímeros e Resíduos")
    
    # Seção de upload de imagens (opcional)
    with st.expander("📤 Adicionar novas imagens"):
        uploaded_file = st.file_uploader("Enviar imagem para o glossário", type=['jpg', 'png', 'jpeg'])
        if uploaded_file:
            save_path = os.path.join(IMAGES_DIR, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Imagem {uploaded_file.name} salva com sucesso!")
    
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
    
    # Filtro de busca
    search_term = st.text_input("🔍 Buscar por termo")
    
    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False)).any(axis=1)
        filtered_df = df[mask]
    else:
        filtered_df = df
    
    # Visualização dos dados
    st.subheader("📚 Materiais")
    
    for _, row in filtered_df.iterrows():
        render_chemical_info(row)
        st.markdown("---")

if __name__ == "__main__":
    # Cria a pasta de imagens se não existir
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    main()
