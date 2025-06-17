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
    if 'questions' not in st.session_state:
        questions = load_quiz()
        if not questions:
            st.error("Não foi possível carregar as perguntas do quiz. Verifique o arquivo quiz_perguntas.csv")
            return
        st.session_state.update({
            'questions': questions,
            'current_question': 0,
            'score': 0,
            'quiz_complete': False
        })
    
    # Se o quiz foi completado, mostra resultados
    if st.session_state.get('quiz_complete', False):
        mostrar_resultado_final()
        return
    
    # Obtém a pergunta atual
    question = st.session_state.questions[st.session_state.current_question]
    
    # Mostra progresso e pergunta
    mostrar_barra_progresso()
    mostrar_pergunta(question)
    
    # Processa resposta do usuário
    processar_resposta(question)

def mostrar_barra_progresso():
    progresso = (st.session_state.current_question + 1) / len(st.session_state.questions)
    st.progress(progresso)
    st.caption(f"Progresso: {st.session_state.current_question + 1} de {len(st.session_state.questions)} perguntas")

def mostrar_pergunta(question):
    st.subheader(f"Pergunta {st.session_state.current_question + 1} de {len(st.session_state.questions)}")
    st.markdown(f"**{question['pergunta']}**")
    
    # Mostra opções como botões para melhor usabilidade
    for i, opcao in enumerate(question['opcoes']):
        if st.button(opcao, key=f"op_{st.session_state.current_question}_{i}"):
            st.session_state.selected_option = i
            verificar_resposta(question, i)

def processar_resposta(question):
    if 'selected_option' in st.session_state:
        # Mostra feedback
        if st.session_state.selected_option == question['resposta'] - 1:  # -1 porque as opções são 1-4
            st.success(f"✅ Correto! {question['explicacao']}")
            st.session_state.score += 1
        else:
            resposta_correta = question['opcoes'][question['resposta'] - 1]
            st.error(f"❌ Errado. A resposta correta é: {resposta_correta}. {question['explicacao']}")
        
        # Botão para próxima pergunta
        if st.button("➡️ Próxima pergunta", type="primary"):
            avancar_quiz()

def verificar_resposta(question, selected_index):
    st.session_state.resposta_verificada = True
    if selected_index == question['resposta'] - 1:
        st.session_state.score += 1

def avancar_quiz():
    st.session_state.current_question += 1
    if st.session_state.current_question >= len(st.session_state.questions):
        st.session_state.quiz_complete = True
    else:
        # Limpa estado para próxima pergunta
        if 'selected_option' in st.session_state:
            del st.session_state.selected_option
        if 'resposta_verificada' in st.session_state:
            del st.session_state.resposta_verificada
    st.rerun()

def mostrar_resultado_final():
    score = st.session_state.score
    total = len(st.session_state.questions)
    percentual = score / total
    
    st.balloons()
    st.success(f"## 🎯 Pontuação Final: {score}/{total} ({percentual:.0%})")
    
    # Feedback personalizado
    if percentual == 1:
        st.info("""
        ### 🌟 Excelente! Você é um expert em reciclagem!
        *Parabéns! Seu conhecimento sobre resíduos e sustentabilidade é impressionante.*
        """)
    elif percentual >= 0.75:
        st.info("""
        ### 👏 Muito bom!
        *Você tem um ótimo entendimento do assunto! Continue aprendendo.*
        """)
    elif percentual >= 0.5:
        st.warning("""
        ### 📚 Bom trabalho!
        *Você está no caminho certo, mas pode melhorar ainda mais!*
        """)
    else:
        st.error("""
        ### 📖 Continue estudando!
        *Visite o glossário para melhorar seu conhecimento sobre reciclagem.*
        """)
    
    # Botão para reiniciar
    if st.button("🔄 Refazer Quiz", type="primary"):
        resetar_quiz()
        st.rerun()

