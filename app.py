import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
import re
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Caminho correto para a pasta de imagens
IMAGES_MATERIAIS_DIR = "imagens_materiais"
IMAGES_RESIDUOS_DIR = "imagens_residuos"

IMAGES_DIR = "imagens"
# Cria as pastas de imagem se não existirem
os.makedirs(IMAGES_MATERIAIS_DIR, exist_ok=True)
os.makedirs(IMAGES_RESIDUOS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)


# Função para normalizar nomes (exemplo simples)
def normalizar_nome(nome):
    return nome.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "").replace(",", "")

# Função para mostrar imagens com fallback
def mostrar_imagem_com_fallback(nome_imagem, caminho_dir, legenda, cor_fundo):
    caminho_imagem = os.path.join(caminho_dir, nome_imagem)
    if os.path.exists(caminho_imagem):
        try:
            img = Image.open(caminho_imagem)
            st.image(img, use_container_width=True, caption=legenda)
        except:
            img_padrao = Image.new('RGB', (300, 300), color=cor_fundo)
            st.image(img_padrao, use_container_width=True, caption=legenda)
    else:
        img_padrao = Image.new('RGB', (300, 300), color=cor_fundo)
        st.image(img_padrao, use_container_width=True, caption=legenda)


# Configuração da página
st.set_page_config(
    page_title="Química para reciclagem e limpeza dos oceanos",
    page_icon="♻️",
    layout="wide"
)

# Carregar dados (polímeros e resíduos)
@st.cache_data
def load_data():
    polimeros = pd.read_csv("polimeros.csv", sep=";")
    residuos = pd.read_csv("residuos.csv", sep=";")
    return polimeros, residuos

# Adicione esta função para carregar os dados da coleta seletiva
@st.cache_data
def load_coleta_data():
    url = "https://raw.githubusercontent.com/michaufsc/glossario-quimica-residuos/refs/heads/main/pontos_coleta.csv"
    df = pd.read_csv(url)
    return df

# Carregar perguntas do quiz
@st.cache_data
def load_quiz():
    df = pd.read_csv("quiz_perguntas.csv", sep=";")
    questions = []
    for _, row in df.iterrows():
        opcoes = [str(row['opcao_1']), str(row['opcao_2']), str(row['opcao_3']), str(row['opcao_4'])]
        questions.append({
            "pergunta": row['pergunta'],
            "opcoes": opcoes,
            "opcoes": [row['opcao_1'], row['opcao_2'], row['opcao_3'], row['opcao_4']],
            "resposta": int(row['resposta']),
            "explicacao": row['explicacao']
            "explicacao": row['explicacao'],
            "imagem": os.path.join(IMAGES_DIR, row['imagem']) if pd.notna(row['imagem']) else None
        })
    random.shuffle(questions)
    return questions

    
# Carrega os dados
@st.cache_data
def load_data():
    try:
        # Carrega os dados com tratamento de encoding e espaços
        polimeros = pd.read_csv("polimeros.csv", sep=";", encoding='utf-8').apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        residuos = pd.read_csv("residuos.csv", sep=";", encoding='utf-8').apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # Remove espaços dos nomes das colunas
        polimeros.columns = polimeros.columns.str.strip()
        residuos.columns = residuos.columns.str.strip()

        return polimeros, residuos
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()  # Retorna DataFrames vazios em caso de erro

# Função para carregar o CSV com as cooperativas
import pandas as pd

