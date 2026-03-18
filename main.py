import pygame
import json
import os
import random
from utils import obtener_dato_curioso, obtener_chiste

# --- COLORES ---
COLOR_CUERPO = (255, 255, 255)
COLOR_PANTALLA = (20, 20, 25)
COLOR_VIVO = (0, 255, 200)
COLOR_LOCO = (255, 50, 150)
COLOR_FONDO = (60, 60, 90)

CONFIG_FILE = "config.json"

class BBotApp:
    def __init__(self):
        pygame.init()
        # Pantalla completa 800x400
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("B-Bot de Pablo Ali")
        self.clock = pygame.time.Clock()
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.datos = json.load(f)
        else:
            self.datos = {"nombre": "Pablo Ali", "nivel": 1, "xp": 0}

        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks: j.init()

        self.mood = "feliz"
        self.texto = f"¡HOLA PABLO ALI! ¿QUE HAREMOS HOY?"
        self.running = True

    def dibujar_escena(self):
        self.screen.fill(COLOR_FONDO)
        
        # 1. CUERPO DEL B-BOT (Lo subimos un poco para dar espacio a la letra)
        pygame.draw.ellipse(self.screen, (40, 40, 70), (280, 270, 240, 30))
        pygame.draw.rect(self.screen, COLOR_CUERPO, (300, 20, 200, 250), border_radius=60)
        
        # 2. PANTALLA DE LA CARA
        pygame.draw.rect(self.screen, COLOR_PANTALLA, (320, 60, 160, 90), border_radius=15)

        # 3. OJOS GRANDES
        tiempo = pygame.time.get_ticks()
        if not (tiempo % 4000 < 150):
            color = COLOR_VIVO if self.mood == "feliz" else COLOR_LOCO
            pygame.draw.circle(self.screen, color, (355, 105), 20) 
            pygame.draw.circle(self.screen, (255, 255, 255), (355, 105), 10) # Pupila
            pygame.draw.circle(self.screen, color, (445, 105), 20)
            pygame.draw.circle(self.screen, (255, 255, 255), (445, 105), 10)

        # 4. BOCA
        if self.mood == "feliz":
            pygame.draw.rect(self.screen, COLOR_VIVO, (370, 190, 60, 10), border_radius=5)
        elif self.mood == "loco":
            pygame.draw.circle(self.screen, COLOR_LOCO, (400, 200), 15, 3)

        # 5. BURBUJA DE TEXTO GIGANTE (Ocupa más espacio abajo)
        pygame.draw.rect(self.screen, (255, 255, 255), (30, 280, 740, 100), border_radius=20)
        
        # FUENTE MUCHO MÁS GRANDE (Tamaño 28 o 30)
        # Usamos Arial porque es muy clara para leer
        font = pygame.font.SysFont("Arial", 28, bold=True)
        
        # Lógica para dividir el texto en dos líneas si es largo
        palabras = self.texto.split(' ')
        linea1, linea2 = "", ""
        for p in palabras:
            if len(linea1 + p) < 30: linea1 += p + " "
            else: linea2 += p + " "

        txt_surf1 = font.render(linea1.upper(), True, (30, 30, 60))
        txt_surf2 = font.render(linea2.upper(), True, (30, 30, 60))
        
        self.screen.blit(txt_surf1, (60, 295))
        self.screen.blit(txt_surf2, (60, 335))

        # BARRA DE NIVEL
        pygame.draw.rect(self.screen, (30, 30, 50), (20, 20, 180, 20), border_radius=10)
        ancho_xp = (self.datos["xp"] / 50) * 170
        pygame.draw.rect(self.screen, COLOR_VIVO, (25, 25, ancho_xp, 10), border_radius=5)

    def run(self):
        while self.running:
            self.dibujar_escena()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A
                        self.mood = "feliz"
                        self.texto = obtener_dato_curioso(self.datos)
                        self.datos["xp"] += 10
                        if self.datos["xp"] >= 50:
                            self.datos["nivel"] += 1
                            self.datos["xp"] = 0
                            self.texto = "¡SUBIMOS DE NIVEL!"
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.datos, f)
                    if event.button == 1: # B
                        self.mood = "loco"
                        self.texto = obtener_chiste()
            
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotApp()
    app.run()
    pygame.quit()
