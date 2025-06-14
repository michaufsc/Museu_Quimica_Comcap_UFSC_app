import streamlit as st
import pandas as pd
import random
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Sistema Educacional de Resíduos",
    page_icon="♻️",
    layout="wide"
)

# Dados dos quizzes
QUIZ = {
    "Polímeros": [
        {
            "pergunta": "Qual destes NÃO é um polímero natural?",
            "opcoes": ["Celulose", "Borracha Natural", "PET", "Proteínas"],
            "resposta": 2,
            "explicacao": "O PET é um polímero sintético derivado do petróleo."
        },
        # Adicione mais perguntas
    ],
    "Reciclagem": [
        {
            "pergunta": "Qual símbolo indica que um material é reciclável?",
            "opcoes": ["♻", "☢", "☣", "⚡"],
            "resposta": 0,
            "explicacao": "O símbolo ♻ é o universal para materiais recicláveis."
        },
        # Adicione mais perguntas
    ]
}

# Atividades pedagógicas
ATIVIDADES = {
    "Ensino Fundamental": [
        "Jogo da memória com símbolos de reciclagem",
        "Construção de minicomposteira em garrafa PET",
        "Experimento de decomposição com diferentes materiais"
    ],
    "Ensino Médio": [
        "Análise química de polímeros com testes de combustão",
        "Simulação de cadeia produtiva de reciclagem",
        "Visita técnica a cooperativa de catadores"
    ],
    "Ensino Superior": [
        "Projeto de melhorias para gestão de resíduos
