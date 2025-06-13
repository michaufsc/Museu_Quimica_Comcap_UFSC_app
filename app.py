import streamlit as st
import pandas as pd
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Resíduos - Prefeitura",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funções para carregar dados
@st.cache_data
def carregar_residuos():
    return pd.read_csv("residuos.csv", encoding='utf-8', quotechar='"')

@st.cache_data
def carregar_polimeros():
    return pd.read_csv("polimeros.csv", encoding='utf-8', quotechar='"')

# Cabeçalho com logo
col1, col2 = st.columns([1, 4])
with col1:
    st.image(Image.open("logo_prefeitura.png"), width=150)  # Substitua pelo seu logo
with col2:
    st.title("♻️ Sistema Integrado de Gestão de Resíduos")

# Menu de navegação
menu = st.sidebar.radio(
    "MENU PRINCIPAL",
    options=["🏠 Dashboard", "📚 Glossário de Resíduos", "🧪 Glossário de Polímeros", "🗺️ Mapa de Coleta"],
    index=0
)

# ========================
# DASHBOARD PRINCIPAL
# ========================
if menu == "🏠 Dashboard":
    st.header("📊 Painel de Controle Operacional")
    
    # Carrega dados
    df_residuos = carregar_residuos()
    df_polimeros = carregar_polimeros()
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Resíduos Catalogados", len(df_residuos))
    with col2:
        st.metric("Polímeros Registrados", len(df_polimeros))
    with col3:
        perigoso = len(df_residuos[df_residuos['Classe ABNT'] == 'I'])
        st.metric("Resíduos Perigosos", f"{perigoso} ({perigoso/len(df_residuos):.1%})")
    
    # Gráficos
    st.subheader("Distribuição por Categoria")
    tab1, tab2 = st.tabs(["Resíduos", "Polímeros"])
    
    with tab1:
        st.bar_chart(df_residuos['Categoria'].value_counts())
    with tab2:
        st.bar_chart(df_polimeros['Tipo de Polimerização'].value_counts())

# ========================
# GLOSSÁRIO DE RESÍDUOS
# ========================
elif menu == "📚 Glossário de Resíduos":
    df = carregar_residuos()
    
    st.header("📚 Glossário de Resíduos")
    st.markdown("Catálogo completo de resíduos sólidos com classificação química e ambiental")
    
    # Filtros avançados
    with st.expander("🔍 Filtros Avançados", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            categorias = st.multiselect(
                "Categoria",
                options=df["Categoria"].unique(),
                default=df["Categoria"].unique()
            )
        with col2:
            classes = st.multiselect(
                "Classe ABNT",
                options=df["Classe ABNT"].unique(),
                default=df["Classe ABNT"].unique()
            )
        with col3:
            reciclavel = st.selectbox(
                "Reciclabilidade",
                options=["Todos"] + list(df["Reciclável"].unique())
            )
    
    # Aplicar filtros
    df_filtrado = df[
        (df["Categoria"].isin(categorias)) & 
        (df["Classe ABNT"].isin(classes))
    ]
    if reciclavel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
    
    # Visualização dos dados
    st.subheader(f"📋 Resultados ({len(df_filtrado)} itens)")
    
    with st.expander("🔍 Busca por texto", expanded=False):
        busca = st.text_input("Digite termos para busca:")
        if busca:
            df_filtrado = df_filtrado[
                df_filtrado.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
            ]
    
    # Exibição em abas
    tab1, tab2 = st.tabs(["Visualização Tabular", "Detalhes"])
    
    with tab1:
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_order=["Categoria", "Sigla ou Nome", "Classe ABNT", "Reciclável", "Destinação"]
        )
    
    with tab2:
        if not df_filtrado.empty:
            selected = st.selectbox(
                "Selecione um resíduo para detalhes:",
                options=df_filtrado["Sigla ou Nome"]
            )
            
            dados = df_filtrado[df_filtrado["Sigla ou Nome"] == selected].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Categoria:** {dados['Categoria']}")
                st.markdown(f"**Nome/Sigla:** {dados['Sigla ou Nome']}")
                st.markdown(f"**Composição Química:** {dados['Composição Química']}")
                st.markdown(f"**Classe ABNT:** {dados['Classe ABNT']}")
            
            with col2:
                st.markdown(f"**Reciclável:** {dados['Reciclável']}")
                st.markdown(f"**Destinação:** {dados['Destinação']}")
                st.markdown(f"**Aplicações/Exemplos:**")
                st.info(dados["Aplicações ou Exemplos"])

