import requests
import random

def obtener_chiste():
    try:
        url = "https://v2.jokeapi.dev/joke/Any?lang=es&type=single"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            if not data.get("error"):
                return data["joke"]
    except:
        pass
    return random.choice([
        "¿Qué le dice un jaguar a otro? ¡Jaguar you!",
        "¿Cómo se dice pañuelo en japonés? Saka-moko.",
        "¿Qué hace una abeja en el gimnasio? ¡Zumba!"
    ])

def obtener_dato_wikipedia():
    try:
        url = "https://es.wikipedia.org/api/rest_v1/page/random/summary"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            data = response.json()
            titulo = data.get("title", "Algo interesante")
            extracto = data.get("extract", "")
            return f"{titulo.upper()}: {extracto[:150]}..."
    except:
        return "EL ESPACIO ES GIGANTE Y LLENO DE ESTRELLAS."

def obtener_cuento_dinamico():
    dato = obtener_dato_wikipedia()
    return [
        "B-Bot encendió sus motores de plasma...",
        f"¡Viajó a investigar sobre {dato.split(':')[0]}!",
        "Pablo Alí lo acompañó en la cabina de mando.",
        "Juntos descubrieron que el universo es genial.",
        "FIN. ¡Botón 1 para otra aventura!"
    ]

def generar_laberinto(dim=8):
    mapa = [[1 if random.random() < 0.25 else 0 for _ in range(dim)] for _ in range(dim)]
    mapa[0][0] = mapa[dim-1][dim-1] = mapa[0][1] = mapa[1][0] = 0
    return mapa
