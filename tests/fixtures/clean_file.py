# Archivo de prueba sin secretos
def get_user_data():
    return {"name": "test", "email": "test@example.com"}

class Configuration:
    def __init__(self):
        self.debug = True
        self.port = 8000
