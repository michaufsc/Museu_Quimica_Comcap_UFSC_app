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

# Carregar dados polimeros e residuos (seus originais)
@st.cache_data
def load_data():
    polimeros = pd.read_csv("polimeros.csv", sep=";")
    residuos = pd.read_csv("residuos.csv", sep=";")
    return polimeros, residuos

polimeros, residuos = load_data()

# Nova função para carregar perguntas do quiz do CSV
@st.cache_data
def load_quiz():
    # CSV deve ter colunas: pergunta, opcao_1, opcao_2, opcao_3, opcao_4, resposta_correta
    df = pd.read_csv("quiz_perguntas.csv")
    questions = []
    for _, row in df.iterrows():
        opcoes = [row['opcao_1'], row['opcao_2'], row['opcao_3'], row['opcao_4']]
        correta = row['resposta_correta']
        # índice da resposta correta para controlar a validação
        idx_correta = opcoes.index(correta) if correta in opcoes else None

        questions.append({
            "pergunta": row['pergunta'],
            "opcoes": opcoes,
            "resposta": idx_correta,
            "explicacao": f"A resposta correta é **{correta}**."
        })
    random.shuffle(questions)
    return questions

# Função quiz que usa as perguntas do CSV
def mostrar_quiz():
    st.header("🧠 Quiz de Resíduos e Polímeros")

    if 'questions' not in st.session_state:
        st.session_state.questions = load_quiz()
        st.session_state.current_question = 0
        st.session_state.score = 0

    questions = st.session_state.questions
    q_num = st.session_state.current_question

    if q_num < len(questions):
        question = questions[q_num]

        st.progress((q_num + 1) / len(questions))
        st.subheader(f"Pergunta {q_num + 1} de {len(questions)}")
        st.markdown(f"**{question['pergunta']}**")

        selected = st.radio("Escolha uma alternativa:", question['opcoes'], key=f"q{q_num}")

        if st.button("Confirmar", key=f"b{q_num}"):
            if question['resposta'] is not None and selected == question['opcoes'][question['resposta']]:
                st.success(f"✅ Correto! {question['explicacao']}")
                st.session_state.score += 1
            else:
                st.error(f"❌ Errado. {question['explicacao']}")

            st.session_state.current_question += 1
            st.experimental_rerun()

    else:
        score = st.session_state.score
        total = len(questions)
        percentual = score / total

        st.balloons()
        st.success(f"🎯 Pontuação Final: {score}/{total}")

        if percentual == 1:
            st.info("🌟 Excelente! Você acertou tudo!")
        elif percentual >= 0.75:
            st.info("👏 Muito bom! Você tem um bom domínio do conteúdo.")
        elif percentual >= 0.5:
            st.warning("🔍 Razoável, mas vale revisar os materiais.")
        else:
            st.error("📚 Vamos estudar mais um pouco? Explore o glossário!")

        if st.button("Refazer Quiz"):
            st.session_state.questions = load_quiz()
            st.session_state.current_question = 0
            st.session_state.score = 0
            st.experimental_rerun()

# O resto do seu código fica igual...

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

