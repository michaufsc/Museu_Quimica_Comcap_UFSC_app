import streamlit as st

# ✅ A configuração da página deve ser o primeiro comando de Streamlit
st.set_page_config(
    page_title="Glossário da Química dos Resíduos",
    page_icon="♻️",
    layout="wide"
)

import pandas as pd
from io import StringIO

# ✅ Dados do glossário
@st.cache_data
def carregar_dados():
    dados_csv = """Categoria;Sigla ou Nome;Composição Química;Origem;Risco à saúde;Tratamento adequado;Destinação final
Metais Pesados;Pb (Chumbo);Pb;Baterias, tintas, ligas metálicas;Neurotoxicidade, anemia;Remoção por precipitação química;Aterro Classe I
Metais Pesados;Hg (Mercúrio);Hg;Lâmpadas fluorescentes, termômetros;Neurotoxicidade, problemas renais;Tratamento com enxofre;Aterro Classe I
Solventes Orgânicos;Benzeno;C6H6;Indústria petroquímica, tintas;Cancerígeno, problemas hematológicos;Incinerador de alta temperatura;Coprocessamento
Solventes Orgânicos;Tolueno;C7H8;Colas, tintas, combustíveis;Neurotoxicidade, irritação respiratória;Destilação;Coprocessamento
Resíduos Hospitalares;Sangue contaminado;;Hospitais, clínicas;Risco biológico, infecções;Autoclavagem;Aterro Classe I
Resíduos Hospitalares;Agulhas e seringas;;Hospitais, postos de saúde;Perfurocortantes, contaminação;Incinerador hospitalar;Aterro Classe I
Agrotóxicos;DDT;C14H9Cl5;Agricultura (proibido);Disruptor endócrino, cancerígeno;Incineração controlada;Aterro Classe I
Agrotóxicos;Glifosato;C3H8NO5P;Agricultura;Possível cancerígeno, toxicidade ambiental;Biorremediação;Aterro Classe I
Plásticos Clorados;PVC;[C2H3Cl]n;Tubulações, embalagens;Liberação de dioxinas na queima;Reciclagem especializada;Coprocessamento
Plásticos Clorados;PCBs;C12H10−xClx;Transformadores elétricos;Neurotoxicidade, bioacumulação;Incineração;Aterro Classe I
Solventes Halogenados;Tetracloreto de carbono;CCl4;Indústria química;Hepatotoxicidade, neurotoxicidade;Destilação fracionada;Coprocessamento
Solventes Halogenados;Tricloroetileno;C2HCl3;Desengraxantes, limpeza industrial;Cancerígeno, neurotoxicidade;Oxidação térmica;Coprocessamento"""
    
    return pd.read_csv(StringIO(dados_csv), sep=";")

# ✅ Carregar os dados
df = carregar_dados()

# ✅ Título do app
st.title("♻️ Glossário da Química dos Resíduos")

# ✅ Campo de busca
busca = st.text_input("🔍 Buscar termo, sigla, composição ou categoria:")

# ✅ Filtragem dos dados
if busca:
    df_filtrado = df[df.apply(lambda row: busca.lower() in str(row).lower(), axis=1)]
else:
    df_filtrado = df

# ✅ Exibir tabela filtrada
st.dataframe(df_filtrado, use_container_width=True)