def load_cooperativas():
    """
    Carrega os dados das cooperativas de reciclagem.
    Retorna um DataFrame com: nome, endereco, latitude, longitude, descricao.
    """

    # Dados diretamente no código
    data = [
        {
            "nome": "Associação de Catadores de Materiais Recicláveis de Florianópolis (ACMR)",
            "endereco": "Rua João Pio Duarte Silva, 150",
            "latitude": -27.5942,
            "longitude": -48.5478,
            "descricao": "Maior associação, responsável pela triagem e comercialização dos recicláveis."
        },
        {
            "nome": "Associação dos Catadores de Materiais Recicláveis do bairro Capoeiras",
            "endereco": "Av. Mauro Ramos, 820",
            "latitude": -27.5945,
            "longitude": -48.5450,
            "descricao": "Foco na inclusão social e sustentabilidade ambiental."
        },
        {
            "nome": "Associação dos Catadores de Materiais Recicláveis do bairro Estreito",
            "endereco": "Rua Henrique Meyer, 300",
            "latitude": -27.6000,
            "longitude": -48.5330,
            "descricao": "Promove trabalho digno e educação ambiental."
        },
        {
            "nome": "Cooperativa de Reciclagem e Trabalho de Florianópolis (COOPERTFLOR)",
            "endereco": "Rua Des. Pedro Silva, 200",
            "latitude": -27.5950,
            "longitude": -48.5400,
            "descricao": "Atua com triagem e comercialização, valorizando o trabalho dos catadores."
        },
        {
            "nome": "Associação de Catadores de Materiais Recicláveis do bairro Itacorubi",
            "endereco": "Rua Henrique Veras, 180",
            "latitude": -27.5930,
            "longitude": -48.5600,
            "descricao": "Promove ações de reciclagem e conscientização ambiental."
        },
        {
            "nome": "Associação dos Catadores de Materiais Recicláveis do bairro Saco Grande",
            "endereco": "Rua Deputado Antônio Edu Vieira, 250",
            "latitude": -27.6005,
            "longitude": -48.5405,
            "descricao": "Organiza cooperativa para melhorar as condições de trabalho."
        },
        {
            "nome": "Cooperativa de Catadores de Florianópolis (COOPERCAT)",
            "endereco": "Rua José Maria Tavares, 100",
            "latitude": -27.5960,
            "longitude": -48.5450,
            "descricao": "Valoriza a inclusão social e sustentabilidade."
        }
    ]

    # Criar DataFrame
    df = pd.DataFrame(data)

    # Garantir que latitude e longitude sejam float válidos
    df['latitude'] = df['latitude'].astype(str).str.replace(',', '.').astype(float)
    df['longitude'] = df['longitude'].astype(str).str.replace(',', '.').astype(float)

    # Eliminar valores faltantes ou inválidos
    df = df.dropna(subset=['latitude', 'longitude'])
    df = df[(df['latitude'].between(-90, 0)) & (df['longitude'].between(-90, -30))]

    return df

#mostrar glossário
def mostrar_glossario_polimeros(polimeros: pd.DataFrame):
    st.header("🧪 Glossário Completo de Polímeros")

    for _, row in polimeros.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3], gap="medium")

            with col1:
                nome_imagem = normalizar_nome(row['Sigla']) + ".png"
                caminho_imagem = os.path.join(IMAGES_MATERIAIS_DIR, nome_imagem)

                if os.path.exists(caminho_imagem):
                    st.image(Image.open(caminho_imagem), use_container_width=True, caption=f"{row['Nome']}")
                else:
                    img_padrao = Image.new('RGB', (300, 300), color=(220, 220, 255))
                    st.image(img_padrao, use_container_width=True, caption=f"{row['Nome']}")

            with col2:
                st.subheader(f"{row['Sigla']} - {row['Nome']}")
                st.markdown(f"**Código:** {row['Código de Identificação']}")
                st.markdown(f"**Tipo de Polimerização:** {row['Tipo de Polimerização']}")
                st.markdown(f"**Densidade:** {row['Densidade']}")
                st.markdown(f"**Ponto de Fusão:** {row['Ponto de Fusão']}")
                st.markdown(f"**Reciclável:** {row['Reciclável']}")
                st.markdown(f"**Aplicações Comuns:** {row['Aplicações Comuns']}")
                st.markdown(f"**Descrição:** {row['Descrição']}")

