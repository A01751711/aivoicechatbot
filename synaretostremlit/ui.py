import streamlit as st
import streamlit_webrtc as webrtc
from streamlit_webrtc import WebRtcMode
import speech_recognition as sr
import av
import numpy as np
import scipy.io.wavfile as wavfile
import io  # Importar io para BytesIO

def set_styles():
    """Aplica estilos personalizados al chat de Streamlit."""
    st.markdown("""
    <style>
    .user-msg {
        background: #23272f;
        color: #fff;
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0 2px 0;
        text-align: right;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .bot-msg {
        background: #1a1d23;
        color: #fff;
        padding: 12px;
        border-radius: 10px;
        margin: 2px 0 8px 0;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .user-icon, .bot-icon {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .user-icon {
        background: #f36c6c;
        color: #fff;
    }
    .bot-icon {
        background: #f7c873;
        color: #23272f;
    }
    </style>
    """, unsafe_allow_html=True)

def show_title():
    """Muestra el título y mensaje de bienvenida en la app."""
    st.title("Asistente de Ventas IA")
    st.write("Bienvenido, por favor proporciona la información solicitada para ayudarte mejor.")

def show_chat_history():
    """Muestra el historial de chat en la interfaz de usuario."""
    chat_display = st.container()
    if not st.session_state.get('chat_finished'):
        with chat_display:
            for i, m in enumerate(st.session_state['chat_history']):
                if m['role'] == 'user':
                    st.markdown(f"""
                    <div class='user-msg'>
                        <span class='user-icon'>👤</span>
                        <span style='flex:1'><b>Tú:</b> {m['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='bot-msg'>
                        <span class='bot-icon'>🤖</span>
                        <span style='flex:1'><b>Chatbot:</b> {m['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            # Leer en voz alta la última respuesta del chatbot
            if st.session_state['chat_history']:
                last_msg = st.session_state['chat_history'][-1]
                if last_msg['role'] == 'assistant':
                    st.components.v1.html(f"""
                    <script>
                    const msg = `{last_msg['content']}`;
                    if ('speechSynthesis' in window) {{
                        const utter = new window.SpeechSynthesisUtterance(msg);
                        utter.lang = 'es-ES';
                        window.speechSynthesis.cancel();
                        window.speechSynthesis.speak(utter);
                    }}
                    </script>
                    """, height=0)
    else:
        st.markdown("""
        <div class='bot-msg'>
            <span class='bot-icon'>🤖</span>
            <span style='flex:1'><b>Chatbot:</b> ¡Gracias por la información! Hemos registrado tus datos.<br>El chat se reiniciará en unos segundos...</span>
        </div>
        """, unsafe_allow_html=True)

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.audio_data = b""

    def recv(self, frame: av.AudioFrame):
        audio = frame.to_ndarray().flatten().astype(np.int16).tobytes()
        self.audio_data += audio
        # Guardar en session_state para acceso global
        st.session_state['audio_buffer'] = st.session_state.get('audio_buffer', b"") + audio
        return frame

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio, language='es-ES')
    except Exception:
        return None

def show_voice_input():
    st.markdown("**O usa tu voz:**")
    # Usar una bandera para evitar múltiples procesamientos
    if 'voice_processed' not in st.session_state:
        st.session_state['voice_processed'] = False
    # Resetear la bandera si el uploader está vacío
    if st.session_state.get('voice_processed', False):
        if st.session_state.get('voice_file_uploader') is None:
            st.session_state['voice_processed'] = False
    # --- Aquí va la carga de archivos, siempre al final ---
    uploaded_file = st.file_uploader("Selecciona un archivo de audio (WAV, OGG, MP3)", type=["wav", "ogg", "mp3"], key="voice_file_uploader")
    if uploaded_file is not None and not st.session_state['voice_processed']:
        recognizer = sr.Recognizer()
        import tempfile
        import os
        # Convertir a WAV si es necesario
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext != '.wav':
            from pydub import AudioSegment
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            audio_temp.close()
            audio_bytes = uploaded_file.read()
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=file_ext.replace('.', ''))
            audio.export(audio_temp.name, format='wav')
            audio_path = audio_temp.name
        else:
            audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            audio_temp.write(uploaded_file.read())
            audio_temp.close()
            audio_path = audio_temp.name
        try:
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language='es-ES')
            if 'chat_history' not in st.session_state:
                st.session_state['chat_history'] = []
            st.session_state['chat_history'].append({"role": "user", "content": text})
            # En vez de modificar input_box directamente, usar clear_input para limpiar el input
            st.session_state['clear_input'] = True
            st.session_state['voice_processed'] = True
            from chat import procesar_chat
            procesar_chat()
            st.experimental_rerun()
        except Exception as e:
            st.error(f"No se pudo transcribir el audio: {e}")
        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
