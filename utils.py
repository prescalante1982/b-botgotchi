import requests
import random

def obtener_chiste():
    try:
        # Intentamos obtener chistes de una categoría segura
        url = "https://v2.jokeapi.dev/joke/Any?lang=es&type=single&blacklistFlags=nsfw,religious,political,racist,sexist,explicit"
        response = requests.get(url, timeout=1.5)
        if response.status_code == 200:
            data = response.json()
            if not data.get("error"): return data["joke"]
    except: pass
    
    # Chistes infantiles de respaldo (Nunca fallan)
    chistes_infantiles = [
        "¿Qué le dice un pato a otro pato? ¡Estamos empatados!",
        "¿Cuál es el animal que es dos veces animal? El gato, porque es gato y araña.",
        "¿Por qué los libros de matemáticas están tristes? Porque tienen muchos problemas.",
        "¿Qué le dice una gallina a otra? ¡Ven-p'acá!",
        "¿Cómo se dice 'perro' en inglés? Dog. ¿Y 'veterinario'? Dog-tor.",
        "¿Qué hace un perro con un taladro? Dog-torando."
    ]
    return random.choice(chistes_infantiles)

def obtener_dato_wikipedia():
    try:
        url = "https://es.wikipedia.org/api/rest_v1/page/random/summary"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('title', 'EL UNIVERSO')}: {data.get('extract', 'Es un lugar lleno de aventuras.')}"
    except:
        return "EL ESPACIO: Es gigante y está lleno de estrellas brillantes."

def obtener_cuento_dinamico():
    # Aseguramos que siempre devuelva una LISTA para evitar que main.py se rompa
    dato = obtener_dato_wikipedia()
    tema = dato.split(':')[0].upper() if ':' in dato else "UNA AVENTURA"
    
    return [
        "B-Bot encendió sus motores de plasma...",
        f"¡Viajó a investigar sobre {tema}!",
        "Pablo Alí lo acompañó en la cabina de mando.",
        "Juntos descubrieron que el universo es genial.",
        "FIN. ¡Pulsa el Botón 1 para volver!"
    ]

def generar_laberinto(dim=8):
    # Más retador: subimos la probabilidad de obstáculos a 0.3 (30%)
    # Pero usamos un bucle para asegurar que el laberinto sea posible
    intentos = 0
    while intentos < 10:
        mapa = [[1 if random.random() < 0.32 else 0 for _ in range(dim)] for _ in range(dim)]
        mapa[0][0] = 0; mapa[dim-1][dim-1] = 0
        mapa[0][1] = 0; mapa[1][0] = 0 # Pasillo inicial
        
        # Verificación rápida: si hay un muro rodeando la meta, reintentar
        if mapa[6][7] == 1 and mapa[7][6] == 1:
            intentos += 1
            continue
        return mapa
    return mapa
