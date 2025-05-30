import streamlit as st
import sqlite3
import pandas as pd

# Consulta y muestra todos los leads guardados en la base de datos leads.db en una webapp de Streamlit
def mostrar_leads():
    try:
        conn = sqlite3.connect("leads.db")
        c = conn.cursor()
        c.execute("SELECT id, nombre, empresa, email, telefono, presupuesto, necesidades, completado, fecha FROM leads")
        rows = c.fetchall()
    except Exception as e:
        st.error(f"Error consultando leads: {e}")
        return
    finally:
        conn.close()
    if not rows:
        st.info("No hay leads guardados.")
        return
    # Encabezados de las columnas
    columns = ["ID", "Nombre", "Empresa", "Email", "Teléfono", "Presupuesto", "Necesidades", "Completado", "Fecha"]
    # Convertir los datos a un DataFrame para mejor visualización
    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)

if __name__ == "__main__":
    st.title("Consulta de Leads")
    mostrar_leads()