# ========================
# GLOSSÁRIO DE POLÍMEROS
# ========================
elif menu == "🧪 Glossário de Polímeros":
    df = carregar_polimeros()
    
    st.header("🧪 Glossário de Polímeros")
    st.markdown("Catálogo técnico de polímeros e suas aplicações")
    
    # Filtros avançados
    with st.expander("🔍 Filtros Avançados", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            tipos = st.multiselect(
                "Tipo de Polimerização",
                options=df["Tipo de Polimerização"].unique(),
                default=df["Tipo de Polimerização"].unique()
            )
            origem = st.multiselect(
                "Origem",
                options=df["Aquisição"].unique(),
                default=df["Aquisição"].unique()
            )
        with col2:
            reciclavel = st.selectbox(
                "Reciclabilidade",
                options=["Todos"] + list(df["Reciclável"].unique())
            )
            cadeia = st.multiselect(
                "Tipo de Cadeia",
                options=df["Tipo de Cadeia"].unique(),
                default=df["Tipo de Cadeia"].unique()
            )
    
    # Aplicar filtros
    df_filtrado = df[
        (df["Tipo de Polimerização"].isin(tipos)) &
        (df["Aquisição"].isin(origem)) &
        (df["Tipo de Cadeia"].isin(cadeia))
    ]
    if reciclavel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Reciclável"] == reciclavel]
    
    # Visualização dos dados
    st.subheader(f"📋 Resultados ({len(df_filtrado)} polímeros)")
    
    with st.expander("🔍 Busca por texto", expanded=False):
        busca = st.text_input("Digite termos para busca:")
        if busca:
            df_filtrado = df_filtrado[
                df_filtrado.apply(lambda row: busca.lower() in str(row).lower(), axis=1)
            ]
    
    # Exibição em abas
    tab1, tab2 = st.tabs(["Visualização Tabular", "Detalhes Técnicos"])
    
    with tab1:
        st.dataframe(
            df_filtrado,
            use_container_width=True,
            height=500,
            hide_index=True,
            column_order=["Nome", "Sigla", "Tipo de Polimerização", "Reciclável", "Aplicações Comuns"]
        )
    
    with tab2:
        if not df_filtrado.empty:
            selected = st.selectbox(
                "Selecione um polímero para detalhes técnicos:",
                options=df_filtrado["Nome"]
            )
            
            dados = df_filtrado[df_filtrado["Nome"] == selected].iloc[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Nome:** {dados['Nome']}")
                st.markdown(f"**Sigla:** {dados['Sigla']}")
                st.markdown(f"**Tipo de Polimerização:** {dados['Tipo de Polimerização']}")
                st.markdown(f"**Monômero(s):** {dados['Monômero(s)']}")
            
            with col2:
                st.markdown(f"**Composição Química:** {dados['Composição Química']}")
                st.markdown(f"**Tipo de Cadeia:** {dados['Tipo de Cadeia']}")
                st.markdown(f"**Reciclável:** {dados['Reciclável']}")
            
            st.markdown("**Aplicações Comuns:**")
            st.info(dados["Aplicações Comuns"])

# ========================
# MAPA DE COLETA
# ========================
elif menu == "🗺️ Mapa de Coleta":
    st.header("🗺️ Mapa de Coleta de Resíduos")
    
    # Dados fictícios para exemplo (substitua pelos seus dados reais)
    dados_mapa = pd.DataFrame({
        "Bairro": ["Centro", "Vila Nova", "Jardim das Flores", "Zona Industrial"],
        "lat": [-23.5505, -23.5432, -23.5555, -23.5600],
        "lon": [-46.6333, -46.6400, -46.6350, -46.6450],
        "Resíduos (kg)": [150, 300, 50, 25],
        "Tipo": ["Orgânico", "Reciclável", "Eletrônico", "Hospitalar"]
    })
    
    # Filtros para o mapa
    tipo_residuo = st.multiselect(
        "Filtrar por tipo de resíduo:",
        options=dados_mapa["Tipo"].unique(),
        default=dados_mapa["Tipo"].unique()
    )
    
    dados_filtrados = dados_mapa[dados_mapa["Tipo"].isin(tipo_residuo)]
    
    # Exibir mapa
    st.map(
        dados_filtrados,
        size='Resíduos (kg)',
        color='#0068c9',
        zoom=12
    )
    
    # Tabela de apoio
    st.subheader("Dados de Coleta por Bairro")
    st.dataframe(
        dados_filtrados,
        column_config={
            "lat": "Latitude",
            "lon": "Longitude",
            "Resíduos (kg)": st.column_config.NumberColumn(format="%d kg")
        },
        hide_index=True,
        use_container_width=True
    )

# Rodapé
st.divider()
st.caption(f"© {pd.Timestamp.now().year} Secretaria Municipal de Meio Ambiente - Versão 1.0")
