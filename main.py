import pygame
import json
import os
import time
import math
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES ---
COLOR_VIVO = (0, 255, 200)
COLOR_SUEÑO = (100, 100, 255)
COLOR_FONDO = (60, 60, 90)

class BBotVivo:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        self.stats = {"hambre": 100, "energia": 100, "diversion": 100}
        self.estado = "IDLE" # IDLE, BAILANDO, DURMIENDO, LABERINTO
        self.texto = "¡HOLA PABLO ALI! ¡DAME UN ABRAZO!"
        
        # Configuración de controles
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

        self.offset_y = 0  # Para el salto del baile
        self.angulo = 0    # Para el balanceo
        self.running = True

    def actualizar_animacion(self):
        t = pygame.time.get_ticks()
        
        # 1. LÓGICA DE BAILE (Salto y rotación)
        if self.estado == "BAILANDO":
            self.offset_y = math.sin(t * 0.01) * 20 # Salta arriba y abajo
            self.angulo = math.sin(t * 0.01) * 10   # Se balancea
            if t % 3000 < 50: self.estado = "IDLE"  # Deja de bailar tras unos segundos
        
        # 2. LÓGICA DE SUEÑO
        elif self.stats["energia"] < 30:
            self.estado = "DURMIENDO"
            self.offset_y = math.sin(t * 0.002) * 5 # Respiración lenta
        
        else:
            self.estado = "IDLE"
            self.offset_y = 0
            self.angulo = 0

    def dibujar_ojos(self, cx, cy, color):
        t = pygame.time.get_ticks()
        
        if self.estado == "DURMIENDO":
            # Ojos cerrados: - -
            pygame.draw.rect(self.screen, COLOR_SUEÑO, (cx-55, cy+105+self.offset_y, 30, 5))
            pygame.draw.rect(self.screen, COLOR_SUEÑO, (cx+25, cy+105+self.offset_y, 30, 5))
            # Letras ZzZ
            font_z = pygame.font.SysFont("Arial", 25, bold=True)
            if t % 1000 < 500:
                self.screen.blit(font_z.render("ZzZ", True, (255, 255, 255)), (cx+80, cy+50+self.offset_y))
        
        elif self.estado == "BAILANDO":
            # Ojos de estrella o alegría: ^ ^
            pygame.draw.lines(self.screen, color, False, [(cx-50, cy+110+self.offset_y), (cx-35, cy+95+self.offset_y), (cx-20, cy+110+self.offset_y)], 4)
            pygame.draw.lines(self.screen, color, False, [(cx+20, cy+110+self.offset_y), (cx+35, cy+95+self.offset_y), (cx+50, cy+110+self.offset_y)], 4)
        
        else:
            # Ojos normales con parpadeo
            if not (t % 4000 < 150):
                pygame.draw.circle(self.screen, color, (cx-40, cy+110+self.offset_y), 20)
                pygame.draw.circle(self.screen, color, (cx+40, cy+110+self.offset_y), 20)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx-40, cy+110+self.offset_y), 8)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx+40, cy+110+self.offset_y), 8)

    def dibujar_bbot(self):
        self.screen.fill(COLOR_FONDO)
        cx, cy = 400, 25
        
        # Sombra en el piso
        pygame.draw.ellipse(self.screen, (40, 40, 70), (300, 270, 200, 30))
        
        # Cuerpo (Cápsula blanca)
        pygame.draw.rect(self.screen, (255, 255, 255), (310, cy+self.offset_y, 180, 240), border_radius=60)
        
        # Pantalla de la cara
        pygame.draw.rect(self.screen, (20, 20, 25), (330, cy+50+self.offset_y, 140, 80), border_radius=15)
        
        # Dibujar Ojos dinámicos
        color_ojos = COLOR_VIVO if self.estado != "DURMIENDO" else COLOR_SUEÑO
        self.dibujar_ojos(cx, cy, color_ojos)

        # Burbuja de texto
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 300, 700, 80), border_radius=20)
        font = pygame.font.SysFont("FreeSans", 22, bold=True)
        self.screen.blit(font.render(self.texto.upper(), True, (50, 50, 80)), (80, 330))

    def run(self):
        while self.running:
            self.actualizar_animacion()
            self.dibujar_bbot()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A: COMER
                        self.estado = "BAILANDO"
                        self.stats["hambre"] = 100
                        self.texto = "¡QUE RICO! ¡GRACIAS PABLO ALI!"
                    
                    elif event.button == 1: # B: CHISTE
                        self.estado = "BAILANDO"
                        self.texto = obtener_chiste()
                    
                    elif event.button in [2, 3]: # X/Y: DORMIR O DESPERTAR
                        if self.stats["energia"] < 50:
                            self.stats["energia"] = 100
                            self.texto = "¡YA DESPERTE! ¡A JUGAR!"
                            self.estado = "BAILANDO"
                        else:
                            self.texto = "TENGO UN POQUITO DE SUEÑO..."

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotVivo()
    app.run()
