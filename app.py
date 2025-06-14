import streamlit as st
import pandas as pd
import random
from PIL import Image
import os

# Configuração dos símbolos de reciclagem
RECYCLING_SYMBOLS = {
    "PET": "♷",
    "PEAD": "♴",
    "PVC": "♵",
    "PEBD": "♶",
    "PP": "♸",
    "PS": "♹",
    "OUTROS": "♻"
}

# Função para exibir símbolos com estilo
def display_symbol(symbol):
    return f"""
    <div style="
        font-size: 2em;
        text-align: center;
        margin: 10px;
        padding: 15px;
        background-color: #e0f7fa;
        border-radius: 10px;
        display: inline-block;
        width: 60px;
    ">
        {symbol}
    </div>
    """

# Gerar perguntas do quiz com símbolos melhorados
def generate_quiz_questions():
    questions = []
    
    # Perguntas sobre símbolos de reciclagem
    for _, row in polimeros.iterrows():
        symbol = row.get('Símbolo Reciclagem', RECYCLING_SYMBOLS.get(row['Sigla'], '♻'))
        wrong_symbols = random.sample(
            [s for s in RECYCLING_SYMBOLS.values() if s != symbol],
            3
        )
        
        questions.append({
            "pergunta": f"Qual é o símbolo de reciclagem do {row['Nome']} ({row['Sigla']})?",
            "opcoes": [symbol] + wrong_symbols,
            "resposta": 0,
            "explicacao": f"O símbolo correto é {symbol} - {row['Nome']}",
            "tipo": "symbol"
        })
    
    # Outras perguntas (mantenha suas perguntas existentes)
    # ...
    
    return random.sample(questions, min(20, len(questions)))

# Função do Quiz com símbolos melhorados
def mostrar_quiz():
    st.header("🧠 Quiz de Identificação de Resíduos")
    
    if 'questions' not in st.session_state:
        st.session_state.questions = generate_quiz_questions()
        st.session_state.current_question = 0
        st.session_state.score = 0
    
    if st.session_state.current_question < len(st.session_state.questions):
        question = st.session_state.questions[st.session_state.current_question]
        
        st.subheader(f"Pergunta {st.session_state.current_question + 1}/{len(st.session_state.questions)}")
        st.markdown(f"**{question['pergunta']}**", unsafe_allow_html=True)
        
        # Exibição especial para perguntas com símbolos
        if question.get('tipo') == 'symbol':
            cols = st.columns(4)
            for i, option in enumerate(question['opcoes']):
                with cols[i]:
                    st.markdown(display_symbol(option), unsafe_allow_html=True)
                    if st.button(f"Selecionar", key=f"opt_{i}"):
                        check_answer(question, i)
        else:
            selected = st.radio("Selecione:", question['opcoes'], key=f"q{st.session_state.current_question}")
            if st.button("Confirmar"):
                check_answer(question, question['opcoes'].index(selected))
    else:
        show_results()

def check_answer(question, selected_index):
    if selected_index == question['resposta']:
        st.success(f"✅ Correto! {question['explicacao']}")
        st.session_state.score += 1
    else:
        st.error(f"❌ Incorreto. {question['explicacao']}")
    
    st.session_state.current_question += 1
    st.experimental_rerun()

def show_results():
    st.balloons()
    st.success(f"""
    🎯 Quiz Concluído!
    Pontuação: {st.session_state.score}/{len(st.session_state.questions)}
    """)
    
    if st.button("🔄 Refazer Quiz"):
        reset_quiz()

def reset_quiz():
    st.session_state.questions = generate_quiz_questions()
    st.session_state.current_question = 0
    st.session_state.score = 0
    st.experimental_rerun()

# [Restante do seu código permanece igual...]
