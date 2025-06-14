import streamlit as st
import pandas as pd
import random
import os
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Glossário de Resíduos com Quiz",
    page_icon="♻️",
    layout="wide"
)

# Dados dos símbolos de reciclagem
RECYCLING_SYMBOLS = {
    "PET": "♷",
    "PEAD": "♴",
    "PVC": "♵",
    "PEBD": "♶",
    "PP": "♸",
    "PS": "♹",
    "OUTROS": "♻"
}

# Função para carregar dados
@st.cache_data
def load_data():
    try:
        polimeros = pd.read_csv("polimeros.csv", sep=";")
        residuos = pd.read_csv("residuos.csv", sep=";")
        return polimeros, residuos
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

polimeros, residuos = load_data()

# Função para exibir símbolos
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

# Gerar perguntas do quiz
def generate_quiz_questions():
    questions = []
    
    # Perguntas sobre polímeros
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
    
    # Perguntas sobre resíduos
    for _, row in residuos.iterrows():
        questions.append({
            "pergunta": f"Como classificar {row['Categoria']} ({row['Sigla ou Nome']}) segundo a ABNT?",
            "opcoes": [
                row['Classe ABNT'],
                random.choice(residuos['Classe ABNT'].unique()),
                random.choice(residuos['Classe ABNT'].unique()),
                "Não classificável"
            ],
            "resposta": 0,
            "explicacao": f"Classificação correta: {row['Classe ABNT']}",
            "tipo": "text"
        })
    
    random.shuffle(questions)
    return questions[:10]  # Limita a 10 perguntas para demonstração

# Função do Quiz
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
        
        if question['tipo'] == 'symbol':
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

# Função do Glossário
def mostrar_glossario():
    st.header("📖 Glossário de Resíduos e Polímeros")
    
    dataset = st.radio(
        "Selecione a base de dados:",
        ["Polímeros", "Resíduos"],
        horizontal=True
    )
    
    df = polimeros if dataset == "Polímeros" else residuos
    
    search_term = st.text_input("🔍 Buscar por termo:")
    
    if search_term:
        mask = df.apply(
            lambda row: row.astype(str).str.contains(search_term, case=False).any(),
            axis=1
        )
        df = df[mask]
    
    for _, row in df.iterrows():
        st.subheader(row['Nome'] if 'Nome' in row else row['Categoria'])
        st.markdown(f"""
        **Sigla:** {row['Sigla'] if 'Sigla' in row else row['Sigla ou Nome']}  
        **Tipo:** {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}  
        **Reciclável:** {row.get('Reciclável', '-')}  
        **Aplicações:** {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}
        """)
        st.divider()

# Interface principal
def main():
    tab1, tab2 = st.tabs(["📖 Glossário", "🧠 Quiz"])
    
    with tab1:
        mostrar_glossario()
    
    with tab2:
        mostrar_quiz()

if __name__ == "__main__":
    # Verificar se os arquivos existem
    if not os.path.exists("polimeros.csv") or not os.path.exists("residuos.csv"):
        st.error("Arquivos CSV não encontrados. Certifique-se que 'polimeros.csv' e 'residuos.csv' estão na mesma pasta do script.")
    else:
        main()
