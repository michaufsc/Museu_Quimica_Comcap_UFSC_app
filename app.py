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
    st.header("🧐 Quiz de Resíduos e Polímeros")

    # Inicializa o estado do quiz
    if 'questions' not in st.session_state:
        st.session_state.questions = load_quiz()
        st.session_state.current_question = 0
        st.session_state.score = 0

    questions = st.session_state.questions
    q_num = st.session_state.current_question

    # Se terminou o quiz
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

        if st.button("🔄 Refazer Quiz"):
            for key in list(st.session_state.keys()):
                if key.startswith("q") or key.startswith("b") or key.startswith("respondido") or key.startswith("correta"):
                    del st.session_state[key]
            del st.session_state.questions
            del st.session_state.current_question
            del st.session_state.score
        return

    # Exibe a pergunta atual
    question = questions[q_num]
    st.progress((q_num + 1) / len(questions))
    st.subheader(f"Pergunta {q_num + 1} de {len(questions)}")
    st.markdown(f"**{question['pergunta']}**")

    # Widget de escolha
    selected = st.radio("Escolha uma alternativa:", question['opcoes'], key=f"q{q_num}")

    # Botão de confirmar
    if f"respondido_{q_num}" not in st.session_state:
        if st.button("✅ Confirmar", key=f"b{q_num}"):
            st.session_state[f"respondido_{q_num}"] = True
            correta = selected == question['opcoes'][question['resposta']]
            st.session_state[f"correta_{q_num}"] = correta
            if correta:
                st.session_state.score += 1

    # Mostra resultado e botão próxima
    if st.session_state.get(f"respondido_{q_num}", False):
        correta = st.session_state[f"correta_{q_num}"]
        if correta:
            st.success(f"✅ Correto! {question['explicacao']}")
        else:
            st.error(f"❌ Errado. {question['explicacao']}")

        if st.button("➡️ Próxima pergunta"):
            st.session_state.current_question += 1


# Função: história do Museu
def mostrar_historia():
    st.header("🏛️ Museu do Lixo – História e Agenda")

    st.markdown("""
O **Museu do Lixo**, instalado pela Comcap em **25 de setembro de 2003**, tornou-se uma referência em **educação ambiental** em Santa Catarina. Sua abordagem lúdica e acessível reforça conceitos de **consumo consciente** com base nos quatro érres (4Rs): **Repensar, Reduzir, Reutilizar e Reciclar**.

O museu nasceu do sonho de mais de dez anos de trabalhadores da Comcap, que desejavam **resgatar objetos descartados** para criar um espaço de memória sobre os hábitos de consumo da sociedade.

As primeiras peças foram reunidas no antigo galpão de triagem da coleta seletiva. Atualmente, o acervo está disposto em **ambientes temáticos**, montados e decorados com **materiais reaproveitados** — desde as tintas das paredes até a mandala do piso, tudo feito com resíduos reciclados.

---

### 🕓 Horário de Funcionamento  
📅 Segunda a sexta-feira  
🕗 Das 8h às 17h

**Visitas monitoradas devem ser agendadas:**  
📞 (48) 3261-4808  
📧 ambiental.comcap@pmf.sc.gov.br

---

### 📍 Localização  
Rodovia Admar Gonzaga, 72 – Bairro Itacorubi, Florianópolis – SC
""")

#função química 
def mostrar_quimica():
    st.header("🧪 Química dos Polímeros e Reciclagem")

    st.markdown("""
    Os **polímeros** são macromoléculas formadas por unidades repetitivas chamadas monômeros. Eles podem ser naturais, como a celulose, ou sintéticos, como:
    - Polietileno (PE)
    - Polipropileno (PP)
    - Poli(tereftalato de etileno) (PET)
    - Poli(cloreto de vinila) (PVC)
    - Poliestireno (PS)

    Os **termoplásticos**, como PE, PP, PET, PVC e PS, possuem as seguintes características:
    - Moldáveis a quente
    - Baixa densidade
    - Boa aparência
    - Isolantes térmico e elétrico
    - Resistentes ao impacto
    - Baixo custo

    No Brasil, o consumo de termoplásticos tem crescido significativamente. Por exemplo, o PET apresentou um aumento de mais de **2.200%** na última década.

    A **separação automatizada** de polímeros é realizada com base na diferença de densidade, utilizando tanques de flotação ou hidrociclones para:
    - PE
    - PP
    - PS
    - PVC
    - PET

    A **reciclagem** desses materiais envolve tecnologias mecânicas e químicas, além da recuperação de energia a partir de resíduos plásticos.

    Empresas recicladoras de PE e PP processam entre 20 e 50 toneladas por mês, com poucas ultrapassando 100 toneladas mensais. As principais aplicações dos polímeros reciclados são em utilidades domésticas.
    """)

