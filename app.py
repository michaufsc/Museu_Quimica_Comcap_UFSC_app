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

# Caminho correto para a pasta de imagens
IMAGES_DIR = "imagens_materiais"

# Carregar dados (polímeros e resíduos)
@st.cache_data
def load_data():
    polimeros = pd.read_csv("polimeros.csv", sep=";")
    residuos = pd.read_csv("residuos.csv", sep=";")
    return polimeros, residuos

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
        horizontal=True,
        key="glossario_tipo_material"
    )
    
    # Barra de busca
    termo_busca = st.text_input(
        "🔍 Pesquisar por nome, sigla ou aplicação:",
        key="glossario_busca"
    )
    
    # Seleção do dataframe apropriado
    df = polimeros if tipo_material == "Polímeros" else residuos
    
    # Filtragem dos dados
    if termo_busca:
        termo_busca = termo_busca.lower()
        df = df[
            df.apply(lambda row: 
                any(termo_busca in str(valor).lower() 
                    for valor in row.values), 
                axis=1)
        ]
    
    # Mensagem se não encontrar resultados
    if df.empty:
        st.warning("Nenhum resultado encontrado para sua busca.")
        if termo_busca:
            st.info("Sugestão: tente termos mais gerais ou verifique a ortografia.")
        return
    
    # Exibição dos itens
    for _, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3], gap="medium")
            
            # Coluna 1 - Imagem
            with col1:
                sigla = row.get("Sigla", row.get("Sigla ou Nome", "SEM_SIGLA"))
                nome_imagem = re.sub(r'[^a-z0-9]', '', str(sigla).lower())
                caminho_imagem = os.path.join(IMAGES_DIR, f"{nome_imagem}.png")
                
                if os.path.exists(caminho_imagem):
                    st.image(
                        Image.open(caminho_imagem),
                        use_container_width=True,
                        caption=sigla
                    )
                else:
                    # Imagem padrão quando não encontrada
                    img_padrao = Image.new('RGB', (300, 300), color=(240, 240, 240))
                    st.image(
                        img_padrao,
                        use_container_width=True,
                        caption=f"Imagem não disponível para {sigla}"
                    )
            
            # Coluna 2 - Informações
            with col2:
                st.subheader(row.get("Nome", row.get("Categoria", "Sem nome")))
                
                # Criando um layout organizado com colunas internas
                col_info1, col_info2 = st.columns(2)
                
                with col_info1:
                    st.markdown(f"""
                    **🔤 Sigla:**  
                    {sigla}  
                    
                    **🧪 Composição:**  
                    {row.get('Composição Química', 'Não especificado')}  
                    
                    **🔄 Reciclável:**  
                    {row.get('Reciclável', 'Não especificado')}
                    """)
                
                with col_info2:
                    st.markdown(f"""
                    **📌 Tipo:**  
                    {row.get('Tipo de Polimerização', row.get('Classe ABNT', 'Não especificado'))}  
                    
                    **📊 Densidade:**  
                    {row.get('Densidade', 'Não especificado')}  
                    
                    **🔥 Ponto de Fusão:**  
                    {row.get('Ponto de Fusão', 'Não especificado')}
                    """)
                
                # Aplicações com expansor para economizar espaço
                with st.expander("📦 Aplicações Comuns"):
                    aplicacoes = row.get('Aplicações Comuns', row.get('Aplicações ou Exemplos', 'Não especificado'))
                    st.write(aplicacoes)
            
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

# Função principal
def main():
    st.header("Museu do Lixo - COMCAP Florianópolis ♻️")
    st.subheader("Aplicativo para educadores: Química dos resíduos")
    st.markdown("*Desenvolvido durante a disciplina de Prática de Ensino em Espaços de Divulgação Científica (Ext 18h)*")
    
    # Divisória superior
    st.markdown("---")
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
""")
        st.markdown("""
**Autor:** nome alunos e prof  
**Disciplina:** Prática de Ensino em Espaços de Divulgação Científica (Ext 18h-a)  
**Instituição:** Universidade Federal de Santa Catarina (UFSC)
""")

if __name__ == "__main__":
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    main()
