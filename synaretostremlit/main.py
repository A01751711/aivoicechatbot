import os
import streamlit as st
from db import init_db, init_lead_data
from chat import procesar_chat
from ui import set_styles, show_title, show_chat_history, show_voice_input

if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = "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"

init_db()
set_styles()
show_title()

# Inicializar historial en session_state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Estado temporal de los datos del lead en la sesión
if 'lead_data' not in st.session_state:
    st.session_state['lead_data'] = init_lead_data()

show_chat_history()

# Entrada de texto y botón siempre abajo
if not st.session_state.get('chat_finished', False):
    with st.container():
        if 'clear_input' not in st.session_state:
            st.session_state['clear_input'] = False
        input_value = "" if st.session_state['clear_input'] else st.session_state.get("input_box", "")
        user_input = st.text_input("Escribe tu mensaje:", value=input_value, key="input_box")
        send = st.button("Enviar", key="send_button")
        if send and user_input:
            st.session_state['chat_history'].append({"role": "user", "content": user_input})
            st.session_state['clear_input'] = True
            st.rerun()
        else:
            st.session_state['clear_input'] = False
        if st.session_state['chat_history'] and st.session_state['chat_history'][-1]['role'] == 'user':
            procesar_chat()

# Mostrar el saludo inicial solo la primera vez
if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True
if st.session_state['first_run'] and not st.session_state['chat_history'] and not st.session_state.get('chat_finished', False):
    st.session_state['chat_history'].append({
        "role": "assistant",
        "content": "¡Hola! Bienvenido al asistente de ventas. Estoy aquí para ayudarte, por favor dime un poco sobre ti y tu empresa cuando estés listo."
    })
    st.session_state['first_run'] = False
    st.rerun()
# Al terminar el chat, limpiar estados para un nuevo usuario tras recarga
if st.session_state.get('chat_finished', False) and st.button('Iniciar nuevo chat'):
    st.session_state['chat_history'] = []
    st.session_state['lead_data'] = init_lead_data()
    st.session_state['first_run'] = True
    st.session_state['chat_finished'] = False
    st.rerun()

# --- Mover la voz al final de la página ---
show_voice_input()