def mostrar_glossario_residuos(residuos: pd.DataFrame):
    st.header("♻️ Glossário Completo de Resíduos")

    # Verifica se o DataFrame está vazio
    if residuos.empty:
        st.warning("Nenhum dado de resíduos disponível.")
        return
    # Verifica se os arquivos existem
    required_files = ["polimeros.csv", "residuos.csv"]
    for file in required_files:
        if not os.path.exists(file):
            st.error(f"Arquivo necessário não encontrado: {file}")
            return  # Encerra a execução se algum arquivo estiver faltando

    # Carrega os dados
    polimeros, residuos = load_data()

    # Verifica se os DataFrames foram carregados corretamente
    if polimeros.empty or residuos.empty:
        st.error("Não foi possível carregar os dados. Verifique os arquivos CSV.")
        return
    # Verifica as colunas disponíveis (para debug)
    st.write("Colunas disponíveis:", residuos.columns.tolist())

    for _, row in residuos.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3], gap="medium")

            with col1:
                # Acesso seguro às colunas
                tipo = str(row.get('Tipo', 'Resíduo')).strip()
                subtipo = str(row.get('Subtipo', tipo)).split('(')[0].strip()

                nome_imagem = normalizar_nome(subtipo) + ".png"
                caminho_imagem = os.path.join(IMAGES_RESIDUOS_DIR, nome_imagem)

                if os.path.exists(caminho_imagem):
                    st.image(Image.open(caminho_imagem), use_container_width=True, caption=f"{subtipo}")
                else:
                    img_padrao = Image.new('RGB', (300, 300), color=(200, 230, 200))
                    st.image(img_padrao, use_container_width=True, caption=f"{subtipo}")

            with col2:
                st.subheader(f"{tipo} - {subtipo}")

                # Adiciona todas as colunas disponíveis dinamicamente
                campos = {
                    'Código': row.get('Código', ''),
                    'Exemplos Comuns': row.get('Exemplos Comuns', ''),
                    'Tempo de Decomposição': row.get('Tempo de Decomposição', ''),
                    'Reciclável': row.get('Reciclável', ''),
                    'Rota de Tratamento': row.get('Rota de Tratamento', ''),
                    'Descrição Técnica': row.get('Descrição Técnica', '')
                }

                for campo, valor in campos.items():
                    if valor:  # Só mostra se tiver valor
                        st.markdown(f"**{campo}:** {valor}")

        st.divider()

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
    st.header("♻️ Quiz Interativo - Museu do Lixo COMCAP")
    st.markdown("Teste seus conhecimentos sobre reciclagem, polímeros e sustentabilidade!")
    
    # Inicializa o estado da sessão
    if 'quiz' not in st.session_state:
        st.session_state.quiz = {
            'questions': load_quiz(),
            'current_question': 0,
            'score': 0,
            'answered': False,
            'selected_option': None,
            'show_results': False
        }
    
    questions = st.session_state.quiz['questions']
    current_q = st.session_state.quiz['current_question']
    
    # Verifica se terminou o quiz
    if st.session_state.quiz['show_results'] or current_q >= len(questions):
        mostrar_resultado_final()
        return
    
    # Mostra progresso
    mostrar_barra_progresso(current_q, len(questions))
    
    # Obtém a pergunta atual
    question = questions[current_q]
    
    # Layout da pergunta
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Pergunta {current_q + 1}/{len(questions)}")
        st.markdown(f"#### {question['pergunta']}")
        
        # Mostra opções como botões
        selected = None
        for i, opcao in enumerate(question['opcoes']):
            if st.button(opcao, 
                         key=f"op_{current_q}_{i}",
                         disabled=st.session_state.quiz['answered'],
                         use_container_width=True):
                selected = i
                st.session_state.quiz['selected_option'] = i
                st.session_state.quiz['answered'] = True
    
    with col2:
        # Mostra imagem se existir
        if question.get('imagem') and os.path.exists(question['imagem']):
            try:
                st.image(
                    question['imagem'],
                    caption="Imagem referente à pergunta",
                    use_column_width=True,
                    output_format="auto"
                )
            except Exception as e:
                st.warning(f"Não foi possível carregar a imagem: {str(e)}")
        elif question.get('imagem'):
            st.warning("Imagem não encontrada")
    
    # Se já respondeu, mostra feedback
    if st.session_state.quiz['answered']:
        mostrar_feedback(question)
        
        # Botão para próxima pergunta
        if st.button("Próxima Pergunta →", 
                    key=f"next_{current_q}",
                    type="primary"):
            avancar_quiz()

