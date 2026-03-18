import pygame
import json
import os
import random
from utils import obtener_dato_curioso, obtener_chiste

# --- COLORES ---
COLOR_CUERPO, COLOR_PANTALLA = (255, 255, 255), (20, 20, 25)
COLOR_VIVO, COLOR_LOCO, COLOR_FONDO = (0, 255, 200), (255, 50, 150), (60, 60, 90)

CONFIG_FILE = "config.json"

class BBotApp:
    def __init__(self):
        pygame.init()
        pygame.joystick.init() 
        
        # Pantalla completa 800x400
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        # Cargar datos
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.datos = json.load(f)
        else:
            self.datos = {"nombre": "Pablo Ali", "nivel": 1, "xp": 0}

        self.controles = []
        self.detectar_controles()

        self.mood = "feliz"
        self.texto = "¡HOLA PABLO ALI! PRESIONA UN BOTON PARA EMPEZAR"
        self.running = True

    def detectar_controles(self):
        """Inicializa todos los mandos conectados."""
        pygame.joystick.quit()
        pygame.joystick.init()
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

    def dibujar_escena(self):
        self.screen.fill(COLOR_FONDO)
        
        # 1. CUERPO DEL B-BOT
        pygame.draw.ellipse(self.screen, (40, 40, 70), (280, 275, 240, 30))
        pygame.draw.rect(self.screen, COLOR_CUERPO, (300, 25, 200, 250), border_radius=60)
        
        # 2. PANTALLA CARA
        pygame.draw.rect(self.screen, COLOR_PANTALLA, (325, 65, 150, 90), border_radius=15)

        # 3. OJOS
        tiempo = pygame.time.get_ticks()
        if not (tiempo % 4500 < 150):
            color = COLOR_VIVO if self.mood == "feliz" else COLOR_LOCO
            pygame.draw.circle(self.screen, color, (360, 110), 20)
            pygame.draw.circle(self.screen, (255, 255, 255), (360, 110), 8)
            pygame.draw.circle(self.screen, color, (440, 110), 20)
            pygame.draw.circle(self.screen, (255, 255, 255), (440, 110), 8)

        # 4. BOCA
        if self.mood == "feliz":
            pygame.draw.rect(self.screen, COLOR_VIVO, (370, 200, 60, 8), border_radius=4)
        else:
            pygame.draw.circle(self.screen, COLOR_LOCO, (400, 210), 12, 3)

        # 5. BURBUJA DE TEXTO (Tamaño Intermedio)
        pygame.draw.rect(self.screen, (255, 255, 255), (40, 300, 720, 85), border_radius=20)
        
        # FUENTE TAMAÑO 22 (Intermedio entre 18 y 28)
        font = pygame.font.SysFont("Arial", 22, bold=True)
        
        # Separar en dos líneas si es necesario
        palabras = self.texto.split(' ')
        l1, l2 = "", ""
        for p in palabras:
            if len(l1 + p) < 35: l1 += p + " "
            else: l2 += p + " "

        txt_s1 = font.render(l1.upper(), True, (40, 40, 70))
        txt_s2 = font.render(l2.upper(), True, (40, 40, 70))
        self.screen.blit(txt_s1, (70, 315))
        self.screen.blit(txt_s2, (70, 345))

        # BARRA DE NIVEL
        pygame.draw.rect(self.screen, (30, 30, 50), (20, 20, 180, 20), border_radius=10)
        ancho_xp = (self.datos["xp"] / 50) * 170
        pygame.draw.rect(self.screen, COLOR_VIVO, (25, 25, ancho_xp, 10), border_radius=5)

    def run(self):
        while self.running:
            # Re-escanear si se desconectan los mandos
            if len(self.controles) == 0 and pygame.time.get_ticks() % 3000 < 30:
                self.detectar_controles()

            self.dibujar_escena()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
                
                # RECONOCIMIENTO DE BOTONES (Cualquier control)
                if event.type == pygame.JOYBUTTONDOWN:
                    # Acción A (Cualquier botón frontal 0-3)
                    if event.button in [0, 1, 2, 3]:
                        self.mood = "feliz"
                        self.texto = obtener_dato_curioso(self.datos)
                        self.datos["xp"] += 10
                        if self.datos["xp"] >= 50:
                            self.datos["nivel"] += 1
                            self.datos["xp"] = 0
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.datos, f)
                    
                    # Acción B (Gatillos o Start/Select)
                    else:
                        self.mood = "loco"
                        self.texto = obtener_chiste()

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotApp()
    app.run()
    pygame.quit()
