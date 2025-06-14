import streamlit as st
import pandas as pd
import random
import os
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Sistema Completo de Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Carregar dados
@st.cache_data
def load_data():
    polimeros = pd.read_csv("polimeros.csv", sep=";")
    residuos = pd.read_csv("residuos.csv", sep=";")
    return polimeros, residuos

polimeros, residuos = load_data()

# Configuração de imagens
IMAGES_DIR = "imagens_materiais"

# Função para mostrar o glossário com imagens
def mostrar_glossario():
    st.header("📖 Glossário Interativo")
    
    dataset = st.radio(
        "Selecione a base de dados:",
        ["Polímeros", "Resíduos"],
        horizontal=True
    )
    
    df = polimeros if dataset == "Polímeros" else residuos
    
    # Barra de busca
    search_term = st.text_input("🔍 Buscar por termo, sigla ou aplicação:")
    
    # Filtragem
    if search_term:
        mask = df.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False).any(),
            axis=1
        )
        df = df[mask]
    
    # Exibição dos itens
    for _, row in df.iterrows():
        sigla = row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']
        image_path = os.path.join(IMAGES_DIR, f"{sigla.lower()}.jpg")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if os.path.exists(image_path):
                st.image(Image.open(image_path), width=200)
            else:
                st.warning("Imagem não disponível")
        
        with col2:
            st.markdown(f"""
            **Nome:** {row['Nome'] if 'Nome' in row else row['Categoria']}  
            **Sigla:** {sigla}  
            **Tipo:** {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}  
            **Composição:** {row.get('Composição Química', '-')}  
            **Reciclável:** {row.get('Reciclável', '-')}  
            **Aplicações:** {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}
            """)
        
        st.divider()

# Atividades Pedagógicas
def mostrar_atividades():
    st.header("📚 Atividades Pedagógicas")
    
    tab1, tab2, tab3 = st.tabs(["Fundamental", "Médio", "Superior"])
    
    with tab1:
        st.markdown("""
        ### 1. Identificação de Polímeros
        **Objetivo:** Reconhecer tipos de plásticos pelos símbolos
        **Materiais:** Amostras de embalagens com códigos de reciclagem
        """)
        
    with tab2:
        st.markdown("""
        ### 1. Análise de Propriedades
        **Objetivo:** Testar densidade e resistência de materiais
        **Materiais:** Amostras de diferentes polímeros
        """)
        
    with tab3:
        st.markdown("""
        ### 1. Análise de Ciclo de Vida
        **Objetivo:** Comparar impactos ambientais de materiais
        **Materiais:** Dados de produção e decomposição
        """)

# Gerar perguntas do quiz
def generate_quiz_questions():
    questions = []
    # Perguntas sobre polímeros (10 perguntas)
    samples_polimeros = polimeros.sample(min(10, len(polimeros)))
    for _, row in samples_polimeros.iterrows():
        questions.append({
            "pergunta": f"Qual o símbolo de reciclagem do {row['Nome']}?",
            "opcoes": [row['Símbolo Reciclagem'], "♻", "♳", "♺"],
            "resposta": 0,
            "explicacao": f"Símbolo correto: {row['Símbolo Reciclagem']}"
        })
    
    # Perguntas sobre resíduos (10 perguntas)
    samples_residuos = residuos.sample(min(10, len(residuos)))
    for _, row in samples_residuos.iterrows():
        questions.append({
            "pergunta": f"Como classificar {row['Categoria']} ({row['Sigla ou Nome']})?",
            "opcoes": [
                row['Classe ABNT'],
                random.choice(residuos['Classe ABNT'].unique()),
                random.choice(residuos['Classe ABNT'].unique()),
                "Não classificável"
            ],
            "resposta": 0,
            "explicacao": f"Classificação ABNT: {row['Classe ABNT']}"
        })
    
    random.shuffle(questions)
    return questions[:20]

# Quiz Interativo
def mostrar_quiz():
    st.header("🧠 Quiz de Resíduos e Polímeros")
    
    if 'questions' not in st.session_state:
        st.session_state.questions = generate_quiz_questions()
        st.session_state.current_question = 0
        st.session_state.score = 0
    
    if st.session_state.current_question < len(st.session_state.questions):
        question = st.session_state.questions[st.session_state.current_question]
        
        st.subheader(f"Pergunta {st.session_state.current_question + 1}/{len(st.session_state.questions)}")
        st.markdown(f"**{question['pergunta']}**")
        
        selected = st.radio("Selecione:", question['opcoes'], key=f"q{st.session_state.current_question}")
        
        if st.button("Confirmar"):
            if selected == question['opcoes'][question['resposta']]:
                st.success(f"✅ Correto! {question['explicacao']}")
                st.session_state.score += 1
            else:
                st.error(f"❌ Errado. {question['explicacao']}")
            
            st.session_state.current_question += 1
            st.experimental_rerun()
    else:
        st.balloons()
        st.success(f"🎯 Pontuação Final: {st.session_state.score}/{len(st.session_state.questions)}")
        
        if st.button("Refazer Quiz"):
            st.session_state.questions = generate_quiz_questions()
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.experimental_rerun()

# Interface principal
def main():
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏷️ Glossário", 
        "🧠 Quiz", 
        "📚 Atividades",
        "ℹ️ Sobre"
    ])
    
    with tab1:
        mostrar_glossario()
    
    with tab2:
        mostrar_quiz()
    
    with tab3:
        mostrar_atividades()
    
    with tab4:
        st.header("Sobre o Projeto")
        st.markdown("""
        **Glossário Interativo de Resíduos e Polímeros**
        - Desenvolvido para educação ambiental
        - Dados técnicos baseados em normas ABNT
        - Integrado com atividades pedagógicas
        """)

if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    main()