def mostrar_barra_progresso(atual, total):
    progresso = (atual + 1) / total
    st.progress(progresso)
    st.caption(f"Progresso: {atual + 1} de {total} perguntas")

def mostrar_feedback(question):
    st.markdown("---")
    selected = st.session_state.quiz['selected_option']
    correct = selected == question['resposta']
    
    if correct:
        st.success("✅ **Correto!** " + question['explicacao'])
        st.balloons()
    else:
        st.error(f"❌ **Ops!** A resposta correta é: **{question['opcoes'][question['resposta']]}**")
        st.info("💡 **Explicação:** " + question['explicacao'])
    
    # Mostra link para mais informações quando relevante
    if "Museu do Lixo" in question['pergunta']:
        st.markdown("[🔍 Saiba mais sobre o Museu](https://www.pmf.sc.gov.br/entidades/comcap/)")

def avancar_quiz():
    # Atualiza pontuação se acertou
    questions = st.session_state.quiz['questions']
    current_q = st.session_state.quiz['current_question']
    selected = st.session_state.quiz['selected_option']
    
    if selected == questions[current_q]['resposta']:
        st.session_state.quiz['score'] += 1
    
    # Prepara próximo estado
    st.session_state.quiz['current_question'] += 1
    st.session_state.quiz['answered'] = False
    st.session_state.quiz['selected_option'] = None
    
    # Verifica se terminou
    if st.session_state.quiz['current_question'] >= len(questions):
        st.session_state.quiz['show_results'] = True

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

