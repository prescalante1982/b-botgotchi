import requests
import random

# Variable global para evitar repeticiones
ultimo_chiste = ""

def obtener_chiste():
    global ultimo_chiste
    chistes_infantiles = [
        "¿Qué le dice un pato a otro pato? ¡Estamos empatados!",
        "¿Cuál es el animal que es dos veces animal? El gato, porque es gato y araña.",
        "¿Por qué los libros de matemáticas están tristes? Porque tienen muchos problemas.",
        "¿Qué hace un perro con un taladro? Dog-torando.",
        "¿Cómo se dice 'perro' en inglés? Dog. ¿Y 'veterinario'? Dog-tor.",
        "¿Qué le dice una iguana a su hermana? Somos iguanitas."
    ]
    
    try:
        url = "https://v2.jokeapi.dev/joke/Any?lang=es&type=single&blacklistFlags=nsfw,explicit"
        response = requests.get(url, timeout=1.2)
        if response.status_code == 200:
            nuevo = response.json().get("joke", random.choice(chistes_infantiles))
            if nuevo != ultimo_chiste:
                ultimo_chiste = nuevo
                return nuevo
    except: pass
    
    nuevo = random.choice(chistes_infantiles)
    while nuevo == ultimo_chiste: nuevo = random.choice(chistes_infantiles)
    ultimo_chiste = nuevo
    return nuevo

def obtener_cuento_dinamico():
    # RESPALDO SEGURO: Si todo falla, esto evita que la App se cierre
    cuento_respaldo = [
        "B-Bot encendió sus motores de plasma...",
        "¡Viajó a una estrella lejana!",
        "Pablo Alí lo acompañó en la misión.",
        "¡Fue una aventura increíble!",
        "FIN. Presiona Botón 1 para volver."
    ]
    try:
        url = "https://es.wikipedia.org/api/rest_v1/page/random/summary"
        response = requests.get(url, timeout=1.5)
        if response.status_code == 200:
            data = response.json()
            tema = data.get('title', 'EL ESPACIO').upper()
            return [
                f"B-Bot está analizando: {tema}",
                "Iniciando teletransporte...",
                f"Pablo Alí descubrió que {tema} es asombroso.",
                "¡Misión completada con éxito!",
                "FIN. Presiona Botón 1 para volver."
            ]
    except:
        return cuento_respaldo
    return cuento_respaldo

def generar_laberinto(dim=8):
    # Laberinto retador garantizado
    mapa = [[1 if random.random() < 0.35 else 0 for _ in range(dim)] for _ in range(dim)]
    mapa[0][0] = 0; mapa[7][7] = 0
    mapa[0][1] = 0; mapa[1][0] = 0 # Asegurar salida
    return mapa
