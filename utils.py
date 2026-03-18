import requests
import random

def obtener_chiste():
    """Trae un chiste de JokeAPI o usa backup local."""
    try:
        url = "https://v2.jokeapi.dev/joke/Any?lang=es&type=single"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if not data.get("error"):
                return data["joke"]
    except:
        pass
    
    respaldo = ["¿Qué le dice un jaguar a otro? ¡Jaguar you!", "¿Cómo se dice pañuelo en japonés? Saka-moko."]
    return random.choice(respaldo)

def obtener_dato_wikipedia():
    """
    Se conecta a Wikipedia y trae el resumen de una página aleatoria 
    en español para usarlo como dato curioso o inicio de cuento.
    """
    try:
        # API de Wikipedia para obtener una página aleatoria
        url_random = "https://es.wikipedia.org/api/rest_v1/page/random/summary"
        response = requests.get(url_random, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            titulo = data.get("title", "Algo interesante")
            extracto = data.get("extract", "")
            
            # Acortamos el texto para que quepa bien en la pantalla del B-Bot
            resumen = f"¿SABÍAS QUÉ? {titulo.upper()}: {extracto}"
            return resumen[:200] + "..." # Limitamos caracteres
    except:
        return "EL BOT NO PUDO CONECTARSE A LA GRAN BIBLIOTECA, PERO SIGUE SIENDO GENIAL."

def obtener_cuento_dinamico():
    """
    Genera un cuento combinando una base fija con un dato real de Wikipedia
    para que la historia siempre tenga un elemento nuevo.
    """
    dato_real = obtener_dato_wikipedia()
    
    # Estructura de cuento con 'semilla' de Wikipedia
    historia = [
        "B-Bot encendió su antena de largo alcance...",
        f"¡Y descubrió algo sobre {dato_real.split(':')[0]}!",
        "Decidió viajar allí con Pablo Alí en su nave.",
        "Aprendieron que el universo es gigante y lleno de magia.",
        "FIN. ¡Presiona Botón 1 para otra aventura!"
    ]
    return historia

def generar_laberinto(dimension=8):
    """Genera un mapa aleatorio de NxN."""
    mapa = [[1 if random.random() < 0.25 else 0 for _ in range(dimension)] for _ in range(dimension)]
    mapa[0][0] = 0
    mapa[dimension-1][dimension-1] = 0
    mapa[0][1] = 0
    mapa[1][0] = 0
    return mapa