def mostrar_resultado_final():
    score = st.session_state.quiz['score']
    total = len(st.session_state.quiz['questions'])
    
    st.success(f"## 🎯 Resultado Final: {score}/{total}")
    
    # Feedback personalizado
    if score == total:
        st.balloons()
        st.markdown("""
        ### 🌟 Excelente! Você é um expert em reciclagem!
        *Parabéns! Seu conhecimento sobre resíduos e sustentabilidade é impressionante.*
        """)
    elif score >= total * 0.75:
        st.markdown("""
        ### 👏 Muito bom!
        *Você tem um ótimo entendimento do assunto! Continue aprendendo.*
        """)
    else:
        st.markdown("""
        ### 📚 Continue explorando!
        *Visite o glossário para melhorar seu conhecimento sobre reciclagem.*
        """)
    
    # Botão para reiniciar
    if st.button("🔄 Refazer Quiz", type="primary"):
        for key in list(st.session_state.keys()):
            if key.startswith('quiz'):
                del st.session_state[key]
        st.rerun()
    
    # Links úteis
    st.markdown("---")
    st.markdown("### 📚 Para aprender mais:")
    st.page_link("app.py", label="Visitar Glossário", icon="📖")
    st.page_link("https://www.pmf.sc.gov.br/entidades/comcap/", label="Site do Museu do Lixo", icon="🏛️")

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

    st.markdown("""
### 🔍 Saiba mais

- O museu integra o roteiro de **visitação monitorada ao Centro de Valorização de Resíduos (CVR)** da Comcap, empresa de economia mista da Prefeitura de Florianópolis.  
- Recebe cerca de **7 mil visitantes por ano**, mediante agendamento prévio.  
- O acervo conta com aproximadamente **10 mil itens** recuperados na coleta ou por **entrega voluntária**, ainda em processo de catalogação.  
- A instalação ocupa uma área de **200 m²**.  
- Coleções em destaque: ferros de passar roupa, latas de refrigerante e de cerveja, máquinas fotográficas e de costura, aparelhos de telefone e computadores.  
- Os ambientes são decorados com **materiais reutilizados**, desde tintas até pisos.  
- Foram criados personagens para as atividades educativas, como **Neiciclagem** (Valdinei Marques), **Dona Tainha** (Joseane Rosa), **Vento Sul** e **Reciclardo** (Ricardo Conceição).

---
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
- Frutas, legumes e verduras  
- Cascas de ovos  
- Borra de café com filtro  
- Folhas secas e grama  
- Serragem e palha  
- Restos de poda triturados
""")

    st.subheader("❌ O que NÃO pode ir para a compostagem:")
    st.markdown("""
- Carnes, laticínios e peixes  
- Excrementos de animais domésticos  
- Óleos, gorduras e produtos químicos  
- Itens sanitários ou plásticos
""")

    st.subheader("🧪 Como funciona a compostagem")
    st.markdown("""
A compostagem cria um ambiente propício à ação de **bactérias e fungos** que decompõem a matéria orgânica. Também participam do processo **minhocas, insetos e embuás**, transformando os resíduos em um **composto orgânico**, uma terra escura, fértil e rica em nutrientes.

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
- [\U0001F4D8 **Manual de Compostagem com Minhocas: Projeto Minhoca na Cabeça**](https://cepagroagroecologia.wordpress.com/minhoca-na-cabeca/)  
- [\U0001F3A5 **Vídeo sobre valorização dos orgânicos em Florianópolis**](https://www.youtube.com/watch?v=xyz)  
- [\U0001F4D7 **Manual de Compostagem: MMA, Cepagro, SESC-SC**](https://www.mma.gov.br)  
- [\U0001F4D2 **Livreto: Compostagem Comunitária – Guia Completo**](https://compostagemcomunitaria.com.br)
""")
#função mapa
def mostrar_mapa_coleta():
    st.header("🗺️ Mapa Completo dos Pontos de Coleta Seletiva")

    df_coleta = load_coleta_data()

    # Verificação básica
    if 'latitude' not in df_coleta.columns or 'longitude' not in df_coleta.columns:
        st.error("Os dados não possuem colunas 'latitude' e 'longitude'")
        return

    # Centro do mapa
    centro_lat = df_coleta['latitude'].mean()
    centro_lon = df_coleta['longitude'].mean()

    # Criação do mapa
    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=12)

    for _, row in df_coleta.iterrows():
        popup_text = f"<b>{row.get('nome', 'Ponto de Coleta')}</b><br>{row.get('endereco', '')}<br>{row.get('tipo', '')}"
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup_text,
            icon=folium.Icon(color="green", icon="recycle", prefix='fa')
        ).add_to(mapa)

    folium_static(mapa)

