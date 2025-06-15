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
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

def mostrar_coleta_seletiva():
    st.header("🏘️ Coleta Seletiva por Bairro")

    # Carrega os dados do GitHub
    df = load_coleta_data()

    # Sidebar com filtros
    with st.sidebar:
        st.subheader("🔎 Filtros")
        bairros = sorted(df['nome'].str.extract(r'^(.*?)(?=\s*-)')[0].dropna().unique())
        bairro_selecionado = st.selectbox("Selecione um bairro:", options=["Todos"] + bairros)

        tipos_disponiveis = list(df['tipo'].unique())
        tipo_selecionado = st.radio("Tipo de ponto:", options=["Todos"] + tipos_disponiveis)

    # Filtro por bairro
    dados_filtrados = df.copy()
    if bairro_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['nome'].str.contains(bairro_selecionado, case=False)]

    # Filtro por tipo
    if tipo_selecionado != "Todos":
        dados_filtrados = dados_filtrados[dados_filtrados['tipo'] == tipo_selecionado]

    # Estatísticas rápidas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Pontos exibidos", len(dados_filtrados))
    with col2:
        st.metric("Total no banco", len(df))

    st.markdown("---")
    st.subheader("📍 Mapa de Pontos de Coleta")

    # Mapa com marcadores
    m = folium.Map(location=[-27.5969, -48.5495], zoom_start=12, tiles="CartoDB positron")

    for _, row in dados_filtrados.iterrows():
        popup = f"""
        <b>{row['nome']}</b><br>
        <b>Tipo:</b> {row['tipo']}<br>
        <b>Dias:</b> {row.get('dias_coleta', 'Não informado')}<br>
        <b>Horário:</b> {row.get('horario', 'Não informado')}
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=popup,
            icon=folium.Icon(color='green' if row['tipo'] == 'PEV' else 'blue', icon='recycle' if row['tipo'] == 'PEV' else 'trash')
        ).add_to(m)

    folium_static(m, width=800, height=500)

    # Legenda
    st.markdown("""
    **Legenda:**  
    🟢 PEVs (Pontos de Entrega Voluntária)  
    🔵 Pontos de Coleta Regular
    """)

    # Tabela
    st.markdown("---")
    st.subheader("📋 Detalhes dos Pontos")

    st.dataframe(
        dados_filtrados[['nome', 'tipo', 'dias_coleta', 'horario']].rename(columns={
            'nome': 'Local',
            'tipo': 'Tipo',
            'dias_coleta': 'Dias de Coleta',
            'horario': 'Horário'
        }),
        height=400,
        use_container_width=True
    )

    # Informações educativas
    st.markdown("---")
    st.subheader("ℹ️ Como Funciona a Coleta Seletiva")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### ✅ Materiais Aceitos
        - Papel, papelão e jornais  
        - Plásticos (limpos e secos)  
        - Vidros (sem tampas)  
        - Metais (latas, arames)
        """)

    with col2:
        st.markdown("""
        ### ❌ Materiais Recusados
        - Lixo orgânico  
        - Fraldas descartáveis  
        - Espelhos e cerâmicas  
        - Embalagens sujas
        """)

    st.markdown("*Fonte: [Programa de Coleta Seletiva de Florianópolis](https://www.pmf.sc.gov.br/)*")


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
        st.header("🧵 Microplásticos")
        st.markdown("Conteúdo sobre microplásticos ainda será adicionado.")

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
**Disciplina:** Prática de Ensino em Espaços de Divulgação Científica (Ext 18h-a)  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)
""")

# Execução do app
if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    main()

