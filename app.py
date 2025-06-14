import streamlit as st
import pandas as pd

@st.cache_data
def load_quiz():
    df = pd.read_csv("quiz_perguntas.csv", sep=';')
    questions = []
    for _, row in df.iterrows():
        questions.append({
            "pergunta": row["pergunta"],
            "opcoes": [row["opcao_1"], row["opcao_2"], row["opcao_3"], row["opcao_4"]],
            "resposta": int(row["resposta"]),
            "explicacao": row.get("explicacao", "")
        })
    return questions

def main():
    st.title("🧠 Quiz de Resíduos e Polímeros")

    if "current_question" not in st.session_state:
        st.session_state.current_question = 0
        st.session_state.answered = False
        st.session_state.is_correct = False

    questions = load_quiz()
    q = questions[st.session_state.current_question]

    st.write(f"Pergunta {st.session_state.current_question + 1} de {len(questions)}")
    st.write(q["pergunta"])

    if not st.session_state.answered:
        resposta_usuario = st.radio("Escolha uma alternativa:", q["opcoes"], key="radio")
        if st.button("Responder"):
            index_resposta = q["opcoes"].index(resposta_usuario)
            st.session_state.is_correct = (index_resposta == q["resposta"])
            st.session_state.answered = True
            st.experimental_rerun()
    else:
        if st.session_state.is_correct:
            st.success(f"✅ Correto! {q['explicacao']}")
        else:
            st.error(f"❌ Errado. {q['explicacao']}")

        if st.session_state.current_question + 1 < len(questions):
            if st.button("Próxima pergunta"):
                st.session_state.current_question += 1
                st.session_state.answered = False
                st.session_state.is_correct = False
                st.experimental_rerun()
        else:
            st.info("🎉 Você terminou o quiz!")

if __name__ == "__main__":
    main()
