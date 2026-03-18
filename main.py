import pygame
import json
import os
import random
from utils import obtener_dato_curioso, obtener_chiste

# --- CONFIGURACIÓN VISUAL ---
COLOR_CUERPO = (255, 255, 255)
COLOR_PANTALLA = (20, 20, 25)
COLOR_VIVO = (0, 255, 200)
COLOR_LOCO = (255, 50, 150)
COLOR_FONDO = (60, 60, 90)

CONFIG_FILE = "config.json"

class BBotApp:
    def __init__(self):
        pygame.init()
        # Forzar Pantalla Completa a 800x400
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("B-Bot de Pablo Ali")
        self.clock = pygame.time.Clock()
        
        # Datos persistentes
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.datos = json.load(f)
        else:
            self.datos = {"nombre": "Pablo Ali", "nivel": 1, "xp": 0}

        # --- INICIALIZACIÓN DE TODOS LOS JOYSTICKS ---
        pygame.joystick.init()
        self.controles = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.controles.append(joy)
            print(f"Control {i} detectado: {joy.get_name()}")

        self.mood = "feliz"
        self.texto = f"¡HOLA PABLO ALI! PRESIONA CUALQUIER BOTON"
        self.running = True

    def dibujar_interfaz(self):
        self.screen.fill(COLOR_FONDO)
        
        # 1. CUERPO (Ajustado para dejar espacio a la letra grande)
        pygame.draw.ellipse(self.screen, (40, 40, 70), (280, 270, 240, 30))
        pygame.draw.rect(self.screen, COLOR_CUERPO, (300, 20, 200, 250), border_radius=60)
        
        # 2. CARA DIGITAL
        pygame.draw.rect(self.screen, COLOR_PANTALLA, (320, 60, 160, 90), border_radius=15)

        # 3. OJOS (Pestañeo aleatorio)
        tiempo = pygame.time.get_ticks()
        if not (tiempo % 4000 < 150):
            color = COLOR_VIVO if self.mood == "feliz" else COLOR_LOCO
            # Ojo Izquierdo
            pygame.draw.circle(self.screen, color, (355, 105), 22) 
            pygame.draw.circle(self.screen, (255, 255, 255), (355, 105), 10)
            # Ojo Derecho
            pygame.draw.circle(self.screen, color
