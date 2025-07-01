import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
import re
import folium
import plotly.express as px
from streamlit_folium import folium_static
from datetime import datetime

st.set_page_config(layout="wide")

# Adicione o CSS para melhorar as abas
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        white-space: normal;
    }
</style>
""", unsafe_allow_html=True)

# Caminho correto para a pasta de imagens
IMAGES_MATERIAIS_DIR = "imagens_materiais"
IMAGES_RESIDUOS_DIR = "imagens_residuos"

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

# Função para carregar dados polimeros e residuos
@st.cache_data
def carregar_dados():
    polimeros = pd.read_csv("polimeros.csv", sep=";")
    residuos = pd.read_csv("residuos.csv", sep=";")  # Se tiver o arquivo resíduos na raiz também
    return polimeros, residuos

#função para carregar os dados da coleta seletiva
@st.cache_data
def load_coleta_data():
    try:
        url = "https://raw.githubusercontent.com/michaufsc/glossario-quimica-residuos/refs/heads/main/pontos_coleta.csv"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de coleta: {str(e)}")
        return pd.DataFrame()
        
#função dados quiz        
@st.cache_data
def load_quiz():
    try:
        # Verificação mais robusta do arquivo
        if not os.path.isfile("quiz_perguntas.csv"):
            st.error("Arquivo quiz_perguntas.csv não encontrado no diretório atual")
            return []

        # Tentativas de leitura mais organizadas
        read_attempts = [
            {"sep": ";", "encoding": "utf-8"},
            {"sep": ",", "encoding": "utf-8"}, 
            {"sep": ";", "encoding": "latin1"}
        ]
        
        df = None
        for attempt in read_attempts:
            try:
                df = pd.read_csv(
                    "quiz_perguntas.csv",
                    sep=attempt["sep"],
                    encoding=attempt["encoding"],
                    on_bad_lines='warn'
                )
                break
            except Exception as e:
                continue
                
        if df is None or df.empty:
            st.error("Não foi possível ler o arquivo ou o arquivo está vazio")
            return []

        # Limpeza e padronização mais eficiente
        df.columns = df.columns.str.strip().str.lower()
        
        # Mapeamento mais completo
        column_mapping = {
            'pergunta': ['pergunta', 'question', 'pregunta', 'enunciado'],
            'opcao_1': ['opcao_1', 'opção 1', 'option1', 'alternativa_a', 'a)'],
            'opcao_2': ['opcao_2', 'opção 2', 'option2', 'alternativa_b', 'b)'],
            'opcao_3': ['opcao_3', 'opção 3', 'option3', 'alternativa_c', 'c)'],
            'opcao_4': ['opcao_4', 'opção 4', 'option4', 'alternativa_d', 'd)'],
            'resposta': ['resposta', 'answer', 'correct', 'correta', 'gabarito'],
            'explicacao': ['explicacao', 'explicação', 'explanation', 'feedback']
        }

        # Renomeação mais segura
        renamed_cols = {}
        for standard_name, alternatives in column_mapping.items():
            for alt in alternatives:
                if alt in df.columns:
                    renamed_cols[alt] = standard_name
        df = df.rename(columns=renamed_cols)

        # Verificação de colunas obrigatórias mais clara
        required_cols = ['pergunta', 'opcao_1', 'opcao_2', 'opcao_3', 'opcao_4', 'resposta', 'explicacao']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            st.error(f"Colunas obrigatórias faltando: {', '.join(missing_cols)}")
            st.write("Colunas encontradas:", list(df.columns))
            return []

        # Processamento mais seguro das perguntas
        questions = []
        for _, row in df.iterrows():
            try:
                # Tratamento mais robusto da resposta
                resposta_str = str(row['resposta']).strip().upper()
                resposta_num = None
                
                # Aceita respostas como "1", "A", "a)", etc.
                if resposta_str in ['1', 'A', 'A)']:
                    resposta_num = 1
                elif resposta_str in ['2', 'B', 'B)']:
                    resposta_num = 2
                elif resposta_str in ['3', 'C', 'C)']:
                    resposta_num = 3
                elif resposta_str in ['4', 'D', 'D)']:
                    resposta_num = 4
                
                if resposta_num is None:
                    st.warning(f"Resposta inválida na pergunta: {row['pergunta']}")
                    continue
                    
                questions.append({
                    "pergunta": str(row['pergunta']).strip(),
                    "opcoes": [
                        str(row['opcao_1']).strip(),
                        str(row['opcao_2']).strip(),
                        str(row['opcao_3']).strip(),
                        str(row['opcao_4']).strip()
                    ],
                    "resposta": resposta_num - 1,  # Convertendo para índice 0-3
                    "explicacao": str(row['explicacao']).strip()
                })
            except Exception as e:
                st.warning(f"Erro ao processar linha: {str(e)}")
                continue
                
        if not questions:
            st.error("Nenhuma pergunta válida foi carregada")
            return []
            
        random.shuffle(questions)
        return questions
        
    except Exception as e:
        st.error(f"Falha crítica ao carregar quiz: {str(e)}")
        return []
#acessibilidade
def load_custom_css():
    """Carrega os estilos CSS personalizados"""
    st.markdown("""
    <style>
        /* Variáveis de cores */
        :root {
            --primary-color: #1e88e5;
            --secondary-color: #2e7d32;
            --error-color: #d32f2f;
        }
        
        /* Estilos gerais */
        body {
            color: #333333;
            line-height: 1.6;
        }
        
        /* Cabeçalhos */
        h1, h2, h3 {
            color: var(--primary-color) !important;
        }
        
        /* Botões */
        .stButton>button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
        }
        
        /* Abas */
        [data-baseweb="tab"] {
            padding: 10px 16px !important;
            margin: 0 4px !important;
            border-radius: 4px !important;
        }
        
        [data-baseweb="tab"][aria-selected="true"] {
            background-color: var(--primary-color) !important;
            color: white !important;
        }
        
        /* Melhorias de acessibilidade */
        [data-baseweb="input"]:focus,
        [data-baseweb="textarea"]:focus,
        [data-baseweb="select"]:focus {
            box-shadow: 0 0 0 2px var(--primary-color) !important;
        }
        
        /* Imagens */
        .stImage {
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
#dados esps isopor
@st.cache_data
def carregar_pontos_isopor():
    """Base de dados oficial dos PEVs de Isopor® em Florianópolis"""
    dados = {
        'Local': [
            'Centro - Hercílio Luz x Anita Garibaldi',
            'Centro - Praça dos Namorados',
            'Beira-Mar Norte - Mirante',
            'Parque São Jorge - Av. Gov. José Boabaid',
            'Trindade - Praça Gama Rosa',
            'Coqueiros - Centro de Saúde',
            'Estreito - Praça N.S. Fátima',
            'Santa Mônica - Av. Madre Benvenuta',
            'João Paulo - Praça Dr. Fausto Lobo',
            'Jurerê Internacional - Final Av. dos Búzios'
        ],
        'Endereço': [
            'Rua Hercílio Luz, 60 (esquina com Anita Garibaldi)',
            'Largo São Sebastião, Centro',
            'Avenida Beira-Mar Norte, 1030 (Mirante)',
            'Avenida Governador José Boabaid, 250',
            'Rua Gama Rosa, Trindade',
            'Rua General Bittencourt, 175 (frente ao Centro de Saúde)',
            'Rua Henrique Meyer, 550 (Praça N.S. Fátima)',
            'Avenida Madre Benvenuta, 1580 (ao lado posto policial)',
            'Rodovia João Paulo, 5000 (Praça Dr. Fausto Lobo)',
            'Avenida dos Búzios, 1500 (junto ao PEV de Vidro)'
        ],
        'Latitude': [
            -27.5945, -27.5918, -27.5872,
            -27.5701, -27.5867, -27.5728,
            -27.6003, -27.5824, -27.5603,
            -27.4245
        ],
        'Longitude': [
            -48.5482, -48.5495, -48.5581,
            -48.5268, -48.5214, -48.5472,
            -48.5330, -48.5008, -48.5067,
            -48.4221
        ],
        'Horário': [
            '24 horas', '24 horas', '24 horas',
            '24 horas', '24 horas', '24 horas',
            '24 horas', '24 horas', '24 horas',
            '24 horas'
        ]
    }
    return pd.DataFrame(dados)
        
# Adicione esta função para carregar os dados das cooperativas
@st.cache_data
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

        st.divider()
def mostrar_glossario_residuos(residuos: pd.DataFrame):
    st.header("♻️ Glossário Completo de Resíduos")
    
    # Verifica se o DataFrame está vazio
    if residuos.empty:
        st.warning("Nenhum dado de resíduos disponível.")
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
    
    # Inicializa o estado do quiz se necessário
    if 'quiz_data' not in st.session_state:
        questions = load_quiz()
        if not questions:
            st.error("Não foi possível carregar as perguntas do quiz.")
            return
        st.session_state.quiz_data = {
            'questions': questions,
            'current_question': 0,
            'score': 0,
            'user_answer': None,
            'show_feedback': False
        }
    
    quiz_data = st.session_state.quiz_data
    
    # Se o quiz foi completado, mostra resultados
    if quiz_data['current_question'] >= len(quiz_data['questions']):
        mostrar_resultado_final(quiz_data['score'], len(quiz_data['questions']))
        return
    
    # Obtém a pergunta atual
    question = quiz_data['questions'][quiz_data['current_question']]
    
    # Mostra progresso
    st.progress((quiz_data['current_question'] + 1) / len(quiz_data['questions']))
    st.caption(f"Pergunta {quiz_data['current_question'] + 1} de {len(quiz_data['questions'])}")
    
    # Mostra pergunta
    st.subheader(question['pergunta'])
    
    # Mostra opções
    options = question['opcoes']
    user_answer = st.radio(
        "Selecione sua resposta:",
        options,
        index=None,
        key=f"question_{quiz_data['current_question']}"
    )
    
    # Botão para enviar resposta
    if st.button("Enviar resposta") and user_answer is not None:
        quiz_data['user_answer'] = options.index(user_answer)
        quiz_data['show_feedback'] = True
        
        # Verifica resposta
        if quiz_data['user_answer'] == question['resposta']:
            quiz_data['score'] += 1
        
        st.session_state.quiz_data = quiz_data
        st.rerun()
    
    # Mostra feedback após resposta
    if quiz_data['show_feedback']:
        if quiz_data['user_answer'] == question['resposta']:
            st.success(f"✅ Correto! {question['explicacao']}")
        else:
            correct_answer = options[question['resposta']]
            st.error(f"❌ Resposta incorreta. A resposta correta é: {correct_answer}. {question['explicacao']}")
        
        # Botão para próxima pergunta
        if st.button("Próxima pergunta"):
            quiz_data['current_question'] += 1
            quiz_data['show_feedback'] = False
            quiz_data['user_answer'] = None
            st.session_state.quiz_data = quiz_data
            st.rerun()

def mostrar_resultado_final(score, total_questions):
    st.balloons()
    st.success(f"## 🎯 Pontuação Final: {score}/{total_questions} ({(score/total_questions):.0%})")
    
    # Feedback personalizado
    if score == total_questions:
        st.info("### 🌟 Excelente! Você é um expert em reciclagem!")
    elif score >= total_questions * 0.75:
        st.info("### 👏 Muito bom! Seu conhecimento sobre o tema é ótimo!")
    elif score >= total_questions * 0.5:
        st.warning("### 📚 Bom trabalho! Você está no caminho certo!")
    else:
        st.error("### 📖 Continue estudando! Visite o glossário para aprender mais.")
    
    # Botão para reiniciar
    if st.button("🔄 Refazer Quiz"):
        del st.session_state.quiz_data
        st.rerun()

# Função: história do Museu
def mostrar_historia():
    st.empty()  # Limpa qualquer conteúdo residual
    st.header("🏛️ Museu do Lixo – História e Agenda")

    # Introdução
    st.markdown("""
    O **Museu do Lixo**, instalado pela Comcap em **25 de setembro de 2003**, tornou-se uma referência em **educação ambiental** em Santa Catarina. 
    Sua abordagem lúdica e acessível reforça conceitos de **consumo consciente** com base nos princípios:
    """)

    # Seção dos 4Rs – versão didática sem HTML
    st.subheader("♻️ Os 4Rs da Sustentabilidade")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔍 1. REPENSAR")
        st.success("Questionar nossos hábitos:\n\n*“Preciso mesmo disso?”*")

        st.markdown("### 🔄 3. REUTILIZAR")
        st.warning("Dar novos usos antes de descartar.")

    with col2:
        st.markdown("### 📉 2. REDUZIR")
        st.success("Diminuir a quantidade de resíduos gerados.")

        st.markdown("### ♻ 4. RECICLAR")
        st.info("Transformar materiais usados em novos produtos.")

    # Texto da história do museu
    st.markdown("""
    O museu nasceu do sonho de mais de dez anos de trabalhadores da Comcap, que desejavam **resgatar objetos descartados** 
    para criar um espaço de memória sobre os hábitos de consumo da sociedade.

    As primeiras peças foram reunidas no antigo galpão de triagem da coleta seletiva. Atualmente, o acervo está disposto em 
    **ambientes temáticos**, montados e decorados com **materiais reaproveitados** — desde as tintas das paredes até a mandala 
    do piso, tudo feito com resíduos reciclados.

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

    ### 🔍 Saiba mais
    - O museu integra o roteiro de **visitação monitorada ao Centro de Valorização de Resíduos (CVR)** da Comcap  
    - Recebe cerca de **7 mil visitantes por ano**  
    - Acervo com **10 mil itens** recuperados  
    - Área de **200 m²** com decoração 100% reutilizada  
    - Personagens educativos como **Neiciclagem** e **Dona Tainha**
    """)

    # Galeria de imagens
    st.markdown("---")
    st.subheader("📸 Conheça Nossa Estrutura")

    col1, col2 = st.columns(2)

    # Imagem 1 - Fachada
    with col1:
        try:
            img_path = os.path.join("imagens_materiais", "museuext.png")
            if os.path.exists(img_path):
                st.image(img_path, caption="Vista externa do Museu", use_container_width=True)
            else:
                raise FileNotFoundError
        except Exception:
            st.warning("Imagem da fachada não encontrada")
            placeholder = Image.new('RGB', (600, 400), color=(220, 220, 220))
            st.image(placeholder, caption="Fachada do Museu (imagem não disponível)", use_container_width=True)

    # Imagem 2 - Equipe
    with col2:
        try:
            img_path = os.path.join("imagens_materiais", "museuint.png")
            if os.path.exists(img_path):
                st.image(img_path, caption="Nossa equipe de educadores", use_container_width=True)
            else:
                raise FileNotFoundError
        except Exception:
            st.warning("Imagem da equipe não encontrada")
            placeholder = Image.new('RGB', (600, 400), color=(220, 220, 220))
            st.image(placeholder, caption="Equipe do museu (imagem não disponível)", use_container_width=True)

    # Rodapé institucional (ajustado para celular)
    st.markdown("### ℹ️ Agendamentos")
    st.markdown("""
📧 [ambiental.comcap@pmf.sc.gov.br](mailto:ambiental.comcap@pmf.sc.gov.br)  
📞 (48) 3261-4808
""")
    
def mostrar_quimica():
    # Definição das cores de fallback
    COR_MATERIAIS = (220, 220, 255)  # Azul claro
    COR_RESIDUOS = (200, 230, 200)   # Verde claro

    st.markdown("""
    ## 🔬 Polímeros: Estrutura, Propriedades e Sustentabilidade

    Os **polímeros** são macromoléculas formadas pela repetição de unidades estruturais menores chamadas **monômeros**, unidas por ligações covalentes. Essa repetição pode ocorrer centenas ou milhares de vezes, conferindo propriedades únicas como elasticidade, resistência térmica e mecânica.

    ### Classificação dos Polímeros

    Podemos classificar os polímeros em:

    - **Naturais**: celulose (paredes celulares vegetais), amido (reserva energética), proteínas (colágeno, seda), látex (borracha natural)
    - **Sintéticos**: PET (garrafas), PE e PP (embalagens), PVC (tubos), PS (isopor), Nylon (tecidos), PLA (bioplásticos)

    Quanto ao comportamento térmico:
    - **Termoplásticos**: Podem ser remodelados (PET, PE, PP)
    - **Termofixos**: Mantêm forma após moldagem (borracha vulcanizada)

    Estruturalmente:
    - **Lineares**: Flexíveis (PE)
    - **Ramificados**: Menor densidade (LDPE)
    - **Reticulados**: Alta rigidez (borracha vulcanizada)

    ### Propriedades dos Principais Polímeros Sintéticos

    - **PET (♳)**: Ponto de fusão 260-265°C, densidade 1.38-1.39 g/cm³, resistência 55-75 MPa
    - **PEAD (♴)**: Fusão 130-137°C, densidade 0.94-0.96 g/cm³, resistência 20-32 MPa
    - **PVC (♵)**: Fusão 100-260°C, libera HCl no processamento
    - **PP (♷)**: Fusão 160-165°C, resistência 30-40 MPa
    - **PS (♸)**: Fusão 240°C, baixa reciclabilidade

    ### Reciclagem e Sustentabilidade

    No Brasil:
    - PET: 55% de reciclagem
    - PEAD: 30%
    - PVC: <5%
    - Embalagens multicamadas: difíceis de reciclar

    Processo de reciclagem:
    - Temperaturas: PET 270-290°C, PP 200-230°C
    - Consumo: ~10L água/kg plástico
    - Eficiência: 30-50% melhor que produção virgem

    **Inovações:**
    1. Biopolímeros (PLA, PHA)
    2. Reciclagem química avançada
    3. Catalisadores enzimáticos
    4. IA para triagem automatizada

    **Boas Práticas:**
    - Indústria: Design ecológico, logística reversa
    - Sociedade: Separação adequada, redução de descartáveis, apoio a cooperativas

    **Referências:**
    - ATKINS, P.; JONES, L. Princípios de Química. 5.ed. Bookman, 2012.
    - CALLISTER, W. D. Fundamentos da Ciência dos Materiais. 9.ed. LTC, 2020.
    - MANO, E. B. Introdução a Polímeros. 4.ed. Edgard Blücher, 2005.
    """)

    # Adicionar imagens
    mostrar_imagem_com_fallback("polo.png", IMAGES_MATERIAIS_DIR,
                                "Estrutura molecular de polímeros", COR_MATERIAIS)
    mostrar_imagem_com_fallback("tipos2.png", IMAGES_MATERIAIS_DIR,
                                "Aplicações dos polímeros", COR_MATERIAIS)

def mostrar_isopor():
    st.header("♻️ Projeto Recicla+EPS - Florianópolis")
    
    # Texto técnico sobre EPS
    st.markdown("""
    ### Poliestireno Expandido (EPS): O Material Versátil

    O EPS, conhecido popularmente como isopor, é um plástico celular rígido composto por 98% de ar e apenas 2% de matéria-prima plástica. Sua estrutura única de células fechadas lhe confere propriedades excepcionais que o tornam indispensável em diversas aplicações.

    Do ponto de vista químico, o EPS é um polímero termoplástico derivado do estireno. Suas características técnicas incluem:

    - **Excelente isolamento térmico**: condutividade entre 0,031-0,038 W/mK
    - **Baixa absorção de água**: menos de 1% em 24 horas
    - **Resistência mecânica**: proporcional à sua densidade (10-30 kg/m³)
    - **Ampla faixa térmica**: opera entre -40°C a +70°C
    - **Vida útil prolongada**: mais de 50 anos em aplicações estáticas

    **Principais aplicações industriais:**
    - Embalagens protetoras para produtos eletrônicos e eletrodomésticos
    - Isolamento térmico em construções civis
    - Componentes para refrigeração industrial
    - Moldes para fundição
    - Elementos flutuantes

    **Aspectos ambientais:**
    - 100% reciclável (mecânica e quimicamente)
    - Baixo consumo energético na produção moderna
    - Programas eficientes de logística reversa implementados

    *Observação*: "Isopor" é uma marca registrada que se tornou sinônimo de EPS no Brasil, representando produtos de alta qualidade nesta categoria de materiais.
    """)
    
    # Mostra a imagem local eps.png
    eps_path = os.path.join(IMAGES_RESIDUOS_DIR, "isopor.png")
    try:
        st.image(
            eps_path,
            caption="Diagrama do processo de reciclagem mecânica de EPS - Projeto Recicla+EPS",
            use_container_width=True
        )
    except FileNotFoundError:
        placeholder = Image.new('RGB', (800, 400), color=(200, 230, 200))
        st.image(
            placeholder,
            caption="Diagrama ilustrativo do processo de reciclagem",
            use_container_width=True
        )
    
    # Dicas de descarte
    st.subheader("📦 Como Preparar seu Isopor® para a reciclagem:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **✅ Faça assim:**  
        • Limpe restos de alimentos  
        • Não precisa lavar (apenas remover resíduos)  
        • Deixe secar naturalmente  
        """)
    with col2:
        st.markdown("""
        **🚫 Evite:**  
        • Isopor com gordura ou sujeira  
        • Embalagens contaminadas  
        • Descartar no lixo comum  
        """)

    # Benefícios do projeto
    st.subheader("🌱 Por que descartar corretamente?")
    st.markdown("""
    - Transforma-se em novos produtos (réguas, rodapés, placas)  
    - Gera renda para cooperativas de reciclagem  
    - Florianópolis recicla **10 toneladas/mês** de Isopor®  
    - Reduz a poluição ambiental  
    """)
 # Mostra a imagem local eps.png
    eps_path = os.path.join(IMAGES_RESIDUOS_DIR, "eps.png")
    try:
        st.image(
            eps_path,
            caption="O EPS é amplamente utilizado em nossa sociedade",
            use_container_width=True
        )
    except FileNotFoundError:
        placeholder = Image.new('RGB', (800, 400), color=(200, 230, 200))
        st.image(
            placeholder,
            caption="Diagrama ilustrativo do processo de reciclagem",
            use_container_width=True
        )
    # Título geral da seção de reciclagem
    st.header("♻️ A Reciclagem do Isopor®")

    # Etapas da reciclagem
    st.subheader("🔄 Como o Isopor® é Reciclado: Passo a Passo")
    st.markdown("""
    **1. Coleta**  
    O isopor limpo é recolhido por cooperativas ou coleta seletiva.  

    **2. Triagem**  
    É separado de outros resíduos nas centrais de triagem.  

    **3. Trituração**  
    O material é quebrado em pequenos pedaços para facilitar o processamento.  

    **4. Compactação**  
    Os flocos podem ser compactados em blocos (lingotes), reduzindo o volume.  

    **5. Extrusão**  
    É derretido e transformado em grânulos de poliestireno reciclado.  

    **6. Reutilização**  
    Os grânulos são usados para fabricar novos produtos: molduras, vasos, peças de construção etc.  
    """)

    st.subheader("📍 Lista Completa dos Pontos de Entrega Voluntária (PEVs)")

# Dados dos pontos
pontos_df = pd.DataFrame({
    'Local': [
        'Centro - Hercílio Luz x Anita Garibaldi',
        'Centro - Praça dos Namorados',
        'Beira-Mar - Mirante',
        'Parque São Jorge',
        'Trindade - Praça Gama Rosa',
        'Coqueiros - Centro de Saúde',
        'Estreito - Praça N.S. Fátima',
        'Santa Mônica',
        'João Paulo',
        'Jurerê Internacional'
    ],
    'Endereço': [
        'Hercílio Luz esquina com Anita Garibaldi',
        'Praça dos Namorados, Largo São Sebastião',
        'Av. Beira-Mar Norte (Mirante)',
        'Av. Gov. José Boabaid',
        'Praça da Rua Gama Rosa',
        'Em frente ao Centro de Saúde de Coqueiros',
        'Praça Nossa Senhora de Fátima',
        'Av. Madre Benvenuta (posto policial)',
        'Rodovia João Paulo, Praça Dr. Fausto Lobo',
        'Final da Av. dos Búzios (junto ao PEV de Vidro)'
    ],
    'Link': [
        'https://maps.app.goo.gl/1',
        'https://maps.app.goo.gl/2',
        'https://maps.app.goo.gl/3',
        'https://maps.app.goo.gl/4',
        'https://maps.app.goo.gl/5',
        'https://maps.app.goo.gl/6',
        'https://maps.app.goo.gl/7',
        'https://maps.app.goo.gl/8',
        'https://maps.app.goo.gl/9',
        'https://maps.app.goo.gl/10'
    ],
    'lat': [
        -27.5945, -27.5918, -27.5872,
        -27.5701, -27.5867, -27.5728,
        -27.6003, -27.5824, -27.5603,
        -27.4245
    ],
    'lon': [
        -48.5482, -48.5495, -48.5581,
        -48.5268, -48.5214, -48.5472,
        -48.5330, -48.5008, -48.5067,
        -48.4221
    ]
})

# Mostrar lista com separador
for _, row in pontos_df.iterrows():
    st.markdown(f"""
**{row['Local']}**  
📍 {row['Endereço']}  
🔗 [Abrir no Google Maps]({row['Link']})  
---  
""")

# Exibir mapa após os pontos
st.subheader("🗺️ Visualize no Mapa Interativo")
st.map(pontos_df, use_container_width=True)

# Rodapé
st.markdown("""
📌 **Fonte:** Prefeitura de Florianópolis – [Recicla+EPS](https://www.pmf.sc.gov.br)  
📞 **Dúvidas:** Secretaria de Meio Ambiente – (48) 3212-1650  
🕒 **Funcionamento:** Todos os pontos abertos 24h  
""")

# Função: compostagem

def mostrar_compostagem():
    st.header("🌱 Compostagem como Método Adequado ao Tratamento de Resíduos Sólidos Orgânicos Urbanos")

    with st.expander("📌 Resumo", expanded=True):
        st.markdown("""
        A compostagem da fração orgânica dos resíduos sólidos urbanos é uma solução eficiente, econômica e sustentável, 
        alinhada à Política Nacional de Resíduos Sólidos (Lei 12.305/2010). Em Florianópolis, o método de **leira estática 
        com aeração passiva** (Método UFSC) tem demonstrado excelentes resultados, processando cerca de **2 mil toneladas/ano** 
        de matéria orgânica e gerando composto de alta qualidade para uso em hortas escolares e ajardinamento público.
        """)

    st.subheader("✅ Benefícios da Compostagem")
    st.markdown("""
    - **Redução de custos**: Economia de R$ 100 mil/ano comparado ao aterro sanitário
    - **Qualidade do composto**: Rico em nutrientes (carbono, nitrogênio, fósforo) e livre de patógenos
    - **Sustentabilidade**: Fecha o ciclo dos resíduos, evitando aterrar recursos naturais
    - **Educação ambiental**: Promove conscientização e participação comunitária
    """)

    st.subheader("🧪 Método UFSC de Compostagem Termofílica")
    st.markdown("""
    Desenvolvido pelo **professor Paul Richard Momsen Miller (UFSC)**, o método utiliza:
    - **Leiras estáticas** (2,5m x 35m x 2m) com camadas de resíduos úmidos (restos de alimentos) e secos (podas trituradas)
    - **Aeração passiva**: Sem revolvimento mecânico, apenas ventilação natural
    - **Fases do processo**:
      1. **Termofílica** (45-75°C): Elimina patógenos e acelera decomposição
      2. **Maturação** (120 dias): Produz húmus estável e biofertilizante líquido
    """)

    # Container para as imagens lado a lado
    col1, col2 = st.columns(2)
    with col1:
        st.image("imagens_residuos/leira.png", 
                caption="Modelo de leira estática com cobertura vegetal",
                use_container_width=True)
    with col2:
        st.image("imagens_residuos/metodo_ufsc.png", 
                caption="Etapas do processo de compostagem – Método UFSC",
                use_container_width=True)

    st.markdown("""
    **Locais de aplicação em Florianópolis:**
    - Campus da UFSC (Pátio de Compostagem)
    - SESC Cacupé
    - Fundação Serte
    - Hortas escolares e comunitárias
    - Projetos da COMCAP em parceria com a sociedade civil
    """)

    st.subheader("📊 Dados Relevantes")
    
    with st.expander("Composição dos Resíduos no Brasil (ABRELPE, 2012)"):
        st.table({
            "Material": ["Matéria Orgânica", "Plásticos", "Papel/Papelão", "Outros"],
            "Participação (%)": ["51,4", "13,5", "13,1", "22,0"]
        })
    
    st.markdown("""
    **Florianópolis (2013):**
    - 11.755 toneladas/ano coletadas seletivamente (7% do total)
    - 70 mil toneladas/ano de resíduos orgânicos potencialmente compostáveis
    """)

    st.subheader("💡 Como Implementar na Sua Cidade?")
    st.markdown("""
    1. **Segregação na fonte**: Separação doméstica de orgânicos
    2. **Coleta especializada**: Transporte dedicado para resíduos compostáveis
    3. **Pátios de compostagem**: Estruturas simples com leiras estáticas
    4. **Parcerias**: Envolvimento de universidades, ONGs e cooperativas
    """)

    st.subheader("📚 Materiais Complementares")
    st.markdown("""
    - [📘 Manual de Compostagem Doméstica](https://cepagroagroecologia.wordpress.com/minhoca-na-cabeca/) - Cepagro
    - [📗 Compostagem Comunitária: Passo a Passo](https://compostagemcomunitaria.com.br)
    - [🎥 Vídeo Educativo: Método UFSC](https://www.youtube.com)
    - [📄 Política Nacional de Resíduos Sólidos](http://www.planalto.gov.br/ccivil_03/_ato2007-2010/2010/lei/l12305.htm)
    """)

    st.markdown("---")
    st.markdown("""
    *"Compostar é transformar lixo em vida, fechando o ciclo da natureza na cidade."*
    """)
    st.markdown("✂️ **Dica prática**: Use serragem ou podas trituradas para equilibrar a umidade nas leiras!")

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
    ### 🔎 O que são microplásticos?

    Microplásticos são fragmentos de plástico com menos de 5 milímetros, muitas vezes invisíveis a olho nu.

    Eles se dividem em dois tipos:

    - **Primários**: fabricados intencionalmente nesse tamanho, como microesferas usadas em cosméticos, pastas de dente e produtos de limpeza.
    - **Secundários**: formados pela fragmentação de plásticos maiores devido ao sol, chuva, vento, ondas e ação de organismos.
    """)

    mostrar_imagem_com_fallback("micro.png", IMAGES_MATERIAIS_DIR,
                              "Tipos e fontes de microplásticos no ambiente marinho", 
                              (200, 230, 200))

    st.markdown("""
    ### 🌊 Impacto Ambiental

    Esses fragmentos acabam nos oceanos e podem permanecer por décadas no ambiente, acumulando-se em:
    - Praias e costas marinhas
    - Sedimentos oceânicos
    - Corpos de organismos marinhos
    - Até na água potável

    ### 🔬 O Papel da Química

    A Química nos permite detectar, identificar e compreender os efeitos dos microplásticos:
    1. Análise espectroscópica (FTIR, Raman)
    2. Cromatografia (GC-MS)
    3. Técnicas de microscopia avançada

    ---

    ### 🐠 Impactos nos oceanos e na vida marinha

    Animais marinhos frequentemente ingerem microplásticos por engano, levando a:

    - Dificuldade de digestão e absorção de nutrientes;
    - Inflamações e bloqueios intestinais;
    - Acúmulo de substâncias tóxicas nos tecidos.

     Os efeitos não param por aí: os microplásticos **sobem na cadeia alimentar**, chegando até peixes e frutos do mar consumidos por humanos - um risco silencioso, mas real.
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
    3. ISO/TR 21960:2020. *Plastics Environmental aspects State of knowledge and methodologies*.
    4. Browne, M. A. et al. (2011). *Accumulation of microplastic on shorelines worldwide: sources and sinks*. **Environmental Science & Technology**.
    5. NOAA  National Oceanic and Atmospheric Administration (2009). *Microplastics Program Overview*.
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
        
def mostrar_plastico_oceanos():
    st.header("🌊 Microplásticos no Litoral Catarinense")
    st.markdown("""
    **Dados científicos simplificados para conscientização**  
    *Fontes: UFSC, UNIVALI e estudos internacionais*
    """)
    
    # Abas para cada estudo
    tab1, tab2 = st.tabs(["📊 Dados Locais", "📚 Estudos Científicos"])
    
    with tab1:
        st.subheader("Principais Descobertas em SC")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Praia do Campeche", "127 partículas/m³")
            st.metric("Praia Mole", "15 partículas/g de sedimento")
        
        
        with col2:
            st.metric("Baía Norte", "28 partículas/g de sedimento")
            st.metric("Jurerê", "89 partículas/m³")
            st.progress(78, text="Sedimentos contaminados em SC")

    with tab2:
        st.subheader("Estudos de Referência")
        
        with st.expander("🔍 Persistência nos Sedimentos (Gonçalves et al., 2024)"):
            st.markdown("""
            - **Amostras:** Sedimentos de 10 praias catarinenses  
            - **Método:** Espectroscopia FTIR  
            - **Resultados:**  
              • Até 700 anos de persistência  
              • 92% dos sedimentos contaminados  
            - [Artigo completo](https://doi.org/10.1016/j.scitotenv.2023.169243)
            """)
        
        with st.expander("📰 Fontes dos Microplásticos (UFSC/G1, 2024)"):
            st.markdown("""
            - **Principais origens:**  
              1. Esgoto (32%)  
              2. Turismo (28%)  
              3. Pesca (23%)  
            - **Solução:** Filtros em máquinas de lavar reduzem 87% das microfibras
            """)

    st.markdown("---")
    st.markdown("""
    ### 💡 Como ajudar?
    1. Reduza plásticos descartáveis
    2. Participe de mutirões de limpeza
    3. Compartilhe estes dados
    """)
# Função principal
def main():
     # Carrega CSS primeiro
    load_custom_css()
    
    st.header("Museu do Lixo ♻️ COMCAP Florianópolis")
    st.subheader("Aplicativo para educação ambiental")
    st.subheader("Oceano de Plásticos")
    st.markdown("*Desenvolvido durante a disciplina de Prática de Ensino em Espaços de Divulgação Científica (Ext 18h)*")
    st.markdown("Curso de Graduação em Química")
    st.markdown("Universidade Federal de Santa Catarina (UFSC)")
    
    polimeros, residuos = carregar_dados()
    
    # Controle de abas (agora com 12 abas)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs([
        "🏛️ História", 
        "🧪 Química",
        "🏷️ Plásticos",
        "🧵 Microplásticos",
        "📦 Isopor",
        "🌊 Oceanos",
        "🏘️ Coleta",
        "🤝 Cooperativas",
        "🌱 Compostagem",
        "🧐 Quiz",
        "📚 Atividades",
        "ℹ️ Sobre"
    ])

    with tab1:
        mostrar_historia()
        
    with tab2:
        mostrar_quimica()

    with tab3:
        mostrar_glossario_polimeros(polimeros)

    with tab4:
        mostrar_microplasticos()
        
    with tab5:
        mostrar_isopor()
        
    with tab6:
        mostrar_plastico_oceanos()
   
    with tab7:
        mostrar_coleta_seletiva()
        
    with tab8:
        mostrar_cooperativas()
        
    with tab9:
        mostrar_compostagem()
        
    with tab10:
        mostrar_quiz()
        
    with tab11:
        st.header("📚 Atividades Pedagógicas")
        st.markdown("Sugestões de atividades educativas sobre resíduos e meio ambiente.")

    with tab12:
        st.header("ℹ️ Sobre o Projeto")
        st.markdown("""
        **Glossário Interativo de Resíduos e Polímeros**  
        - Desenvolvido para educação ambiental  
        - Dados técnicos baseados em normas ABNT  
        - Integrado com atividades pedagógicas  
        """)
        # ... (mantenha o restante do conteúdo da aba Sobre)

if __name__ == "__main__":
    os.makedirs(IMAGES_MATERIAIS_DIR, exist_ok=True)
    os.makedirs(IMAGES_RESIDUOS_DIR, exist_ok=True)
    main()
