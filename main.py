import pygame
import json
import time
import math
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (60, 60, 90)
COLOR_VIVO = (0, 255, 200)

class BBotConsola:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        try:
            self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        except:
            self.screen = pygame.display.set_mode((800, 400))
        
        self.clock = pygame.time.Clock()
        self.modo = "MENU"
        self.texto = "¡HOLA PABLO ALI! ¿QUE HACEMOS?"
        self.running = True
        self.pos_pablo = [0, 0]
        self.mapa = []
        
        self.controles = []
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            self.controles.append(j)

    def iniciar_laberinto(self):
        self.modo = "JUEGO"
        self.mapa = generar_laberinto(8)
        self.pos_pablo = [0, 0]
        self.texto = "¡LLEGA AL ORO!"

    def mover(self, df, dc):
        nf, nc = self.pos_pablo[0] + df, self.pos_pablo[1] + dc
        if 0 <= nf < 8 and 0 <= nc < 8:
            if self.mapa[nf][nc] == 0:
                self.pos_pablo = [nf, nc]
                if nf == 7 and nc == 7:
                    self.modo = "MENU"
                    self.texto = "¡GANASTE PABLO ALI!"

    def dibujar_todo(self):
        self.screen.fill(COLOR_FONDO)
        font = pygame.font.SysFont("Arial", 22, bold=True)
        
        if self.modo == "MENU":
            pygame.draw.rect(self.screen, (255, 255, 255), (200, 50, 400, 300), border_radius=20)
            opciones = ["1. JUGAR", "2. MASCOTA", "3. CHISTES", "4. CUENTOS"]
            for i, opt in enumerate(opciones):
                txt = font.render(opt, True, (50, 50, 80))
                self.screen.blit(txt, (300, 100 + i*60))
        
        elif self.modo == "JUEGO":
            ox, oy = 240, 40
            for f in range(8):
                for c in range(8):
                    color = (80, 80, 150) if self.mapa[f][c] == 1 else (220, 220, 250)
                    if f == 7 and c == 7: color = (255, 215, 0)
                    pygame.draw.rect(self.screen, color, (ox+c*40, oy+f*40, 36, 36), border_radius=5)
            pygame.draw.circle(self.screen, COLOR_VIVO, (ox+self.pos_pablo[1]*40+18, oy+self.pos_pablo[0]*40+18), 15)
        
        else:
            txt = font.render(self.texto.upper(), True, (255, 255, 255))
            self.screen.blit(txt, (100, 180))

    def run(self):
        while self.running:
            self.dibujar_todo()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.type == pygame.JOYBUTTONDOWN:
                    if self.modo == "MENU":
                        if event.button == 0: self.iniciar_laberinto()
                        elif event.button == 1: self.modo = "MASCOTA"; self.texto = "¡TENGO HAMBRE!"
                        elif event.button == 2: self.modo = "CHISTES"; self.texto = obtener_chiste()
                        elif event.button == 3: self.modo = "CUENTOS"; self.texto = "HABIA UNA VEZ UN ROBOT..."
                    
                    if event.button in [6, 7, 8, 9]:
                        self.modo = "MENU"

                if self.modo == "JUEGO" and event.type == pygame.JOYHATMOTION:
                    hx, hy = event.value
                    if hx != 0: self.mover(0, hx)
                    if hy != 0: self.mover(-hy, 0)

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConsola()
    app.run()
    pygame.quit()
