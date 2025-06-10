import streamlit as st
import pandas as pd
from io import StringIO

# Função para carregar os dados com tratamento de erros
@st.cache_data  # Cache para melhor desempenho
def carregar_dados():
    # Dados CSV como string (substitua pelo seu arquivo ou URL)
    dados_csv = """Categoria,Sigla ou Nome,Composição Química,Classe ABNT,Reciclável,Destinação,Aplicações ou Exemplos
Plástico,PEAD (Polietileno de Alta Densidade),Polímero de etileno,Classe II-B,Sim,Reciclagem mecânica,"Sacolas, frascos rígidos"
Plástico,PET (Polietileno Tereftalato),Poliéster,Classe II-B,Sim,"Reciclagem química ou mecânica","Garrafas, embalagens de alimentos"
Plástico,PVC (Policloreto de Vinila),Polímero vinílico com cloro,Classe II-B,Limitado,Reciclagem especializada,"Tubos, brinquedos"
Metal,Alumínio,Al,Classe II-B,Sim,"Fusão e reutilização","Latinhas, embalagens, esquadrias"
Metal,Ferro,Fe,Classe II-B,Sim,Reciclagem siderúrgica,"Arames, peças de máquinas"
Vidro,Comum (sílica + carbonato de sódio),"SiO₂ + Na₂CO₃",Classe II-B,Sim,"Reciclagem infinita","Garfos, garrafas, potes"
Papel,"Papelão e papel branco",Base celulósica,Classe II-B,Sim,Reciclagem mecânica,"Caixas, folhas, embalagens"
Orgânico,Resíduo de alimentos,Compostos orgânicos,Classe II-A,Não,Compostagem,"Restos de frutas, cascas, vegetais"
Orgânico,Resíduo de poda,"Celulose, lignina",Classe II-A,Não,Compostagem,"Podas, grama, folhas secas"
Hospitalar,"Agulhas, seringas, sangue","Metais pesados e orgânicos",Classe I,Não,"Incinerador licenciado","Resíduos de postos de saúde, hospitais"
Eletrônico,Baterias de Lítio,"Li, Classe I",Classe I,Não,"Reciclagem especial/Ponto de coleta","Smartphones, notebooks"
Eletrônico,Placas de circuito impresso,"Metais pesados + polímeros",Classe I,Não,"Recuperação especializada","Computadores, eletrodomésticos"
Perigoso,Óleo usado,"Compostos orgânicos polares",Classe I,Não,"Coleta e regeneração ou coprocessamento","Óleo de motor, óleo de fritura"
Perigoso,Solventes industriais,"Compostos orgânicos voláteis",Classe I,Não,"Coprocessamento em fornos","Thinner, acetona"
"""
    
    try:
        # Para arquivo local (descomente se for usar arquivo)
        # df = pd.read_csv("residuos.csv", encoding='utf-8', quotechar='"', engine='python')
        
        # Para GitHub (descomente e substitua a URL)
        # url = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/residuos.csv"
        # df = pd.read_csv(url, encoding='utf-8', quotechar='"', engine='python')
        
        # Usando os dados diretamente (para teste)
        df = pd.read_csv(StringIO(dados_csv), encoding='utf-8', quotechar='"', engine='python')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# Carrega os dados
df = carregar_dados()

# Configuração da página
st.set_page_config(
    page_title="Glossário da Química dos Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Cabeçalho
st.title("♻️ Glossário Interativo - Química dos Resíduos")
st.markdown("""
Este glossário interativo visa apoiar **educadores ambientais** no ensino sobre **resíduos sólidos**, 
suas **características químicas**, **classificação segundo a ABNT**, e formas adequadas de destinação e reaproveitamento.
""")

# Filtros na barra lateral
st.sidebar.header("Filtros")
categorias_selecionadas = st.sidebar.multiselect(
    "Selecione as categorias:",
    options=df['Categoria'].unique(),
    default=df['Categoria'].unique()
)

classes_selecionadas = st.sidebar.multiselect(
    "Selecione as classes ABNT:",
    options=df['Classe ABNT'].unique(),
    default=df['Classe ABNT'].unique()
)

opcoes_reciclavel = ['Todos'] + list(df['Reciclável'].unique())
reciclavel_selecionado = st.sidebar.selectbox(
    "Reciclável:",
    options=opcoes_reciclavel,
    index=0
)

# Filtra os dados
dados_filtrados = df[
    (df['Categoria'].isin(categorias_selecionadas)) &
    (df['Classe ABNT'].isin(classes_selecionadas))
]

if reciclavel_selecionado != 'Todos':
    dados_filtrados = dados_filtrados[dados_filtrados['Reciclável'] == reciclavel_selecionado]

# Conteúdo principal
if not dados_filtrados.empty:
    # Exibe os dados filtrados
    st.subheader("Dados Filtrados")
    st.dataframe(
        dados_filtrados,
        use_container_width=True,
        height=600,
        hide_index=True,
        column_config={
            "Composição Química": st.column_config.TextColumn(width="large"),
            "Aplicações ou Exemplos": st.column_config.TextColumn(width="large")
        }
    )
    
    # Visualização detalhada
    with st.expander("🔍 Visualização Detalhada por Item"):
        material_selecionado = st.selectbox(
            "Selecione um material para detalhes:",
            options=dados_filtrados['Sigla ou Nome'].unique()
        )
        
        dados_material = dados_filtrados[dados_filtrados['Sigla ou Nome'] == material_selecionado].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Categoria:** {dados_material['Categoria']}")
            st.markdown(f"**Nome/Sigla:** {dados_material['Sigla ou Nome']}")
            st.markdown(f"**Composição Química:** {dados_material['Composição Química']}")
        
        with col2:
            st.markdown(f"**Classe ABNT:** {dados_material['Classe ABNT']}")
            st.markdown(f"**Reciclável:** {dados_material['Reciclável']}")
            st.markdown(f"**Destinação:** {dados_material['Destinação']}")
        
        st.markdown("**Aplicações/Exemplos:**")
        st.info(dados_material['Aplicações ou Exemplos'])
else:
    st.warning("Nenhum resultado encontrado com os filtros selecionados.")

# Informações adicionais
st.divider()
with st.expander("📚 Sobre a Classificação ABNT NBR 10.004"):
    st.markdown("""
    - **Classe I - Perigosos**: Apresentam riscos à saúde pública ou ao meio ambiente (inflamáveis, tóxicos, corrosivos).
    - **Classe II A - Não inertes**: Resíduos que podem sofrer decomposição (orgânicos, biodegradáveis).
    - **Classe II B - Inertes**: Resíduos que não se degradam facilmente (vidro, alguns plásticos e metais).
    """)

# Rodapé
st.caption("Desenvolvido para educação ambiental - Dados conforme ABNT NBR 10.004")
