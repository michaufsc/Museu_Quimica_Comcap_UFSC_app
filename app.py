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

# Diretório de imagens
IMAGES_DIR = "imagens_materiais"

# Cache para carregar dados
@st.cache_data
def load_data():
    polimeros = pd.read_csv("polimeros.csv", sep=";")
    residuos = pd.read_csv("residuos.csv", sep=";")
    return polimeros, residuos

# Cache para carregar quiz
@st.cache_data
def load_quiz():
    df = pd.read_csv("quiz_perguntas.csv", sep=";")
    questions = []
    for _, row in df.iterrows():
        opcoes = [str(row['opcao_1']), str(row['opcao_2']), str(row['opcao_3']), str(row['opcao_4'])]
        questions.append({
            "pergunta": row['pergunta'],
            "opcoes": opcoes,
            "resposta": int(row['resposta']),
            "explicacao": row['explicacao']
        })
    random.shuffle(questions)
    return questions

polimeros, residuos = load_data()

# Função: glossário interativo
def mostrar_glossario():
    st.header("📖 Glossário Interativo")
    dataset = st.radio("Selecione a base de dados:", ["Polímeros", "Resíduos"], horizontal=True)
    df = polimeros if dataset == "Polímeros" else residuos
    search_term = st.text_input("🔍 Buscar por termo, sigla ou aplicação:")

    if search_term:
        mask = df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        df = df[mask]

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
            **Nome:** {row.get('Nome', row.get('Categoria'))}  
            **Sigla:** {sigla}  
            **Tipo:** {row.get('Tipo de Polimerização', row.get('Classe ABNT', '-'))}  
            **Composição:** {row.get('Composição Química', '-')}  
            **Reciclável:** {row.get('Reciclável', '-')}  
            **Aplicações:** {row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', '-'))}
            """)
        st.divider()

# Função: atividades pedagógicas
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

# Função: quiz interativo
def mostrar_quiz():
    st.header("🧠 Quiz de Resíduos e Polímeros")

    if 'questions' not in st.session_state:
        st.session_state.questions = load_quiz()
        st.session_state.current_question = 0
        st.session_state.score = 0

    questions = st.session_state.questions
    q_num = st.session_state.current_question

    if q_num >= len(questions):
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
            del st.session_state.questions
            del st.session_state.current_question
            del st.session_state.score
            st.experimental_rerun()
        return

    question = questions[q_num]
    st.progress((q_num + 1) / len(questions))
    st.subheader(f"Pergunta {q_num + 1} de {len(questions)}")
    st.markdown(f"**{question['pergunta']}**")
    selected = st.radio("Escolha uma alternativa:", question['opcoes'], key=f"q{q_num}")

    if f"respondido_{q_num}" not in st.session_state:
        if st.button("Confirmar", key=f"b{q_num}"):
            st.session_state[f"respondido_{q_num}"] = True
            correta = selected == question['opcoes'][question['resposta']]
            st.session_state[f"correta_{q_num}"] = correta
            if correta:
                st.session_state.score += 1

    if f"respondido_{q_num}" in st.session_state:
        correta = st.session_state[f"correta_{q_num}"]
        if correta:
            st.success(f"✅ Correto! {question['explicacao']}")
        else:
            st.error(f"❌ Errado. {question['explicacao']}")

        if st.button("Próxima pergunta"):
            st.session_state.current_question += 1
            st.experimental_rerun()

# Função: compostagem

def mostrar_compostagem():
    st.header("🌱 Compostagem com os Dados Orgânicos")
    st.markdown("""
A compostagem artesanal, por meio da reciclagem de resíduos orgânicos, traz de volta à cidade a beleza e o equilíbrio das paisagens naturais.

A separação também facilita a destinação de recicláveis secos para a coleta seletiva.

---

### ✅ O que serve para a compostagem:
Cascas de frutas e de ovos, sobras de verduras, restos de comida, borra de café ou chimarrão, filtro de café, aparas de grama, etc.

---

### 🔄 Como é feita:
A compostagem propicia um ambiente favorável à ação de bactérias e fungos que iniciam a decomposição dos resíduos orgânicos. Atraídos por tanta fartura, insetos, minhocas e embuás também operam a reciclagem. O produto final é o composto orgânico, terra escura de excelente qualidade.

---

### 📊 Dados de Florianópolis:
- 35% dos resíduos domiciliares são orgânicos (24% restos de alimentos e 11% resíduos verdes)
- 43% são recicláveis secos
- 22% são rejeitos

Das 193 mil toneladas recolhidas por ano pela coleta da Comcap:
- Cerca de 70 mil toneladas são resíduos orgânicos
- Isso equivale a 27 caminhões por dia desviados do aterro sanitário

💰 Com custo de R$ 156,81 por tonelada para transporte e aterro, a economia ao separar o lixo orgânico pode chegar a R$ 11 milhões/ano

---

### 📚 Materiais úteis:
- [Manual para fazer compostagem com minhocas – Projeto Minhoca na Cabeça](https://)
- [Vídeo sobre valorização de orgânicos em Florianópolis](https://)
- [Manual de Compostagem Doméstica, Comunitária e Institucional – MMA, Cepagro e Sesc-SC](https://)
- [Livreto Compostagem Comunitária – Guia completo sobre valorização e gestão de resíduos](https://)
""")

# Função: história do Museu
def mostrar_historia():
    st.header("🏛️ História do Museu do Lixo")

    st.markdown("""
O Museu do Lixo, instalado pela Comcap em 25 de setembro de 2003, tornou-se referência entre as atividades de educação ambiental no Estado de Santa Catarina, pela forma lúdica e informal com que reforça conteúdos sobre consumo sustentável baseado nos quatro érres (4Rs) – **Repensar, Reduzir, Reutilizar e Reciclar**.

[...] (texto mantido conforme versão anterior)
""")

# Função principal
def main():
    st.header("Museu do Lixo - COMCAP Florianópolis ♻️")
    st.subheader("Aplicativo para educadores: Química dos resíduos")
    st.markdown("*Desenvolvido durante a disciplina de Prática de Ensino em Espaços de Divulgação Científica (Ext 18h-a)*")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏷️ Glossário",
        "🧠 Quiz",
        "📚 Atividades",
        "🌱 Compostagem",
        "🏛️ História do Museu",
        "ℹ️ Sobre"
    ])

    with tab1:
        mostrar_glossario()
    with tab2:
        mostrar_quiz()
    with tab3:
        mostrar_atividades()
    with tab4:
        mostrar_compostagem()
    with tab5:
        mostrar_historia()
    with tab6:
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
