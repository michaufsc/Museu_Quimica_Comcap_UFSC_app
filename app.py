import streamlit as st
import pandas as pd
import random

# Configuração da página
st.set_page_config(
    page_title="Sistema Educacional de Resíduos",
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

# Atividades Pedagógicas Corrigidas
def mostrar_atividades():
    st.header("📚 Atividades Pedagógicas Práticas")
    
    with st.expander("🔬 Para Ensino Fundamental (6º ao 9º ano)"):
        st.markdown("""
        ### 1. Jogo da Memória dos Polímeros
        **Materiais:** Cartões com imagens de polímeros e seus símbolos de reciclagem  
        **Objetivo:** Associar cada polímero ao seu símbolo e aplicação  
        **Duração:** 30 minutos

        ### 2. Experimento de Decomposição
        **Materiais:** Amostras de PET, PEAD, vidro, papel e orgânicos  
        **Objetivo:** Observar diferenças na degradação dos materiais  
        **Duração:** 2 meses (observações semanais)
        """)
    
    with st.expander("🧪 Para Ensino Médio"):
        st.markdown("""
        ### 1. Análise de Propriedades
        **Materiais:** Amostras de diferentes plásticos, fonte de calor, água  
        **Objetivo:** Identificar polímeros por densidade e teste de chama  
        **Duração:** 2 aulas

        ### 2. Simulação de Cooperativa
        **Materiais:** Resíduos diversos, balanças, tabelas de preços  
        **Objetivo:** Vivenciar processo de triagem e comercialização  
        **Duração:** 3 aulas
        """)
    
    with st.expander("🎓 Para Ensino Superior"):
        st.markdown("""
        ### 1. Análise de Ciclo de Vida
        **Materiais:** Dados de produção de PET vs PLA  
        **Objetivo:** Comparar impactos ambientais  
        **Duração:** 1 semana

        ### 2. Desenvolvimento de Biopolímeros
        **Materiais:** Amido de milho, glicerol, corante  
        **Objetivo:** Produzir plástico biodegradável  
        **Duração:** 4 aulas
        """)

# Gerar perguntas do quiz baseadas nos CSVs
def generate_quiz_questions():
    questions = []
    
    # Perguntas sobre polímeros
    for _, row in polimeros.iterrows():
        questions.append({
            "pergunta": f"Qual a principal aplicação do {row['Nome']} ({row['Sigla']})?",
            "opcoes": [
                row['Aplicações Comuns'],
                random.choice(polimeros['Aplicações Comuns']),
                random.choice(polimeros['Aplicações Comuns']),
                "Nenhuma das anteriores"
            ],
            "resposta": 0,
            "explicacao": f"O {row['Sigla']} é comumente usado em: {row['Aplicações Comuns']}"
        })
        
        questions.append({
            "pergunta": f"O {row['Nome']} ({row['Sigla']}) é biodegradável?",
            "opcoes": ["Sim", "Não", "Apenas em condições específicas", "Depende do processo"],
            "resposta": 0 if row['Biodegradável'] == 'Sim' else 1,
            "explicacao": f"Biodegradabilidade: {row['Biodegradável']}"
        })
    
    # Perguntas sobre resíduos
    for _, row in residuos.iterrows():
        questions.append({
            "pergunta": f"Como classificar {row['Categoria']} ({row['Sigla ou Nome']}) segundo ABNT?",
            "opcoes": [
                row['Classe ABNT'],
                random.choice(residuos['Classe ABNT']),
                random.choice(residuos['Classe ABNT']),
                "Não classificável"
            ],
            "resposta": 0,
            "explicacao": f"Classificação ABNT: {row['Classe ABNT']}"
        })
        
        questions.append({
            "pergunta": f"Qual o destino mais adequado para {row['Categoria']}?",
            "opcoes": [
                row['Destinação'],
                "Aterro sanitário",
                "Incineração",
                "Descarte comum"
            ],
            "resposta": 0,
            "explicacao": f"Destinação recomendada: {row['Destinação']}"
        })
    
    return random.sample(questions, min(20, len(questions)))

# Função do Quiz
def mostrar_quiz():
    st.header("🧠 Quiz de Resíduos e Polímeros")
    questions = generate_quiz_questions()
    
    if 'question_index' not in st.session_state:
        st.session_state.question_index = 0
        st.session_state.score = 0
    
    if st.session_state.question_index < len(questions):
        question = questions[st.session_state.question_index]
        
        st.subheader(f"Pergunta {st.session_state.question_index + 1}/{len(questions)}")
        st.markdown(f"**{question['pergunta']}**")
        
        answer = st.radio("Selecione a resposta:", question['opcoes'])
        
        if st.button("Confirmar"):
            if answer == question['opcoes'][question['resposta']]:
                st.success(f"✅ Correto! {question['explicacao']}")
                st.session_state.score += 1
            else:
                st.error(f"❌ Errado. Resposta correta: {question['opcoes'][question['resposta']]}")
            
            st.session_state.question_index += 1
            st.experimental_rerun()
    else:
        st.balloons()
        st.success(f"🎯 Quiz completo! Pontuação: {st.session_state.score}/{len(questions)}")
        
        if st.button("Refazer Quiz"):
            st.session_state.question_index = 0
            st.session_state.score = 0
            st.experimental_rerun()

# Interface principal
def main():
    tab1, tab2, tab3 = st.tabs([
        "🧠 Quiz", 
        "📚 Atividades", 
        "♻️ Glossário"
    ])
    
    with tab1:
        mostrar_quiz()
    
    with tab2:
        mostrar_atividades()
    
    with tab3:
        st.header("📖 Glossário Técnico")
        # Sua implementação existente do glossário aqui

if __name__ == "__main__":
    main()
