import pygame
import json
import os
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES ---
COLOR_CUERPO, COLOR_PANTALLA = (255, 255, 255), (20, 20, 25)
COLOR_VIVO, COLOR_LOCO, COLOR_FONDO = (0, 255, 200), (255, 50, 150), (60, 60, 90)

class BBotApp:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        self.datos = {"nombre": "Pablo Ali", "nivel": 1, "xp": 0}
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

        self.estado = "BOT" # "BOT" o "LABERINTO"
        self.mood = "feliz"
        self.texto = "¡HOLA PABLO ALI! PRESIONA X PARA EL LABERINTO"
        
        # Variables del Laberinto
        self.mapa = []
        self.pos_pablo = [0, 0] # [fila, columna]
        self.running = True

    def iniciar_laberinto(self):
        self.estado = "LABERINTO"
        self.mapa = generar_laberinto(10) # Crea un laberinto de 10x10
        self.pos_pablo = [0, 0]
        self.texto = "¡LLEGA AL FINAL CON LAS FLECHAS!"

    def dibujar_laberinto(self):
        self.screen.fill((30, 30, 40))
        tam_celda = 35
        offset_x, offset_y = 220, 30
        
        for f in range(len(self.mapa)):
            for c in range(len(self.mapa[f])):
                color = (100, 100, 120) if self.mapa[f][c] == 1 else (200, 200, 220)
                # Meta
                if f == 9 and c == 9: color = (255, 215, 0)
                
                pygame.draw.rect(self.screen, color, (offset_x + c*tam_celda, offset_y + f*tam_celda, tam_celda-2, tam_celda-2), border_radius=4)
        
        # Dibujar a Pablo (El B-Bot chiquito)
        pygame.draw.circle(self.screen, COLOR_VIVO, (offset_x + self.pos_pablo[1]*tam_celda + 17, offset_y + self.pos_pablo[0]*tam_celda + 17), 12)
        
        # Texto de ayuda abajo
        font = pygame.font.SysFont("Arial", 22, bold=True)
        self.screen.blit(font.render(self.texto, True, (255, 255, 255)), (150, 360))

    def dibujar_bbot(self):
        self.screen.fill(COLOR_FONDO)
        pygame.draw.rect(self.screen, COLOR_CUERPO, (300, 25, 200, 250), border_radius=60)
        pygame.draw.rect(self.screen, COLOR_PANTALLA, (325, 65, 150, 90), border_radius=15)
        
        color = COLOR_VIVO if self.mood == "feliz" else COLOR_LOCO
        pygame.draw.circle(self.screen, color, (360, 110), 20)
        pygame.draw.circle(self.screen, color, (440, 110), 20)
        
        pygame.draw.rect(self.screen, (255, 255, 255), (40, 300, 720, 85), border_radius=20)
        font = pygame.font.SysFont("Arial", 22, bold=True)
        self.screen.blit(font.render(self.texto.upper(), True, (40, 40, 70)), (70, 325))

    def mover(self, df, dc):
        nf, nc = self.pos_pablo[0] + df, self.pos_pablo[1] + dc
        if 0 <= nf < 10 and 0 <= nc < 10 and self.mapa[nf][nc] == 0:
            self.pos_pablo = [nf, nc]
            if nf == 9 and nc == 9: # Ganó
                self.estado = "BOT"
                self.texto = "¡GANASTE PABLO ALI! +20 XP"
                self.datos["xp"] += 20

    def run(self):
        while self.running:
            if self.estado == "BOT": self.dibujar_bbot()
            else: self.dibujar_laberinto()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
                
                # BOTONES
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A: Dato
                        self.estado = "BOT"; self.mood = "feliz"
                        self.texto = obtener_dato_curioso(self.datos)
                    elif event.button == 1: # B: Chiste
                        self.estado = "BOT"; self.mood = "loco"
                        self.texto = obtener_chiste()
                    elif event.button in [2, 3]: # X/Y: Laberinto
                        self.iniciar_laberinto()

                # MOVIMIENTO (Flechas / D-Pad)
                if self.estado == "LABERINTO" and event.type == pygame.JOYHATMOTION:
                    x, y = event.value # x: -1 izq, 1 der / y: -1 abajo, 1 arriba
                    if x == 1: self.mover(0, 1)
                    if x == -1: self.mover(0, -1)
                    if y == 1: self.mover(-1, 0)
                    if y == -1: self.mover(1, 0)

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotApp()
    app.run()
