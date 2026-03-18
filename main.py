import pygame
import json
import os
import time
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES DIVERTIDOS ---
COLOR_PARED = (80, 80, 150)
COLOR_CAMINO = (220, 220, 250)
COLOR_META = (255, 215, 0)
COLOR_PABLO = (0, 255, 150)
COLOR_FONDO = (60, 60, 90)

class BBotGame:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        self.stats = {"hambre": 100, "energia": 100, "diversion": 100}
        self.datos = {"nombre": "Pablo Ali"}
        
        # Reconocer mandos
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

        self.estado = "BOT"
        self.texto = "¡HOLA PABLO ALI! VAMOS A JUGAR"
        self.pos_pablo = [0, 0]
        self.mapa = []
        self.running = True

    def iniciar_juego(self):
        self.estado = "LABERINTO"
        self.mapa = generar_laberinto(8) # Laberinto más pequeño (8x8) para que no sea difícil
        self.pos_pablo = [0, 0]
        self.texto = "¡USA LAS FLECHAS PARA LLEGAR AL ORO!"

    def dibujar_laberinto(self):
        self.screen.fill((40, 40, 60))
        tam = 40
        ox, oy = 240, 40 # Centrado en la pantalla
        
        for f in range(len(self.mapa)):
            for c in range(len(self.mapa[f])):
                color = COLOR_PARED if self.mapa[f][c] == 1 else COLOR_CAMINO
                if f == 7 and c == 7: color = COLOR_META
                pygame.draw.rect(self.screen, color, (ox + c*tam, oy + f*tam, tam-4, tam-4), border_radius=8)
        
        # Pablo Alí es una estrella en el laberinto
        pygame.draw.circle(self.screen, COLOR_PANTALLA_Luz, (ox + self.pos_pablo[1]*tam + 18, oy + self.pos_pablo[0]*tam + 18), 15)
        
        font = pygame.font.SysFont("FreeSans", 22, bold=True)
        txt_surf = font.render(self.texto, True, (255, 255, 255))
        self.screen.blit(txt_surf, (150, 365))

    def mover(self, df, dc):
        nf, nc = self.pos_pablo[0] + df, self.pos_pablo[1] + dc
        if 0 <= nf < 8 and 0 <= nc < 8 and self.mapa[nf][nc] == 0:
            self.pos_pablo = [nf, nc]
            if nf == 7 and nc == 7:
                self.estado = "BOT"
                self.texto = "¡ERES UN CAMPEON PABLO ALI!"
                self.stats["diversion"] = 100

    def dibujar_bbot(self):
        self.screen.fill(COLOR_FONDO)
        # Cuerpo y Ojos (Diseño amigable)
        pygame.draw.rect(self.screen, (255, 255, 255), (300, 30, 200, 240), border_radius=60)
        pygame.draw.circle(self.screen, (0, 200, 255), (360, 110), 22)
        pygame.draw.circle(self.screen, (0, 200, 255), (440, 110), 22)
        
        # Caja de texto limpia
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 290, 700, 90), border_radius=20)
        font = pygame.font.SysFont("FreeSans", 24, bold=True)
        txt_render = font.render(self.texto.upper(), True, (50, 50, 80))
        self.screen.blit(txt_render, (80, 320))

    def run(self):
        while self.running:
            if self.estado == "BOT": self.dibujar_bbot()
            else: self.dibujar_laberinto()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
                
                # BOTONES
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A: Aprender
                        self.estado = "BOT"
                        self.texto = obtener_dato_curioso(self.datos)
                    elif event.button == 1: # B: Reír
                        self.estado = "BOT"
                        self.texto = obtener_chiste()
                    elif event.button in [2, 3]: # X/Y: Jugar
                        self.iniciar_juego()

                # MOVIMIENTO UNIVERSAL (Hats y Ejes)
                if self.estado == "LABERINTO":
                    if event.type == pygame.JOYHATMOTION:
                        hx, hy = event.value
                        if hx != 0: self.mover(0, hx)
                        if hy != 0: self.mover(-hy, 0)
                    if event.type == pygame.JOYAXISMOTION:
                        if event.axis == 0 and abs(event.value) > 0.5: self.mover(0, 1 if event.value > 0 else -1)
                        if event.axis == 1 and abs(event.value) > 0.5: self.mover(1 if event.value > 0 else -1, 0)

            pygame.display.flip()
            self.clock.tick(20)

COLOR_PANTALLA_Luz = (0, 255, 200)

if __name__ == "__main__":
    app = BBotGame()
    app.run()
    pygame.quit()