def resetar_quiz():
    # Limpa todo o estado relacionado ao quiz
    for key in list(st.session_state.keys()):
        if key.startswith(('q', 'b', 'respondido', 'correta', 'selected', 'resposta')):
            del st.session_state[key]
    del st.session_state.questions
    del st.session_state.current_question
    del st.session_state.score
    del st.session_state.quiz_complete


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
    st.header("🧪 Ciência dos Polímeros e Sustentabilidade")

    # Função robusta para carregar imagens
    def carregar_imagem(nome_arquivo):
        try:
            # Verifica todos os possíveis caminhos
            caminhos_teste = [
                os.path.join("imagens_residuos", nome_arquivo),
                os.path.join("app/imagens_residuos", nome_arquivo),
                os.path.join("/mount/src/glossario-quimica-residuos/imagens_residuos", nome_arquivo),
                nome_arquivo  # Tenta no diretório atual como último recurso
            ]
            
            for caminho in caminhos_teste:
                if os.path.exists(caminho):
                    return Image.open(caminho)
            
            raise FileNotFoundError(f"Imagem não encontrada em nenhum dos caminhos testados: {nome_arquivo}")
        except Exception as e:
            st.error(f"Erro ao carregar imagem {nome_arquivo}: {str(e)}")
            return None

    # Seção 1: Conceitos Fundamentais
    st.markdown("""
    ## 🔬 O que são Polímeros?
    Macromoléculas formadas por unidades repetitivas (**monômeros**) com cadeias:
    - **Lineares** (ex: PE) - Flexíveis e moldáveis
    - **Ramificadas** (ex: LDPE) - Menor densidade
    - **Reticuladas** (ex: Borracha vulcanizada) - Alta rigidez
    """)
    
    polo_img = carregar_imagem("polo.png")
    if polo_img:
        st.image(polo_img, use_container_width=True, 
                caption="Estrutura molecular de polímeros sintéticos típicos")

    # Seção 2: Classificação
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🌱 Polímeros Naturais
        - Celulose (paredes celulares)
        - Amido (reserva energética)
        - Quitina (exoesqueletos)
        - Proteínas (colágeno, seda)
        - Látex (borracha natural)
        """)
    
    with col2:
        st.markdown("""
        ### 🏭 Polímeros Sintéticos
        - PET (garrafas)
        - PE/PP (embalagens)
        - PVC (tubos)
        - PS (isopor)
        - Nylon (têxteis)
        - PLA (bioplástico)
        """)

    tipos_img = carregar_imagem("tipos.png")
    if tipos_img:
        st.image(tipos_img, use_container_width=True,
                caption="Aplicações comerciais dos principais polímeros")

    # Seção 3: Gestão de Resíduos
    st.markdown("""
    ---
    ## ♻️ Ciclo de Vida e Reciclagem
    """)

    tab1, tab2, tab3 = st.tabs(["Composição", "Processos", "Inovações"])

    with tab1:
        reci_img = carregar_imagem("reci.png")
        if reci_img:
            st.image(reci_img, use_container_width=True,
                    caption="Distribuição dos polímeros em resíduos urbanos")
        st.markdown("""
        **Dados de Reciclagem (Brasil):**
        - PET: 55% (líder em reciclagem)
        - PEAD: 30% 
        - PVC: <5% (problema crítico)
        - Embalagens multicamadas: virtualmente irrecicláveis
        """)

    with tab2:
        mec_img = carregar_imagem("mec.png")
        if mec_img:
            st.image(mec_img, use_container_width=True,
                    caption="Fluxograma de reciclagem mecânica")
        st.markdown("""
        **Parâmetros Operacionais:**
        - Temperatura de extrusão:
          - PET: 270-290°C
          - PP: 200-230°C
        - Consumo hídrico: 10L/kg de plástico
        - Eficiência energética: 30-50% vs produção virgem
        """)

    with tab3:
        ciclo_img = carregar_imagem("ciclo_vida.png")
        if ciclo_img:
            st.image(ciclo_img, use_container_width=True,
                    caption="Tecnologias emergentes no ciclo de vida")
        st.markdown("""
        **Tendências:**
        1. Biopolímeros (PLA, PHA)
        2. Reciclagem química avançada
        3. Catalisadores enzimáticos
        4. Sistemas IA para triagem
        """)

    # Seção 4: Tabelas Comparativas
    st.markdown("""
    ---
    ## 📊 Propriedades Comparativas
    """)

    st.markdown("""
    ### Termoplásticos vs Termorrígidos
    | Propriedade       | Termoplásticos (ex: PET) | Termorrígidos (ex: Baquelite) |
    |-------------------|--------------------------|-------------------------------|
    | Moldagem          | Reciclável               | Não reciclável               |
    | Resistência       | Média-Alta               | Muito Alta                   |
    | Aplicação         | Embalagens               | Componentes elétricos        |
    """)

    st.markdown("""
    ### Biopolímeros vs Convencionais
    | Critério          | PLA              | PET              |
    |-------------------|------------------|------------------|
    | Matéria-prima     | Milho/Cana       | Petróleo         |
    | Decomposição      | 6-24 meses       | 450+ anos        |
    | Custo             | 2-3x maior       | Baixo            |
    | Resistência       | 50-70 MPa        | 55-80 MPa        |
    """)

    # Seção 5: Boas Práticas
    st.markdown("""
    ---
    ## 🌍 Ações Sustentáveis
    **Indústria:**
    - Design para reciclagem
    - Logística reversa eficiente

    **Sociedade:**
    1. Separação adequada
    2. Redução de descartáveis
    3. Preferência por reciclados
    4. Participação em cooperativas
    """)
# Função: compostagem
import streamlit as st

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
                use_column_width=True)
    with col2:
        st.image("imagens_residuos/metodo_ufsc.png", 
                caption="Etapas do processo de compostagem – Método UFSC",
                use_column_width=True)

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

# Para executar o app
if __name__ == "__main__":
    mostrar_compostagem()

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
def main():
    st.header("Museu do Lixo ♻️ COMCAP Florianópolis ")
    st.subheader("Aplicativo para educação ambiental")
    st.subheader("Química dos resíduos")
    st.markdown("*Desenvolvido durante a disciplina de Prática de Ensino em Espaços de Divulgação Científica (Ext 18h)*")
    st.markdown("Curso de Graduação em Química")
    st.markdown("Universidade Federal de Santa Catarina (UFSC)")
    
 # Carregar os dados (leitura CSV)
    polimeros, residuos = carregar_dados()
    
    # Abas principais com novas seções
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "🏛️ História do Museu",
        "🧪 Química dos Plásticos (Polímeros)",
        "🏷️ Tipos de Plásticos",
         "🧵 Microplásticos",
        "🏘️ Coleta Seletiva por Bairro",
        "🤝 Cooperativass de Reciclagem",
        "🌱 Compostagem",
        "🧐 Quiz",
        "📚 Atividades Pedagógicas",
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
        mostrar_coleta_seletiva()
        
    with tab6:
        mostrar_cooperativas()
   
    with tab7:
        mostrar_compostagem()
        
    with tab8:
        mostrar_quiz()
    with tab9:
        st.header("📚 Atividades Pedagógicas")
        st.markdown("Sugestões de atividades educativas sobre resíduos e meio ambiente.")

    with tab10:
        st.header("ℹ️ Sobre o Projeto")
        st.markdown("""
**Glossário Interativo de Resíduos e Polímeros**  
- Desenvolvido para educação ambiental  
- Dados técnicos baseados em normas ABNT  
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