# coleta seletiva
def mostrar_coleta_seletiva():
    st.header("🏘️ Coleta Seletiva por Bairro")

    df = load_coleta_data()

    # Verifica e converte as colunas de latitude e longitude para numéricas
    df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
    df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')

    # Remove linhas com coordenadas inválidas
    df = df.dropna(subset=['latitude', 'longitude'])

    with st.expander("📋 Filtros - clique para abrir/fechar"):
        bairros = sorted(df['nome'].str.extract(r'^(.*?)(?=\s*-)')[0].dropna().unique())
        bairros.insert(0, "Todos")
        bairro_selecionado = st.selectbox("Selecione um bairro:", bairros, index=0)

        tipos = ["Todos"] + list(df['tipo'].dropna().unique())
        tipo_selecionado = st.radio("Tipo de ponto:", tipos, horizontal=True)

    # Aplica os filtros
    dados_filtrados = df.copy()
    if bairro_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['nome'].str.contains(bairro_selecionado, case=False, na=False)]
    if tipo_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['tipo'] == tipo_selecionado]

    # Mostra a tabela
    st.markdown(f"### 📌 {len(dados_filtrados)} ponto(s) encontrado(s)")
    st.dataframe(dados_filtrados.reset_index(drop=True))

    # Mostra o mapa (se houver dados com latitude e longitude válidas)
    if not dados_filtrados.empty:
        try:
            centro_lat = dados_filtrados['latitude'].mean()
            centro_lon = dados_filtrados['longitude'].mean()

            mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)

            for _, row in dados_filtrados.iterrows():
                popup = f"<b>{row.get('nome', 'Ponto de Coleta')}</b><br>{row.get('endereco', '')}<br>{row.get('tipo', '')}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup,
                    icon=folium.Icon(color="green", icon="recycle", prefix="fa")
                ).add_to(mapa)

            st.markdown("### 🗺️ Mapa dos Pontos Filtrados")
            folium_static(mapa)
        except Exception as e:
            st.warning(f"Não foi possível exibir o mapa: {str(e)}")
    else:
        st.warning("Nenhum ponto encontrado com os filtros selecionados.")


# Aba: Microplásticos

def mostrar_microplasticos():
    st.header("🧩 Microplásticos – Um Problema Invisível nos Mares")

    st.markdown("""
    ### ♻️ Microplásticos: o que são e por que devemos nos preocupar?

    Florianópolis é famosa por suas mais de 100 praias, mas por trás da paisagem deslumbrante há um problema invisível que ameaça a vida marinha e a saúde humana: **os microplásticos**.

    ---

    ### 🔎 O que são microplásticos?

    Microplásticos são fragmentos de plástico com menos de 5 milímetros, muitas vezes invisíveis a olho nu.

    Eles se dividem em dois tipos:

    - **Primários**: fabricados intencionalmente nesse tamanho, como microesferas usadas em cosméticos, pastas de dente e produtos de limpeza.
    - **Secundários**: formados pela fragmentação de plásticos maiores devido ao sol, chuva, vento, ondas e ação de organismos.

    Esses fragmentos acabam nos oceanos e podem permanecer por **décadas no ambiente**, acumulando-se em praias, sedimentos e até na água potável.

    ---

    ### ⚗️ A Química contra a poluição invisível

    A Química nos permite **detectar, identificar e compreender** os efeitos dos microplásticos:

    - Técnicas como **espectroscopia FTIR e Raman** identificam o tipo de polímero presente nas partículas.
    - Substâncias tóxicas como **bisfenol A (BPA)** e **ftalatos**, presentes nos plásticos, podem se desprender e agir como **disruptores endócrinos**, afetando o sistema hormonal de animais e humanos.
    - A combinação de análises físico-químicas com estudos biológicos permite avaliar os **efeitos toxicológicos em diferentes espécies.**

    ---

    ### 🐠 Impactos nos oceanos e na vida marinha

    Animais marinhos frequentemente ingerem microplásticos por engano, levando a:

    - Dificuldade de digestão e absorção de nutrientes;
    - Inflamações e bloqueios intestinais;
    - Acúmulo de substâncias tóxicas nos tecidos.

    Os efeitos não param por aí: os microplásticos **sobem na cadeia alimentar**, chegando até peixes e frutos do mar consumidos por humanos — um risco silencioso, mas real.

    ---

    ### 🌍 O caso de Florianópolis

    Com suas mais de 100 praias e alto consumo de frutos do mar, **Florianópolis está diretamente exposta à contaminação por microplásticos.** A limpeza inadequada das praias, o descarte incorreto de lixo e o turismo intenso aumentam o risco da poluição plástica marinha.

    Estudos já identificaram a presença de microplásticos em:
    - Praias urbanas e remotas da ilha;
    - Ostras, mexilhões e peixes vendidos em mercados locais;
    - Sedimentos de rios que deságuam no mar.

    ---

    ### ✅ O que você pode fazer?

    #### Como cidadão:
    - Evite produtos com microesferas plásticas.
    - Reduza o uso de plástico descartável.
    - Participe de limpezas de praia e separe seu lixo corretamente.

    #### Como estudante, professor ou pesquisador:
    - Incentive a pesquisa sobre alternativas sustentáveis.
    - Estimule debates nas escolas sobre consumo consciente e química ambiental.
    - Divulgue ações de preservação dos oceanos e fontes de poluição invisível.

    ---

    ### 📚 Referências

    1. Rezende, L. T. et al. *Microplásticos: ocorrência ambiental e desafios analíticos*. **Química Nova**, 2022. [https://www.scielo.br/j/qn/a/VJ58TBjHVqDZsvWLckcFbTQ](https://www.scielo.br/j/qn/a/VJ58TBjHVqDZsvWLckcFbTQ)
    2. Dawson, A. L. et al. (2023). *Microplastics: A new contaminant in the environment*. **Frontiers in Environmental Science**, [PMC9914693](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9914693/)
    3. ISO/TR 21960:2020. *Plastics — Environmental aspects — State of knowledge and methodologies*.
    4. Browne, M. A. et al. (2011). *Accumulation of microplastic on shorelines worldwide: sources and sinks*. **Environmental Science & Technology**.
    5. NOAA – National Oceanic and Atmospheric Administration (2009). *Microplastics Program Overview*.
    6. Cózar, A. et al. (2014). *Plastic debris in the open ocean*. **PNAS**.
    """)