# Função: compostagem
def mostrar_compostagem():
    st.header("🌱 Compostagem com Resíduos Orgânicos")

    st.markdown("""
A **compostagem artesanal**, por meio da reciclagem de resíduos orgânicos, traz de volta à cidade a beleza e o equilíbrio das paisagens naturais. Além disso, a separação correta dos resíduos facilita a destinação dos recicláveis secos para a coleta seletiva.
""")

    st.subheader("✅ O que pode ir para a compostagem:")
    st.markdown("""
- Cascas de frutas e de ovos  
- Sobras de verduras e legumes  
- Restos de comida (sem excesso de sal ou gordura)  
- Borra de café ou chimarrão  
- Filtro de papel do café  
- Aparas de grama  
- Folhas secas  
- Palhas, serragem e pequenos galhos
""")

    st.subheader("⚠️ O que NÃO deve ir para a compostagem:")
    st.markdown("""
- Carnes, laticínios e peixes  
- Excrementos de animais domésticos  
- Óleos, gorduras e produtos químicos  
- Itens sanitários ou plásticos
""")

    st.subheader("🧪 Como funciona a compostagem")
    st.markdown("""
A compostagem cria um ambiente propício à ação de **bactérias e fungos** que decompõem a matéria orgânica. Também participam do processo **minhocas, insetos e embuás**, transformando os resíduos em um **composto orgânico** — uma terra escura, fértil e rica em nutrientes.

Esse composto pode ser usado em hortas, vasos, jardins e áreas públicas, ajudando a regenerar o solo e fechar o ciclo dos alimentos.
""")

    st.subheader("📊 Dados de Florianópolis")
    st.markdown("""
- **35%** dos resíduos domiciliares são orgânicos  
  - 24%: restos de alimentos  
  - 11%: resíduos verdes (podas, folhas, jardinagem)  
- **43%** são recicláveis secos  
- **22%** são rejeitos (lixo não reciclável)

Das **193 mil toneladas** coletadas anualmente, **70 mil toneladas** são resíduos orgânicos. Separando-os na fonte, evitaríamos o envio de **27 caminhões de lixo por dia** ao aterro de Biguaçu.
""")

    st.subheader("💰 Economia e benefícios")
    st.markdown("""
Cada tonelada aterrada custa **R$ 156,81** ao município.  
Com compostagem, Florianópolis poderia economizar até **R$ 11 milhões por ano**, além de reduzir impactos ambientais e melhorar a qualidade do solo urbano.
""")

    st.subheader("📚 Materiais e links úteis")
    st.markdown("""
- 📘 [**Manual de Compostagem com Minhocas – Projeto Minhoca na Cabeça**](https://cepagroagroecologia.wordpress.com/minhoca-na-cabeca/)  
- 🎥 [**Vídeo sobre valorização dos orgânicos em Florianópolis**](https://www.youtube.com/watch?v=xyz)  
- 📗 [**Manual de Compostagem – MMA, Cepagro, SESC-SC**](https://www.mma.gov.br)  
- 📒 [**Livreto: Compostagem Comunitária – Guia Completo**](https://compostagemcomunitaria.com.br)
""")


def main():
    st.header("Museu do Lixo - COMCAP Florianópolis ♻️")
    # ... (cabeçalho mantido igual)
    st.markdown("---")
    st.markdown("---")
    # Verificação dos arquivos (debug - pode remover depois)
    st.write("Arquivos no diretório:", [f for f in os.listdir() if f.endswith(('.png', '.jpg', '.jpeg'))])
    
    # Linha de logos modificada
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if os.path.exists("logo_ufsc.png"):
            st.image("logo_ufsc.png", width=120)
        else:
            st.warning("UFSC logo não encontrado")
    
    with col2:
        if os.path.exists("logo_comcap.png"):
            st.image("logo_comcap.png", width=120)
        else:
            st.warning("COMCAP logo não encontrado")
    
    with col3:
        if os.path.exists("logo_museu.png"):
            st.image("logo_museu.png", width=120)
        else:
            st.warning("Museu logo não encontrado")
    
    st.markdown("---")
    # ... (restante do código)

    st.markdown("---")
    # ... (restante do código)
    
    # Linha de logos (ajuste os caminhos das imagens)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.image("https://example.com/logo_ufsc.png", width=120)  # Logo UFSC
    with col2:
        st.image("https://example.com/logo_comcap", width=120)  # Logo COMCAP
    with col3:
        st.image("https://example.com/logo_museu.png", width=120)  # Logo Museu
    
    # Restante do código atual...
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏛️ História do Museu",
        "🏷️ Glossário",
        "🧐 Quiz",
        "📚 Atividades",
        "🌱 Compostagem",
        "🧪 Química",
        "ℹ️ Sobre"
    ])

    with tab1:
        mostrar_historia()
    with tab2:
        mostrar_glossario()
    with tab3:
        mostrar_quiz()
    with tab4:
        mostrar_atividades()
    with tab5:
        mostrar_compostagem()
    with tab6:
        mostrar_quimica()
    with tab7:
        st.header("Sobre o Projeto")
        st.markdown("""
**Glossário Interativo de Resíduos e Polímeros**  
- Desenvolvido para educação ambiental  
- Dados técnicos baseados em normas ABNT  
- Integrado com atividades pedagógicas  

**Autor:** nome alunos e prof  
**Disciplina:** Prática de Ensino em Espaços de Divulgação Científica (Ext 18h-a)  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)
        """)

if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    main()

