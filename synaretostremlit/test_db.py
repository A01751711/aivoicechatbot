import unittest
import sqlite3
import os
from db import init_db, guardar_lead, init_lead_data

class TestDBIntegration(unittest.TestCase):
    DB_PATH = "leads.db"

    def setUp(self):
        # Usar una base de datos temporal para pruebas
        self.test_db = "test_leads.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self._orig_db = TestDBIntegration.DB_PATH
        TestDBIntegration.DB_PATH = self.test_db
        # Parchear sqlite3.connect para usar la base de datos de prueba
        self._orig_connect = sqlite3.connect
        sqlite3.connect = lambda _: self._orig_connect(self.test_db)
        init_db()

    def tearDown(self):
        # Restaurar
        sqlite3.connect = self._orig_connect
        TestDBIntegration.DB_PATH = self._orig_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_guardar_lead_and_retrieve(self):
        datos = {
            'nombre': 'Juan',
            'empresa': 'EmpresaX',
            'email': 'juan@x.com',
            'telefono': '123456',
            'presupuesto': '1000',
            'necesidades': 'Demo',
            'completado': 1
        }
        guardar_lead(datos)
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute("SELECT nombre, empresa, email, telefono, presupuesto, necesidades, completado FROM leads")
        row = c.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], datos['nombre'])
        self.assertEqual(row[1], datos['empresa'])
        self.assertEqual(row[2], datos['email'])
        self.assertEqual(row[3], datos['telefono'])
        self.assertEqual(row[4], datos['presupuesto'])
        self.assertEqual(row[5], datos['necesidades'])
        self.assertEqual(row[6], datos['completado'])

    def test_init_lead_data(self):
        lead = init_lead_data()
        self.assertIsInstance(lead, dict)
        self.assertIn('nombre', lead)
        self.assertIn('empresa', lead)
        self.assertIn('email', lead)
        self.assertIn('telefono', lead)
        self.assertIn('presupuesto', lead)
        self.assertIn('necesidades', lead)
        self.assertEqual(lead['completado'], 0)

if __name__ == "__main__":
    unittest.main()
