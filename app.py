import streamlit as st
import pandas as pd
from typing import Optional

# Configuração da página
st.set_page_config(
    page_title="Glossário Química dos Resíduos",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes para nomes de arquivos
RESIDUOS_FILE = "residuos.csv"
POLIMEROS_FILE = "polimeros.csv"

# Tipos de dados
DataFrame = pd.DataFrame

@st.cache_data
def carregar_dados(arquivo: str) -> Optional[DataFrame]:
    """Carrega dados de um arquivo CSV com tratamento robusto de erros."""
    try:
        df = pd.read_csv(
            arquivo,
            encoding='utf-8',
            quotechar='"',
            sep=';',
            on_bad_lines='warn'
        )
        # Verifica se o DataFrame não está vazio
        if df.empty:
            st.warning(f"O arquivo {arquivo} está vazio.")
            return None
        return df
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado: {arquivo}")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar {arquivo}: {str(e)}")
        return None

def aplicar_filtros(df: DataFrame, busca: str, filtros: dict) -> DataFrame:
    """Aplica filtros ao DataFrame de forma dinâmica."""
    df_filtrado = df.copy()
    
    # Filtro de busca
    if busca:
        df_filtrado = df_filtrado[
            df_filtrado.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
        ]
    
    # Filtros específicos
    for coluna, valores in filtros.items():
        if valores and (valores != ["Todos"]):
            df_filtrado = df_filtrado[df_filtrado[coluna].isin(valores)]
    
    return df_filtrado

def exibir_dataframe(df: DataFrame, altura: int = 500) -> None:
    """Exibe o DataFrame com configurações otimizadas."""
    if df.empty:
        st.warning("Nenhum resultado encontrado com os filtros selecionados.")
        return
    
    st.dataframe(
        df,
        use_container_width=True,
        height=altura,
        hide_index=True,
        column_config={
            col: st.column_config.Column(
                help=f"Informações sobre {col.lower()}"
            ) for col in df.columns
        }
    )

def criar_sidebar_filtros(df: DataFrame, tipo: str) -> dict:
    """Cria os filtros na sidebar de acordo com o tipo de dados."""
    filtros = {}
    
    with st.sidebar:
        st.subheader("🔎 Filtros Avançados")
        
        if tipo == "Resíduos":
            if "Categoria" in df.columns:
                categorias = df["Categoria"].unique()
                filtros["Categoria"] = st.multiselect(
                    "Categoria",
                    options=categorias,
                    default=categorias,
                    help="Filtrar por categorias de resíduos"
                )
            
            if "Classe ABNT" in df.columns:
                classes = df["Classe ABNT"].unique()
                filtros["Classe ABNT"] = st.multiselect(
                    "Classe ABNT",
                    options=classes,
                    default=classes,
                    help="Filtrar por classificação ABNT"
                )
        
        elif tipo == "Polímeros":
            if "Tipo de Polimerização" in df.columns:
                tipos = df["Tipo de Polimerização"].unique()
                filtros["Tipo de Polimerização"] = st.multiselect(
                    "Tipo de Polimerização",
                    options=tipos,
                    default=tipos,
                    help="Filtrar por tipo de polimerização"
                )
        
        # Filtro comum a ambos
        if "Reciclável" in df.columns:
            reciclaveis = df["Reciclável"].unique()
            filtros["Reciclável"] = st.multiselect(
                "Reciclável",
                options=["Todos"] + list(reciclaveis),
                default=["Todos"],
                help="Filtrar por reciclabilidade"
            )
    
    return filtros

def pagina_residuos() -> None:
    """Renderiza a página de resíduos."""
    st.header("📘 Glossário de Resíduos")
    
    df = carregar_dados(RESIDUOS_FILE)
    if df is None:
        return
    
    # Campo de busca
    busca = st.text_input(
        "🔍 Buscar por termo (ex: plástico, hospitalar, alimentos):",
        key="busca_residuos",
        help="Busque por qualquer termo relacionado a resíduos"
    )
    
    # Filtros
    filtros = criar_sidebar_filtros(df, "Resíduos")
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros(df, busca, filtros)
    
    # Exibição
    exibir_dataframe(df_filtrado)
    
    # Estatísticas rápidas
    with st.expander("📊 Estatísticas Rápidas"):
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Itens", len(df))
        col2.metric("Itens Filtrados", len(df_filtrado))
        if "Reciclável" in df.columns:
            reciclaveis = df_filtrado[df_filtrado["Reciclável"] == "Sim"].shape[0]
            col3.metric("Recicláveis", f"{reciclaveis} ({reciclaveis/len(df_filtrado)*100:.1f}%)")

def pagina_polimeros() -> None:
    """Renderiza a página de polímeros."""
    st.header("🧪 Glossário de Polímeros")
    
    df = carregar_dados(POLIMEROS_FILE)
    if df is None:
        return
    
    # Campo de busca
    busca = st.text_input(
        "🔍 Buscar por termo (ex: PET, biodegradável, PLA):",
        key="busca_polimeros",
        help="Busque por qualquer termo relacionado a polímeros"
    )
    
    # Filtros
    filtros = criar_sidebar_filtros(df, "Polímeros")
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros(df, busca, filtros)
    
    # Exibição
    exibir_dataframe(df_filtrado)
    
    # Visualização adicional
    with st.expander("📈 Distribuição de Polímeros"):
        if "Tipo de Polimerização" in df.columns:
            st.bar_chart(df_filtrado["Tipo de Polimerização"].value_counts())

def main() -> None:
    """Função principal da aplicação."""
    st.title("♻️ Glossário Interativo - Química dos Resíduos e Polímeros")
    
    # Menu de navegação
    menu = st.sidebar.radio(
        "Selecione a base de dados:",
        ["Resíduos", "Polímeros"],
        index=0,
        help="Navegue entre as diferentes bases de dados"
    )
    
    # Páginas
    if menu == "Resíduos":
        pagina_residuos()
    elif menu == "Polímeros":
        pagina_polimeros()
    
    # Rodapé
    st.divider()
    st.caption("""
        Desenvolvido para a Prefeitura - Sistema de Gestão de Resíduos  
        📧 Contato: suporte@gestaoresiduos.com | 📞 (XX) XXXX-XXXX
    """)

if __name__ == "__main__":
    main()
