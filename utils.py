import requests
import random

def obtener_chiste():
    """
    Intenta obtener un chiste fresco de JokeAPI.
    Si falla (sin internet), usa uno aleatorio de respaldo local.
    """
    try:
        # Usamos JokeAPI con filtro para español y chistes de una sola línea
        url = "https://v2.jokeapi.dev/joke/Any?lang=es&type=single"
        response = requests.get(url, timeout=2) # Timeout rápido
        
        if response.status_code == 200:
            data = response.json()
            if not data.get("error"):
                return data["joke"]
    except Exception:
        pass # Si hay error de red, cae al plan B

    # --- PLAN B: RESPALDO LOCAL ---
    chistes_locales = [
        "¿Qué le dice un jaguar a otro? ¡Jaguar you!",
        "¿Cómo se dice pañuelo en japonés? Saka-moko.",
        "¿Cuál es el colmo de un robot? ¡Que se le crucen los cables!",
        "¿Qué hace una abeja en el gimnasio? ¡Zumba!",
        "Había un niño tan, tan, tan despistado que... ¡se me olvidó el chiste!"
    ]
    return random.choice(chistes_locales)

def obtener_dato_wikipedia():
    """
    Se conecta a Wikipedia y trae el resumen de una página aleatoria
    en español para usarlo como dato curioso o semilla de cuento.
    """
    try:
        # API de Wikipedia para obtener una página aleatoria resumida
        url_random = "https://es.wikipedia.org/api/rest_v1/page/random/summary"
        response = requests.get(url_random, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            titulo = data.get("title", "Algo interesante")
            extracto = data.get("extract", "")
            
            # Acortamos el texto para que quepa bien en la pantalla
            resumen = f"{titulo.upper()}: {extracto}"
            return resumen[:150] + "..." # Limitamos a 150 caracteres
    except Exception:
        # Respaldo si no hay internet
        return "EL ESPACIO ES GIGANTE Y LLENO DE ESTRELLAS."

def obtener_cuento_dinamico():
    """
    Genera un cuento breve combinando una base fija con un dato real
    de Wikipedia para que la historia siempre tenga un elemento nuevo.
    """
    dato_real = obtener_dato_wikipedia()
    
    # Estructura de cuento con 'semilla' de Wikipedia
    # Usamos .split(':')[0] para tomar solo el título del dato de Wikipedia
    historia = [
        "B-Bot encendió sus motores de plasma...",
        f"¡Viajó a investigar sobre {dato_real.split(':')[0]}!",
        "Pablo Alí lo acompañó en la cabina de mando.",
        "Juntos descubrieron que el universo es genial.",
        "FIN. ¡Botón 1 para otra aventura!"
    ]
    return historia

def generar_laberinto(dimension=8):
    """
    Genera un mapa aleatorio de NxN.
    0 = Camino libre, 1 = Pared/Obstáculo.
    """
    # Probabilidad de pared 0.2 para que no sea muy difícil
    mapa = [[1 if random.random() < 0.2 else 0 for _ in range(dimension)] for _ in range(dimension)]
    
    # ASEGURAR CAMINO: Punto de inicio (0,0) y meta (N-1, N-1) siempre libres
    mapa[0][0] = 0
    mapa[dimension-1][dimension-1] = 0
    
    # Asegurar que el jugador no nazca encerrado
    mapa[0][1] = 0
    mapa[1][0] = 0
    
    return mapa
