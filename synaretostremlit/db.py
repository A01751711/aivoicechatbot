import sqlite3

def init_db():
    try:
        conn = sqlite3.connect("leads.db")
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                empresa TEXT,
                email TEXT,
                telefono TEXT,
                presupuesto TEXT,
                necesidades TEXT,
                completado INTEGER DEFAULT 0,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migración simple para agregar columnas si no existen
        try:
            c.execute("ALTER TABLE leads ADD COLUMN presupuesto TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE leads ADD COLUMN necesidades TEXT")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE leads ADD COLUMN completado INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        conn.commit()
    except Exception as e:
        print(f"Error inicializando la base de datos: {e}")
    finally:
        conn.close()

def guardar_lead(datos):
    try:
        conn = sqlite3.connect("leads.db")
        c = conn.cursor()
        c.execute("INSERT INTO leads (nombre, empresa, email, telefono, presupuesto, necesidades, completado) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (datos.get('nombre',''), datos.get('empresa',''), datos.get('email',''), datos.get('telefono',''), datos.get('presupuesto',''), datos.get('necesidades',''), int(datos.get('completado',0))))
        conn.commit()
    except Exception as e:
        print(f"Error guardando lead: {e}")
    finally:
        conn.close()

def init_lead_data():
    """Inicializa el diccionario de datos de lead con valores vacíos."""
    return {
        'nombre': '',
        'empresa': '',
        'email': '',
        'telefono': '',
        'presupuesto': '',
        'necesidades': '',
        'completado': 0
    }
