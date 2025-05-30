import unittest
from db import init_lead_data
from chat import extraer_datos, actualizar_lead_data

class TestChatLogic(unittest.TestCase):
    def setUp(self):
        # Simular session_state para pruebas
        class DummySession(dict):
            pass
        self._orig_session = __import__('streamlit').session_state
        __import__('streamlit').session_state = DummySession()
        __import__('streamlit').session_state['lead_data'] = init_lead_data()

    def tearDown(self):
        __import__('streamlit').session_state = self._orig_session

    def test_extraer_datos_json(self):
        # Simula una respuesta del modelo
        conversation = "Usuario: Mi nombre es Ana y trabajo en Acme. Mi correo es ana@acme.com."
        datos = extraer_datos(conversation)
        self.assertIsInstance(datos, dict)
        # No se puede garantizar el resultado exacto sin el modelo, pero debe ser dict

    def test_actualizar_lead_data(self):
        datos = {'nombre': 'Pedro', 'empresa': 'Beta', 'email': 'pedro@beta.com', 'telefono': '555', 'presupuesto': '2000', 'necesidades': 'Soporte', 'completado': 1}
        actualizar_lead_data(datos)
        lead = __import__('streamlit').session_state['lead_data']
        self.assertEqual(lead['nombre'], 'Pedro')
        self.assertEqual(lead['empresa'], 'Beta')
        self.assertEqual(lead['completado'], 1)

if __name__ == "__main__":
    unittest.main()