#função coperativas
def mostrar_cooperativas():
    st.header("♻️ Cooperativas de Reciclagem de Florianópolis")

    st.markdown("""
    As cooperativas de reciclagem em Florianópolis exercem um papel essencial na gestão dos resíduos sólidos urbanos, contribuindo para a sustentabilidade ambiental, inclusão social e geração de trabalho digno para catadores e cooperados. Estas organizações funcionam a partir de princípios democráticos e autogestionários, promovendo o protagonismo dos trabalhadores no processo produtivo e na tomada de decisões.

    ### Governança e Organização
    A governança das cooperativas é pautada na participação coletiva, que fortalece a autonomia dos cooperados e a gestão compartilhada dos recursos. Apesar disso, enfrentam desafios estruturais como limitações de infraestrutura, falta de equipamentos e veículos próprios, além da necessidade de capacitação em áreas administrativas e de segurança no trabalho.

    ### Desafios
    Dentre os principais desafios estão a precariedade na infraestrutura física, dificuldade em acessar linhas de crédito e financiamentos específicos, além da falta de políticas públicas integradas que fortaleçam o setor. A valorização social e institucional destas cooperativas é fundamental para garantir sua sustentabilidade econômica, social e ambiental.

    ### Importância das Cooperativas
    Além do impacto ambiental positivo, as cooperativas contribuem para a economia circular e a redução de resíduos enviados a aterros sanitários. O trabalho coletivo gera renda e promove a inclusão social de grupos vulneráveis, reforçando a importância da participação cidadã na gestão dos resíduos sólidos.

    ### Referências
    - CARRION, C. L. G.; MARTINS, D. T. M.; et al. Cooperativismo e inclusão social: um estudo das cooperativas de catadores de resíduos sólidos em Florianópolis. *Repositório UFSC*, 2022. [Link](https://repositorio.ufsc.br/handle/123456789/192872)
    - PREFEITURA MUNICIPAL DE FLORIANÓPOLIS. *Plano Municipal de Gestão Integrada de Resíduos Sólidos*. Florianópolis: PMF, 2022. [PDF](https://www.pmf.sc.gov.br/arquivos/documentos/pdf/24_06_2022_15.28.44.a6b5dac659782748068dd07d94d5c782.pdf)
    - OLIVEIRA, R. F.; SILVA, M. S. Gestão ambiental e desafios das cooperativas de reciclagem. *Revista Gestão Ambiental*, v. 14, n. 2, p. 115-130, 2021. [Artigo](https://portaldeperiodicos.animaeducacao.com.br/index.php/gestao_ambiental/article/view/3908/3086)
    """)

    df = load_cooperativas()

    tab_lista, tab_mapa = st.tabs(["📋 Lista de Cooperativas", "🗺️ Mapa"])

    with tab_lista:
        st.subheader("Cooperativas Cadastradas")

        busca = st.text_input("Pesquisar cooperativas:", placeholder="Digite nome ou endereço")

        if busca:
            df_filtrado = df[
                df['nome'].str.contains(busca, case=False, na=False) |
                df['endereco'].str.contains(busca, case=False, na=False)
            ]
        else:
            df_filtrado = df.copy()

        st.dataframe(
            df_filtrado.rename(columns={
                'nome': 'Cooperativa',
                'endereco': 'Endereço',
                'descricao': 'Descrição'
            }),
            hide_index=True,
            use_container_width=True,
            height=min(400, 45 * len(df_filtrado) + 45)
        )

    with tab_mapa:
        st.subheader("Localização das Cooperativas")

        mapa = folium.Map(
            location=[df['latitude'].mean(), df['longitude'].mean()],
            zoom_start=13,
            tiles="cartodbpositron"
        )

        for _, row in df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(f"""
                    <div style='width:250px'>
                        <h4>{row['nome']}</h4>
                        <p><b>Endereço:</b> {row['endereco']}</p>
                        <p><b>Atuação:</b> {row['descricao']}</p>
                    </div>
                """, max_width=300),
                icon=folium.Icon(color="green", icon="recycle", prefix="fa")
            ).add_to(mapa)

        folium_static(mapa, width=700, height=500)
        st.caption("📍 Clique nos marcadores para ver detalhes")


