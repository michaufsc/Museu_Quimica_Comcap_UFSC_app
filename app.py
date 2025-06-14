import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import base64
from io import BytesIO
import re

# Configuração da página
st.set_page_config(
    page_title="Glossário Científico de Resíduos",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .material-card {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        transition: 0.3s;
        background-color: #f8f9fa;
    }
    .material-card:hover {
        box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
    }
    .chem-formula {
        font-family: "Times New Roman", serif;
        font-style: italic;
        font-size: 1.1em;
    }
    .recycling-symbol {
        font-size: 1.5em;
        vertical-align: middle;
    }
    .stDataFrame {
        font-size: 0.95em;
    }
</style>
""", unsafe_allow_html=True)

# Funções auxiliares
def load_data(file_path):
    try:
        return pd.read_csv(file_path, sep=";", encoding='utf-8')
    except Exception as e:
        st.error(f"Erro ao carregar {file_path}: {str(e)}")
        return pd.DataFrame()

def clean_chemical_formula(formula):
    """Converte fórmulas químicas para formato HTML com subscritos"""
    if pd.isna(formula):
        return ""
    return re.sub(r'([0-9]+)', r'<sub>\1</sub>', str(formula))

def render_chemical_info(row):
    """Renderiza card informativo para cada material"""
    with st.container():
        st.markdown(f"""
        <div class="material-card">
            <h3>{row['Nome'] if 'Nome' in row else row['Categoria']} 
                <small>({row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']})</small>
            </h3>
            <p><strong>Tipo:</strong> {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}</p>
            <p><strong>Composição:</strong> <span class="chem-formula">{clean_chemical_formula(row.get('Composição Química', row.get('Composição Química', '-')))</span></p>
            <p><strong>Reciclabilidade:</strong> {row.get('Reciclável', row.get('Reciclável', '-'))} 
                {f"<span class='recycling-symbol'>{row['Símbolo Reciclagem']}</span>" if 'Símbolo Reciclagem' in row and pd.notna(row['Símbolo Reciclagem']) else ''}
            </p>
            <p><strong>Aplicações:</strong> {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}</p>
            <p><strong>Impacto Ambiental:</strong> {row.get('Impacto Ambiental', row.get('Perigo Potencial', '-'))}</p>
        </div>
        """, unsafe_allow_html=True)

def create_molecular_structure_image(formula):
    """Gera imagem representativa da estrutura molecular (simulada)"""
    # Esta é uma implementação simulada - na prática, você poderia integrar com RDKit ou outro gerador
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.text(0.5, 0.5, formula, fontsize=12, ha='center', va='center')
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def render_molecular_view(formula):
    """Exibe visualização molecular simulada"""
    if pd.isna(formula):
        return
    
    img_base64 = create_molecular_structure_image(formula)
    st.markdown(f"""
    <div style="text-align: center; margin: 10px 0;">
        <img src="data:image/png;base64,{img_base64}" width="150">
        <p style="font-size: 0.8em; margin-top: 5px;">Representação estrutural</p>
    </div>
    """, unsafe_allow_html=True)

def plot_decomposition_chart(df, column):
    """Gráfico de decomposição/reciclagem"""
    if column not in df.columns:
        return
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    if df[column].dtype == 'object':
        # Para dados categóricos
        sns.countplot(data=df, y=column, ax=ax, order=df[column].value_counts().index)
        ax.set_title(f"Distribuição por {column}")
    else:
        # Para dados numéricos
        sns.histplot(data=df, x=column, bins=10, ax=ax)
        ax.set_title(f"Distribuição de {column}")
    
    ax.set_xlabel("")
    ax.set_ylabel("")
    st.pyplot(fig)

def create_download_link(df, filename):
    """Gera link para download do DataFrame"""
    csv = df.to_csv(index=False, sep=";")
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Baixar dados filtrados</a>'

# Carregamento de dados
polimeros = load_data("polimeros.csv")
residuos = load_data("residuos.csv")

# Interface principal
def main():
    st.title("♻️ Glossário Científico de Polímeros e Resíduos")
    st.markdown("""
    **Ferramenta para educadores ambientais** · Dados técnicos para atividades de conscientização
    """)
    st.markdown("---")
    
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
    
    # Filtros
    st.sidebar.header("Filtros Avançados")
    
    # Filtros dinâmicos baseados nas colunas disponíveis
    filters = {}
    filter_cols = [col for col in df.columns if col not in ['Nome', 'Sigla', 'Composição Química', 'Símbolo Reciclagem']]
    
    for col in filter_cols:
        if df[col].nunique() < 20:  # Filtros para colunas com poucos valores únicos
            unique_vals = df[col].unique()
            selected = st.sidebar.multiselect(
                f"Filtrar por {col}",
                options=unique_vals,
                default=unique_vals
            )
            filters[col] = selected
    
    # Filtro de texto
    search_term = st.sidebar.text_input("Buscar por termo")
    
    # Aplicar filtros
    filtered_df = df.copy()
    for col, values in filters.items():
        if values:
            filtered_df = filtered_df[filtered_df[col].isin(values)]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(axis=1)
        ]
    
    # Visualização dos dados
    tab1, tab2, tab3 = st.tabs(["📋 Dados Detalhados", "🖼️ Visualização em Cards", "📊 Análises"])
    
    with tab1:
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=600,
            hide_index=True
        )
        
        # Link para download
        st.markdown(create_download_link(filtered_df, f"{dataset.lower()}_filtrado.csv"), unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Visualização Didática")
        
        cols = st.columns(2)
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 2]:
                render_chemical_info(row)
                
                if 'Composição Química' in row and pd.notna(row['Composição Química']):
                    with st.expander("Estrutura Molecular"):
                        render_molecular_view(row['Composição Química'])
    
    with tab3:
        st.subheader("Análises e Estatísticas")
        
        if dataset == "Polímeros":
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Distribuição por Tipo de Polimerização**")
                plot_decomposition_chart(filtered_df, 'Tipo de Polimerização')
            
            with col2:
                st.markdown("**Reciclabilidade dos Materiais**")
                plot_decomposition_chart(filtered_df, 'Reciclável')
            
            st.markdown("**Biodegradabilidade vs. Impacto Ambiental**")
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.countplot(
                data=filtered_df,
                x='Impacto Ambiental',
                hue='Biodegradável',
                ax=ax
            )
            ax.set_title("Relação entre Biodegradabilidade e Impacto Ambiental")
            st.pyplot(fig)
        
        else:  # Resíduos
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Distribuição por Categoria**")
                plot_decomposition_chart(filtered_df, 'Categoria')
            
            with col2:
                st.markdown("**Reciclabilidade dos Resíduos**")
                plot_decomposition_chart(filtered_df, 'Reciclável')
            
            st.markdown("**Classes ABNT vs. Perigo Potencial**")
            fig, ax = plt.subplots(figsize=(10, 4))
            sns.countplot(
                data=filtered_df,
                x='Classe ABNT',
                hue='Perigo Potencial',
                ax=ax
            )
            ax.set_title("Classificação de Risco dos Resíduos")
            st.pyplot(fig)
    
    # Seção educacional
    st.markdown("---")
    st.subheader("💡 Sugestões para Atividades Educativas")
    
    if dataset == "Polímeros":
        st.markdown("""
        - **Identificação de plásticos:** Use a coluna 'Símbolo Reciclagem' para ensinar a identificar tipos de plástico
        - **Experimentos de densidade:** Compare diferentes polímeros usando a coluna 'Tipo de Polimerização'
        - **Debate sobre impactos:** Use os dados de 'Impacto Ambiental' para discussões sobre consumo responsável
        """)
    else:
        st.markdown("""
        - **Classificação de resíduos:** Use os dados para criar exercícios de separação correta
        - **Linha do tempo da decomposição:** Ilustre quanto tempo cada material leva para se decompor
        - **Rota do lixo:** Trace o caminho de diferentes resíduos com base na coluna 'Destinação'
        """)
    
    st.markdown("---")
    st.caption("""
    Desenvolvido para educadores ambientais · Dados atualizados em 2023 · 
    [Repositório no GitHub](https://github.com) | [Contato](mailto:educacao@residuos.org)
    """)

if __name__ == "__main__":
    main()
