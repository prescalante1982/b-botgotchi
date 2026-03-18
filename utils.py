import requests
import random

def obtener_chiste():
    try:
        url = "https://v2.jokeapi.dev/joke/Any?lang=es&type=single"
        response = requests.get(url, timeout=1.5) # Timeout más agresivo
        if response.status_code == 200:
            data = response.json()
            if not data.get("error"):
                return data["joke"]
    except:
        pass
    
    chistes_locales = [
        "¿Qué le dice un jaguar a otro? ¡Jaguar you!",
        "¿Cómo se dice pañuelo en japonés? Saka-moko.",
        "¿Cuál es el colmo de un robot? ¡Que se le crucen los cables!",
        "¿Qué hace una abeja en el gimnasio? ¡Zumba!"
    ]
    return random.choice(chistes_locales)

def obtener_dato_wikipedia():
    try:
        url = "https://es.wikipedia.org/api/rest_v1/page/random/summary"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            titulo = data.get("title", "ALGO GENIAL")
            extracto = data.get("extract", "Es un misterio por descubrir.")
            return f"{titulo}: {extracto}"
    except:
        return "EL ESPACIO: Es gigante y está lleno de estrellas brillantes."

def obtener_cuento_dinamico():
    dato = obtener_dato_wikipedia()
    # Si no hay ':' usamos el texto completo, si lo hay, solo el título
    tema = dato.split(':')[0].upper() if ':' in dato else "UNA AVENTURA"
    
    return [
        "B-Bot encendió sus motores de plasma...",
        f"¡Viajó a investigar sobre {tema}!",
        "Pablo Alí lo acompañó en la cabina de mando.",
        "Juntos descubrieron que el universo es genial.",
        "FIN. ¡Pulsa el Botón 1 para volver!"
    ]

def generar_laberinto(dim=8):
    mapa = [[1 if random.random() < 0.25 else 0 for _ in range(dim)] for _ in range(dim)]
    mapa[0][0] = 0; mapa[dim-1][dim-1] = 0
    # Asegurar salida del inicio
    mapa[0][1] = 0; mapa[1][0] = 0
    return mapa