# Função principal
# Função principal
def main():
    st.header("Museu do Lixo - COMCAP Florianópolis ♻️")
    st.subheader("Aplicativo para educadores: Química dos resíduos")
    st.markdown("*Desenvolvido durante a disciplina de Prática de Ensino em Espaços de Divulgação Científica (Ext 18h)*")
    st.markdown("---")

    # Abas principais com novas seções
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🏛️ História do Museu",
        "🏷️ Glossário",
        "🧐 Quiz",
        "🌱 Compostagem",
        "🧪 Química dos Polímeros",
        "🏘️ Coleta Seletiva por Bairro",
        "🧵 Microplásticos",
        "🤝 Associações de Reciclagem",
        "📚 Atividades Pedagógicas",
        "ℹ️ Sobre"
    ])

    with tab1:
        mostrar_historia()

    with tab2:
        mostrar_glossario(polimeros, residuos)

    with tab3:
        mostrar_quiz()

    with tab4:
        mostrar_compostagem()

    with tab5:
        mostrar_quimica()

    with tab6:
        mostrar_coleta_seletiva()

    with tab7:
        mostrar_microplasticos()

    with tab8:
        mostrar_cooperativas()

    with tab9:
        st.header("📚 Atividades Pedagógicas")
        st.markdown("Sugestões de atividades educativas sobre resíduos e meio ambiente.")

    with tab10:
        st.header("ℹ️ Sobre o Projeto")
        st.markdown("""
**Glossário Interativo de Resíduos e Polímeros**  
- Desenvolvido para educação ambiental  
- Dados técnicos baseados em normas ABNT  More actions
- Integrado com atividades pedagógicas  
""")
        st.markdown("""
**Autor:** nome dos alunos e professora  
**Disciplina:** Prática de Ensino em Espaços de Divulgação Científica (Ext 18h-a)  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)
""")

# Execução do app
if __name__ == "__main__":
    os.makedirs(IMAGES_MATERIAIS_DIR, exist_ok=True)
    os.makedirs(IMAGES_RESIDUOS_DIR, exist_ok=True)
    main()
