import streamlit as st
import sys
import os

# Ajouter le dossier parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.Agent import Agent
from agents.dto_role import *

# from llama_cpp import Llama

# Chargement du modèle local
dev_agent = Agent(name="Henri", role=DeveloperDTO(), model_name="codellama:7b-instruct-q4_0")

# Interface utilisateur avec Streamlit
st.title("🤖 Rhododendron - Chatbot LLM")
st.write("Discute avec un modèle de langage local !")

# Initialisation de l'historique de conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Affichage de l'historique des messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Champ de saisie utilisateur
user_input = st.chat_input("Écris un message...")
if user_input:
    # Afficher la requête de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Génération de la réponse LLM
    with st.chat_message("assistant"):
        # pass
        response = dev_agent.query(user_input)
        st.markdown(response)

    # Ajouter la réponse à l'historique
    st.session_state.messages.append({"role": "assistant", "content": response})
