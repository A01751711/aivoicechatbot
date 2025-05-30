Este proyecto es una aplicación de asistente de ventas basada en IA, construida con Streamlit y varias librerías para procesamiento de audio y chat. El flujo general es el siguiente:

Interfaz de usuario (ui.py):
Define la apariencia y el flujo de la app usando Streamlit.
Aplica estilos personalizados al chat.
Muestra el título y mensajes de bienvenida.
Presenta el historial del chat, diferenciando mensajes del usuario y del bot, y utiliza síntesis de voz para leer la última respuesta del bot.
Permite al usuario enviar mensajes de texto o cargar archivos de audio (voz), que son transcritos a texto usando SpeechRecognition y, si es necesario, convertidos a formato WAV con pydub.
Cuando se recibe un mensaje (texto o voz), se agrega al historial y se llama a la función principal de procesamiento de chat.

Procesamiento del chat (chat.py):
Contiene la lógica para procesar los mensajes del usuario, generar respuestas del asistente y actualizar el historial del chat.
Puede interactuar con otros módulos para obtener información relevante o almacenar datos.
Base de datos (db.py y leads.db):
Gestiona el almacenamiento y consulta de datos, como los leads o información de usuarios.
Permite registrar y consultar información relevante para el asistente de ventas.
Consultas adicionales (consultar_leads.py):
Proporciona funciones para consultar información específica de los leads almacenados en la base de datos.

Pruebas (test_*.py):
Archivos de pruebas unitarias para verificar el correcto funcionamiento de los módulos principales (chat, db, webrtc).

Ejecución:
El archivo main.py inicia la aplicación Streamlit.
El archivo por lotes ejecutar_streamlit.bat permite lanzar la app fácilmente en Windows.

En resumen: el usuario interactúa con la app mediante texto o voz, la entrada se procesa y almacena, el asistente responde usando IA, y toda la información relevante se guarda y consulta desde una base de datos local. Todo el flujo está integrado en una interfaz web amigable gracias a Streamlit.
