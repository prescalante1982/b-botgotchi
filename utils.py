import wikipedia
import random
from googletrans import Translator

translator = Translator()

def obtener_dato_curioso(datos):
    wikipedia.set_lang("es")
    # A niveles más altos, datos más complejos (Universo)
    tema = random.choice(datos["gustos"]) if datos["nivel"] < 3 else "Universo"
    try:
        resumen = wikipedia.summary(tema, sentences=1)
        return resumen[:100] + "..."
    except:
        return "¡Sabías que los robots no duermen!"

def generar_laberinto(dim):
    # Genera una matriz simple para el mini-juego
    return [[random.choice([0, 1]) for _ in range(dim)] for _ in range(dim)]
