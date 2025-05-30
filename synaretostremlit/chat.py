import streamlit as st
import json
from db import guardar_lead

_model_instance = None

def get_model():
    """Obtiene una instancia singleton del modelo de chat."""
    global _model_instance
    if _model_instance is None:
        try:
            from langchain.chat_models import init_chat_model
            _model_instance = init_chat_model("llama3-8b-8192", model_provider="groq")
        except Exception as e:
            st.error(f"Error inicializando el modelo: {e}")
            raise
    return _model_instance

CAMPOS = ['nombre', 'empresa', 'email', 'telefono', 'presupuesto', 'necesidades']
PREGUNTAS = {
    'nombre': '¿Cuál es tu nombre?',
    'empresa': '¿Para qué empresa trabajas?',
    'email': '¿Cuál es tu correo electrónico?',
    'telefono': '¿Cuál es tu número de teléfono?',
    'presupuesto': '¿Cuál es tu presupuesto?',
    'necesidades': '¿Cuáles son tus necesidades?'
}

def extraer_datos(conversation):
    """Extrae los datos del usuario desde la conversación usando el modelo de IA."""
    extract_prompt = (
        "Extrae y resume los siguientes datos del usuario si están presentes en la conversación: nombre, empresa, email, teléfono, presupuesto, necesidades. "
        "Si no tienes alguno, responde con 'No proporcionado'. "
        "Responde solo en formato JSON: {'nombre': ..., 'empresa': ..., 'email': ..., 'telefono': ..., 'presupuesto': ..., 'necesidades': ...}. "
        "Aquí está la conversación:\n" + conversation
    )
    try:
        extract_response = get_model().invoke(extract_prompt)
        datos = json.loads(extract_response.content.replace("'", '"'))
        return datos
    except Exception:
        return {}

def actualizar_lead_data(datos):
    for campo in st.session_state['lead_data']:
        if campo in datos and datos[campo] not in [None, '', 'No proporcionado']:
            st.session_state['lead_data'][campo] = datos[campo]

def obtener_faltantes():
    return [campo for campo in CAMPOS if not st.session_state['lead_data'][campo]]

def construir_conocidos():
    return ", ".join([f"{campo}: {st.session_state['lead_data'][campo]}" for campo in CAMPOS if st.session_state['lead_data'][campo]])

def construir_prompt(faltantes, conocidos_str):
    if faltantes:
        # Solo mencionar un dato faltante para hacer la charla aún más breve
        faltantes_a_mencionar = faltantes[:1]
        faltantes_str = ", ".join([PREGUNTAS[c] for c in faltantes_a_mencionar])
        return (
            "Eres un asistente de ventas. Conversa de manera breve y natural, como si estuvieras charlando con un cliente habitual. "
            "No saludes ni repitas saludos. "
            + (f"Ya tengo estos datos: {conocidos_str}. " if conocidos_str else "") +
            "Si el usuario ya te contó algo, puedes hacer un breve comentario. "
            "Si lo ves oportuno, puedes preguntar o invitar a que te cuente más sobre: " + faltantes_str + ". "
            "No insistas ni repitas lo que ya sabes. "
            "No hagas preguntas cerradas ni una por una. "
            "Sé cordial y breve. "
            "No saludes de nuevo, continúa la conversación."
        )
    else:
        conocidos = [f"{campo}: {st.session_state['lead_data'][campo]}" for campo in CAMPOS]
        conocidos_str = ", ".join(conocidos)
        st.session_state['lead_data']['completado'] = 1
        return (
            "Eres un asistente de ventas. "
            "Ya tienes todos los datos: " + conocidos_str + ". "
            "Agradece y despídete de forma breve y cordial. "
            "No saludes de nuevo, solo despídete."
        )

def procesar_chat():
    history = st.session_state['chat_history']
    conversation = ""
    for m in history:
        if m['role'] == 'user':
            conversation += f"Usuario: {m['content']}\n"
        else:
            conversation += f"Asistente: {m['content']}\n"
    if len(history) > 2:
        conversation = "[IMPORTANTE: Ya has saludado, NO saludes de nuevo. Continúa la conversación como si fuera una charla continua.]\n" + conversation
    datos = extraer_datos(conversation)
    actualizar_lead_data(datos)
    faltantes = obtener_faltantes()
    conocidos_str = construir_conocidos()
    system_prompt = construir_prompt(faltantes, conocidos_str)
    context = system_prompt + "\n" + conversation
    response = get_model().invoke(context)
    # Manejo de ambigüedades y errores
    if 'No entiendo' in response.content or 'no comprendo' in response.content or 'no proporcionado' in response.content.lower():
        st.session_state['chat_history'].append({"role": "assistant", "content": "No entendí completamente tu respuesta. ¿Podrías aclarar o dar más detalles?"})
        st.rerun()
    st.session_state['chat_history'].append({"role": "assistant", "content": response.content})
    if not faltantes:
        st.session_state['lead_data']['completado'] = 1
        guardar_lead(st.session_state['lead_data'])
        st.session_state['chat_history'].append({"role": "assistant", "content": "¡Gracias por la información! Hemos registrado tus datos. FIN DEL CHAT."})
        st.session_state['chat_finished'] = True
        st.rerun()
    st.rerun()
