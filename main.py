import pygame
import json
import os
import random
from utils import obtener_dato_curioso, generar_laberinto, obtener_chiste

# --- CONFIGURACIÓN DE PERSISTENCIA ---
CONFIG_FILE = "config.json"
DATA_INICIAL = {
    "nombre": "Mateo",
    "edad": 7,
    "gustos": ["espacio", "dinosaurios", "robots"],
    "nivel": 1,
    "xp": 0
}

def cargar_datos():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return DATA_INICIAL
    return DATA_INICIAL

def guardar_datos(datos):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(datos, f)

# --- CLASE PRINCIPAL DEL B-BOT ---
class BBotApp:
    def __init__(self):
        pygame.init()
        # Resolución optimizada para pantallas de Raspberry Pi
        self.screen = pygame.display.set_mode((800, 480))
        pygame.display.set_caption("B-Botgotchi OS")
        self.clock = pygame.time.Clock()
        
        # Cargar progreso de Mateo
        self.datos = cargar_datos()
        
        # Inicialización de Controles (8BitDo SNES30 + USB Genérico)
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
            print(f"Control conectado: {j.get_name()}")

        # Estados del Sistema
        self.estado = "MENU" # MENU, JUEGO, DATO
        self.mood = "feliz"
        self.texto = f"¡Hola {self.datos['nombre']}! A para Dato, B para Loco."
        self.running = True

    def dibujar_interfaz(self):
        """Renderiza al B-Bot con estética Pixel Art y animaciones."""
        self.screen.fill((10, 10, 10)) # Fondo Negro
        
        # Color de la interfaz según el humor
        color_led = (0, 255, 255) if self.mood != "loco" else (255, 100, 255)
        
        # Cuerpo del B-Bot (Estilo Ron's Gone Wrong)
        # Rectángulo redondeado blanco
        pygame.draw.rect(self.screen, (235, 235, 235), (280, 60, 240, 320), border_radius=25)
        
        # Animación de Pestañeo: Cada 4 segundos cierra los ojos brevemente
        tiempo_actual = pygame.time.get_ticks()
        pestañeando = tiempo_actual % 4000 < 200
        
        if not pestañeando:
            # Ojos Pixel Art (Cuadrados)
            pygame.draw.rect(self.screen, color_led, (330, 140, 40, 40)) # Ojo L
            pygame.draw.rect(self.screen, color_led, (430, 140, 40, 40)) # Ojo R
        
        # Boca dinámica
        if self.mood == "feliz":
            pygame.draw.rect(self.screen, color_led, (360, 260, 80, 10))
        elif self.mood == "loco":
            # Efecto de boca "pixelada" abierta
            pygame.draw.rect(self.screen, color_led, (370, 250, 60, 30), 3)

        # Renderizado de Texto de información
        font = pygame.font.SysFont("monospace", 18, bold=True)
        # Dividir texto si es muy largo para que quepa en pantalla
        txt_display = self.texto[:70] + "..." if len(self.texto) > 70 else self.texto
        img_txt = font.render(txt_display, True, (255, 255, 255))
        self.screen.blit(img_txt, (50, 420))
        
        # Indicador de Nivel y XP
        lvl_txt = font.render(f"LVL: {self.datos['nivel']} | XP: {self.datos['xp']}/50", True, (0, 255, 0))
        self.screen.blit(lvl_txt, (550, 20))

    def check_evolucion(self):
        """Lógica para subir de nivel a Mateo."""
        if self.datos["xp"] >= 50:
            self.datos["nivel"] += 1
            self.datos["xp"] = 0
            self.texto = f"¡NIVEL SUBIDO! Ahora eres Nivel {self.datos['nivel']}"
            guardar_datos(self.datos)

    def run(self):
        while self.running:
            self.dibujar_interfaz()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Manejo de Inputs de Joystick
                if event.type == pygame.JOYBUTTONDOWN:
                    # BOTÓN A (Generalmente botón 0): Obtener Dato/Chiste
                    if event.button == 0:
                        self.mood = "feliz"
                        self.texto = obtener_dato_curioso(self.datos)
                        self.datos["xp"] += 10
                        self.check_evolucion()
                        guardar_datos(self.datos)
                    
                    # BOTÓN B (Generalmente botón 1): Modo Loco / Baile
                    if event.button == 1:
                        self.mood = "loco"
                        self.texto = obtener_chiste()
            
            pygame.display.flip()
            self.clock.tick(30) # 30 FPS para ahorrar recursos en la Pi 3B

if __name__ == "__main__":
    app = BBotApp()
    app.run()
