import wikipedia
import random
import requests
from googletrans import Translator

# Inicializar traductor y configurar Wikipedia en español
translator = Translator()
wikipedia.set_lang("es")

def obtener_dato_curioso(datos):
    """
    Obtiene un dato de Wikipedia basado en los gustos del niño
    o temas universales según su nivel.
    """
    # Si el nivel es bajo, usamos sus gustos. Si es alto, añadimos temas complejos.
    temas_posibles = datos.get("gustos", ["Ciencia"])
    if datos.get("nivel", 1) >= 3:
        temas_posibles += ["Universo", "Galaxias", "Física Cuántica", "Planetas"]
    
    tema = random.choice(temas_posibles)
    
    try:
        # Buscamos un resumen muy corto (1 oración) para que quepa en la pantalla
        resumen = wikipedia.summary(tema, sentences=1)
        return resumen
    except Exception as e:
        print(f"Error en Wikipedia: {e}")
        return f"¿Sabías que los {tema} son súper interesantes? ¡Sigue explorando!"

def obtener_chiste():
    """
    Obtiene un chiste de una API pública y lo traduce, 
    o devuelve uno local si la red falla.
    """
    url_joke = "https://official-joke-api.appspot.com/random_joke"
    
    try:
        response = requests.get(url_joke, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Traducir el chiste (Setup + Punchline)
            texto_original = f"{data['setup']} ... {data['punchline']}"
            traduccion = translator.translate(texto_original, dest='es')
            return traduccion.text
    except Exception as e:
        print(f"Error obteniendo chiste online: {e}")
    
    # Chistes locales por si no hay internet o falla la API
    chistes_locales = [
        "¿Qué le dice un jaguar a otro jaguar? Jaguar you?",
        "¿Cuál es el animal que es dos veces animal? El gato, porque es gato y araña.",
        "¿Cómo se dice pañuelo en japonés? Sakamoko.",
        "¿Qué hace una abeja en el gimnasio? ¡Zumba!",
        "¿Por qué los pájaros vuelan al sur? ¡Porque caminando tardarían mucho!"
    ]
    return random.choice(chistes_locales)

def generar_laberinto(dim):
    """
    Genera una estructura de laberinto básica.
    0 = Camino libre, 1 = Pared/Obstáculo.
    """
    # Por ahora genera un mapa aleatorio simple. 
    # En la siguiente fase podemos meter el algoritmo de Backtracking completo.
    laberinto = [[random.choice([0, 0, 0, 1]) for _ in range(dim)] for _ in range(dim)]
    # Asegurar que el inicio y el final estén limpios
    laberinto[0][0] = 0
    laberinto[dim-1][dim-1] = 0
    return laberinto

def obtener_receta_simple():
    """
    Datos curiosos tipo receta para niveles altos.
    """
    recetas = [
        "Para hacer un sándwich: Pon jamón entre dos panes y ¡listo!",
        "Limonada: Agua, limón y un poquito de azúcar. ¡Refrescante!",
        "Cereal: Primero el cereal, luego la leche. ¡No lo olvides!"
    ]
    return random.choice(recetas)
