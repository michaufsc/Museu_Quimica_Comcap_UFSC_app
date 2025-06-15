# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import random
import os
from PIL import Image
import re

# Configuração da página
st.set_page_config(
    page_title="Sistema Completo de Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Caminhos e diretórios
IMAGES_DIR = "imagens_materiais"

# Dicionário completo de polímeros
DADOS_ESPECIFICOS = {
    'PET': {
        'Nome Completo': 'Politereftalato de Etileno',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,36-1,38 g/cm³',
        'Ponto de Fusão': '250-260°C',
        'Reciclável': 'Sim (código 1)',
        'Aplicações': 'Garrafas, fibras têxteis, embalagens',
        'Descrição': 'Um dos plásticos mais reciclados mundialmente, derivado do petróleo'
    },
    'PE': {
        'Nome Completo': 'Polietileno',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '0,91-0,96 g/cm³',
        'Ponto de Fusão': '105-130°C',
        'Reciclável': 'Sim (código 2)',
        'Aplicações': 'Sacolas, embalagens, tubos',
        'Descrição': 'Plástico mais comum, com versões de alta e baixa densidade'
    },
    'PP': {
        'Nome Completo': 'Polipropileno',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '0,90-0,91 g/cm³',
        'Ponto de Fusão': '160-170°C',
        'Reciclável': 'Sim (código 5)',
        'Aplicações': 'Utensílios domésticos, embalagens',
        'Descrição': 'Versátil e resistente a produtos químicos'
    },
    'PVC': {
        'Nome Completo': 'Policloreto de Vinila',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '1,38 g/cm³',
        'Ponto de Fusão': '100-260°C',
        'Reciclável': 'Sim (código 3)',
        'Aplicações': 'Tubos, revestimentos, cabos',
        'Descrição': 'Contém cloro em sua composição, requer cuidados na reciclagem'
    },
    'PS': {
        'Nome Completo': 'Poliestireno',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '1,04-1,07 g/cm³',
        'Ponto de Fusão': '240°C',
        'Reciclável': 'Sim (código 6)',
        'Aplicações': 'Embalagens, isolantes térmicos',
        'Descrição': 'Conhecido como isopor quando expandido (EPS)'
    },
    'PLA': {
        'Nome Completo': 'Ácido Polilático',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,24-1,27 g/cm³',
        'Ponto de Fusão': '150-160°C',
        'Reciclável': 'Sim (compostável)',
        'Aplicações': 'Impressão 3D, embalagens',
        'Descrição': 'Biopolímero derivado de fontes renováveis como milho e cana'
    },
    'PA': {
        'Nome Completo': 'Poliamida',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,13-1,15 g/cm³',
        'Ponto de Fusão': '220-265°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Têxteis, peças industriais',
        'Descrição': 'Conhecido como Nylon, possui alta resistência mecânica'
    },
    'ABS': {
        'Nome Completo': 'Acrilonitrila Butadieno Estireno',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '1,04-1,06 g/cm³',
        'Ponto de Fusão': '105°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Brinquedos, peças automotivas',
        'Descrição': 'Terpolímero resistente ao impacto'
    },
    'PTFE': {
        'Nome Completo': 'Politetrafluoretileno',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '2,15-2,20 g/cm³',
        'Ponto de Fusão': '327°C',
        'Reciclável': 'Não',
        'Aplicações': 'Revestimentos antiaderentes',
        'Descrição': 'Conhecido como Teflon, possui alta resistência química'
    },
    'PUR': {
        'Nome Completo': 'Poliuretano',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,05 g/cm³',
        'Ponto de Fusão': 'Varia',
        'Reciclável': 'Não',
        'Aplicações': 'Espumas, colchões, fibras',
        'Descrição': 'Versátil, usado de mobiliário a roupas'
    },
    'PC': {
        'Nome Completo': 'Policarbonato',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,20-1,22 g/cm³',
        'Ponto de Fusão': '230-260°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Lentes, CDs, capacetes',
        'Descrição': 'Transparente e resistente ao impacto'
    },
    'PMMA': {
        'Nome Completo': 'Polimetilmetacrilato',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '1,17-1,20 g/cm³',
        'Ponto de Fusão': '160°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Displays, próteses',
        'Descrição': 'Conhecido como acrílico ou vidro acrílico'
    },
    'POM': {
        'Nome Completo': 'Poliacetal',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,41-1,43 g/cm³',
        'Ponto de Fusão': '175°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Engrenagens, componentes',
        'Descrição': 'Alta rigidez e baixo atrito'
    },
    'EVA': {
        'Nome Completo': 'Etileno Acetato de Vinila',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '0,93 g/cm³',
        'Ponto de Fusão': 'Varia',
        'Reciclável': 'Sim',
        'Aplicações': 'Solas de sapato, brinquedos',
        'Descrição': 'Copolímero flexível e leve'
    },
    'PBT': {
        'Nome Completo': 'Polibutileno Tereftalato',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,31 g/cm³',
        'Ponto de Fusão': '223°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Conectores elétricos',
        'Descrição': 'Poliéster termoplástico resistente'
    },
    'SAN': {
        'Nome Completo': 'Estireno Acrilonitrila',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '1,07-1,08 g/cm³',
        'Ponto de Fusão': '115-120°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Eletrodomésticos',
        'Descrição': 'Copolímero transparente'
    },
    'PPS': {
        'Nome Completo': 'Polifenileno Sulfeto',
        'Tipo de Polimerização': 'Policondensação',
        'Densidade': '1,35 g/cm³',
        'Ponto de Fusão': '280-285°C',
        'Reciclável': 'Sim',
        'Aplicações': 'Peças eletrônicas',
        'Descrição': 'Alta resistência térmica'
    },
    'LDPE': {
        'Nome Completo': 'Polietileno de Baixa Densidade',
        'Tipo de Polimerização': 'Adição',
        'Densidade': '0,91-0,93 g/cm³',
        'Ponto de Fusão': '105-115°C',
        'Reciclável': 'Sim (código 4)',
        'Aplicações': 'Filmes plásticos',
        'Descrição': 'Versão flexível do PE'
    }
}
    
  # Mapeamento de siglas para nomes de arquivos de imagem
MAPA_IMAGENS = {
    'PET': 'pet.png',
    'PE': 'pe.png',
    'PP': 'pp.png',
    'PVC': 'pvc.png',
    'PS': 'ps.png',
    'ABS': 'abs.png',
    'PLA': 'pla.png',
    'PA': 'pa.png',
    'PTFE': 'ptfe.png',
    'PUR': 'pur.png',
    'PC': 'pc.png',
    'PMMA': 'pmma.png',
    'POM': 'pom.png',
    'EVA': 'eva.png',
    'PBT': 'pbt.png',
    'SAN': 'san.png',
    'PPS': 'pps.png',
    'LDPE': 'ldpe.png'
}

# Carregar dados (polímeros e resíduos)
@st.cache_data
def load_data():
    try:
        polimeros = pd.read_csv("polimeros.csv", sep=";")
        residuos = pd.read_csv("residuos.csv", sep=";")
        return polimeros, residuos
    except FileNotFoundError as e:
        st.error(f"Erro ao carregar arquivos de dados: {e}")
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data
def load_quiz():
    try:
        df = pd.read_csv("quiz_perguntas.csv", sep=";")
        questions = []
        for _, row in df.iterrows():
            questions.append({
                "pergunta": row['pergunta'],
                "opcoes": [str(row[f'opcao_{i}']) for i in range(1,5)],
                "resposta": int(row['resposta']),
                "explicacao": row['explicacao']
            })
        random.shuffle(questions)
        return questions
    except FileNotFoundError:
        st.error("Arquivo de quiz não encontrado!")
        return []

def mostrar_glossario():
    st.header("📖 Glossário Interativo de Polímeros")
    
    # Filtros na sidebar
    with st.sidebar:
        st.subheader("Filtros")
        tipo_filtro = st.selectbox(
            "Tipo de Polimerização",
            ["Todos"] + list(sorted({v['Tipo de Polimerização'] for v in DADOS_ESPECIFICOS.values()}))
        )
        
        reciclavel_filtro = st.selectbox(
            "Reciclável",
            ["Todos", "Sim", "Não"]
        )
        
        busca = st.text_input("Buscar por nome ou sigla:")

    # Aplicar filtros
    polimeros_filtrados = {}
    for sigla, dados in DADOS_ESPECIFICOS.items():
        if tipo_filtro != "Todos" and dados['Tipo de Polimerização'] != tipo_filtro:
            continue
        if reciclavel_filtro != "Todos" and not dados['Reciclável'].startswith(reciclavel_filtro):
            continue
        if busca and busca.lower() not in sigla.lower() and busca.lower() not in dados['Nome Completo'].lower():
            continue
        polimeros_filtrados[sigla] = dados

    # Exibição - MODIFICADO: removido o expander aninhado
    for sigla, dados in polimeros_filtrados.items():
        with st.expander(f"{sigla} - {dados['Nome Completo']}", expanded=False):
            col1, col2 = st.columns([1, 3])
            
           with col1:
    try:
        img_path = os.path.join(IMAGES_DIR, MAPA_IMAGENS.get(sigla, f"{sigla.lower()}.png"))
        if os.path.exists(img_path):
            st.image(Image.open(img_path), caption=sigla, use_column_width=True)
        else:
            raise FileNotFoundError
    except Exception as e:
        st.image(
            Image.new('RGB', (300, 200), color=(240, 240, 240)),
            caption=f"Imagem não disponível - {sigla}",
            use_column_width=True
        )
            
            with col2:
                st.markdown(f"""
                **🧪 Tipo de Polimerização:** {dados['Tipo de Polimerização']}  
                **⚖ Densidade:** {dados['Densidade']}  
                **🔥 Ponto de Fusão:** {dados['Ponto de Fusão']}  
                **♻ Reciclável:** {dados['Reciclável']}
                """)
                
                # MODIFICADO: Substituído o expander por markdown diretamente
                st.markdown("### 🔍 Detalhes")
                st.markdown(f"**Aplicações:** {dados['Aplicações']}")
                st.markdown(f"**Descrição:** {dados['Descrição']}")
    
    st.markdown(f"*Mostrando {len(polimeros_filtrados)} de {len(DADOS_ESPECIFICOS)} polímeros*")

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

# Função principal
# Função principal
def main():
    st.header("Museu do Lixo - COMCAP Florianópolis ♻️")
    st.subheader("Aplicativo para educadores: Química dos resíduos")
    st.markdown("*Desenvolvido durante a disciplina de Prática de Ensino em Espaços de Divulgação Científica (Ext 18h)*")
    
    # Divisória superior
    st.markdown("---")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏛️ História do Museu",
        "🏷️ Glossário",
        "🧐 Quiz",
        "🧪 Química",
        "🌱 Compostagem",
        "ℹ️ Sobre"
    ])

    with tab1:
        mostrar_historia()
    with tab2:
        mostrar_glossario()
    with tab3:
        mostrar_quiz()
    with tab4:
        mostrar_quimica()
    with tab5:
        mostrar_compostagem()
    with tab6:
        st.header("Sobre o Projeto")
        st.markdown("""
**Glossário Interativo de Resíduos e Polímeros**  
- Desenvolvido para educação ambiental  
- Dados técnicos baseados em normas ABNT  
- Integrado com atividades pedagógicas  
""")
        st.markdown("""
**Autor:** nome alunos e prof  
**Disciplina:** Prática de Ensino em Espaços de Divulgação Científica (Ext 18h-a)  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)
""")
if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
        st.warning(f"Diretório de imagens {IMAGES_DIR} criado automaticamente")
    main()
