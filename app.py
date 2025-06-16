# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
import re
import folium
from streamlit_folium import folium_static
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Sistema Completo de Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Caminho correto para a pasta de imagens
IMAGES_DIR = "imagens_materiais"

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
            "resposta": int(row['resposta']),
            "explicacao": row['explicacao']
        })
    random.shuffle(questions)
    return questions

# Carrega os dados
polimeros, residuos = load_data()

# Função: glossário interativo
def mostrar_glossario():
    st.header("📖 Glossário Interativo de Polímeros e Resíduos")

    # Seleção do tipo de material
    tipo_material = st.radio(
        "Selecione o tipo de material:",
        options=["Polímeros", "Resíduos"],
        horizontal=True
    )

    # Barra de busca
    termo_busca = st.text_input("🔍 Pesquisar por nome, sigla ou aplicação:")

    # Seleção do dataframe apropriado
    df = polimeros if tipo_material == "Polímeros" else residuos

    # Dados técnicos específicos para materiais selecionados
    DADOS_ESPECIFICOS = {
        'PLA': {
            'Nome': 'Ácido Polilático',
            'Tipo de Polimerização': 'Policondensação (biodegradável)',
            'Composição Química': 'Poliéster alifático termoplástico',
            'Densidade': '1,24-1,27 g/cm³',
            'Ponto de Fusão': '150-160°C',
            'Reciclável': 'Sim (compostável industrial)',
            'Aplicações Comuns': 'Impressão 3D, embalagens alimentícias, utensílios descartáveis, implantes médicos',
            'Descrição': 'PLA (Ácido Polilático) é um termoplástico biodegradável derivado de fontes renováveis como amido de milho, cana-de-açúcar ou beterraba. Possui baixa toxicidade e é amplamente utilizado na fabricação de bioplásticos.'
        },
        'PET': {
            'Tipo de Polimerização': 'Policondensação (termoplástico)',
            'Densidade': '1,36 g/cm³',
            'Ponto de Fusão': '250-260°C'
        }
    }

    # Filtragem dos dados
    if termo_busca:
        mask = df.astype(str).apply(lambda col: col.str.contains(termo_busca, case=False, na=False)).any(axis=1)
        df = df[mask]

    if df.empty:
        st.info("🔎 Nenhum resultado encontrado para sua busca.")
        return

    # Exibição dos itens
    for _, row in df.iterrows():
        with st.container():
            sigla = row.get("Sigla", row.get("Sigla ou Nome", "SEM_SIGLA"))

            # Atualiza os dados com informações específicas se existirem
            row_atualizado = row.copy()
            if sigla in DADOS_ESPECIFICOS:
                for chave, valor in DADOS_ESPECIFICOS[sigla].items():
                    row_atualizado[chave] = valor

            col1, col2 = st.columns([1, 3], gap="medium")

            # Coluna 1 - Imagem
            with col1:
                nome_imagem = f"{sigla.lower()}.png"
                caminho_imagem = os.path.join(IMAGES_DIR, nome_imagem)

                if os.path.exists(caminho_imagem):
                    st.image(
                        Image.open(caminho_imagem),
                        use_container_width=True,
                        caption=f"Símbolo {sigla}"
                    )
                else:
                    cor = (200, 230, 200) if sigla == 'PLA' else (240, 240, 240)
                    img_padrao = Image.new('RGB', (300, 300), color=cor)

                    try:
                        draw = ImageDraw.Draw(img_padrao)
                        font = ImageFont.load_default()
                        text = sigla if len(sigla) <= 4 else sigla[:4]
                        w, h = draw.textsize(text, font=font)
                        draw.text(((300 - w) / 2, (300 - h) / 2), text, fill="white", font=font)
                    except Exception as e:
                        pass

                    st.image(
                        img_padrao,
                        use_container_width=True,
                        caption=f"Imagem ilustrativa - {sigla}"
                    )

            # Coluna 2 - Informações
            with col2:
                st.subheader(row_atualizado.get("Nome", row_atualizado.get("Categoria", "Sem nome")))

                if sigla == 'PLA':
                    st.success("♻️ MATERIAL BIODEGRADÁVEL E RENOVÁVEL")

                col_info1, col_info2 = st.columns(2)

                with col_info1:
                    st.markdown(f"""
                    **🔤 Sigla:**  
                    {sigla}  
                    
                    **🧪 Tipo de Polimerização:**  
                    {row_atualizado.get('Tipo de Polimerização', 'Não especificado')}  
                    
                    **📊 Densidade:**  
                    {row_atualizado.get('Densidade', 'Não especificado')}
                    """)

                with col_info2:
                    st.markdown(f"""
                    **🔥 Ponto de Fusão:**  
                    {row_atualizado.get('Ponto de Fusão', 'Não especificado')}  
                    
                    **🔄 Reciclável:**  
                    {row_atualizado.get('Reciclável', 'Não especificado')}  
                    
                    **🧪 Composição:**  
                    {row_atualizado.get('Composição Química', 'Não especificado')}
                    """)

                if sigla in DADOS_ESPECIFICOS and 'Descrição' in DADOS_ESPECIFICOS[sigla]:
                    with st.expander("📝 Descrição Detalhada"):
                        st.write(DADOS_ESPECIFICOS[sigla]['Descrição'])

                with st.expander("📦 Aplicações Comuns"):
                    st.write(row_atualizado.get('Aplicações Comuns', row_atualizado.get('Aplicações ou Exemplos', 'Não especificado')))

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

    # Mostra o mapa (se houver dados com latitude e longitude)
    if not dados_filtrados.empty and 'latitude' in dados_filtrados.columns and 'longitude' in dados_filtrados.columns:
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
    else:
        st.warning("Nenhum ponto com coordenadas para exibir no mapa.")


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
        mostrar_glossario()

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
        mostrar_microplasticos()

    with tab8:
        st.header("🤝 Associações de Reciclagem")
        st.markdown("Conteúdo sobre cooperativas e associações será adicionado aqui.")

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
**Disciplina:** Prática de Ensino em Espaços de Divulgação Científica (Ext 18h-a)  More actions
**Instituição:** Universidade Federal de Santa Catarina (UFSC)
""")

# Execução do app
if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    main()
