import pygame
import json
import time
import math
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES ---
COLOR_FONDO = (60, 60, 90)
COLOR_VIVO = (0, 255, 200)
COLOR_TEXTO = (255, 255, 255)

class BBotConsola:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        self.modo = "MENU"
        self.texto = "¡HOLA PABLO ALI! ¿QUE HACEMOS?"
        self.stats = {"hambre": 100, "energia": 100, "diversion": 100}
        
        # Inicializar mandos
        self.controles = []
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            self.controles.append(j)

        self.ultima_accion = time.time()
        self.pos_pablo = [0, 0]
        self.mapa = []
        self.running = True

    def iniciar_laberinto(self):
        self.modo = "JUEGO"
        self.mapa = generar_laberinto(8)
        self.pos_pablo = [0, 0]
        self.texto = "¡LLEGA AL ORO CON LAS FLECHAS!"

    def mover(self, df, dc):
        nf, nc = self.pos_pablo[0] + df, self.pos_pablo[1] + dc
        if 0 <= nf < 8 and 0 <= nc < 8 and self.mapa[nf][nc] == 0:
            self.pos_pablo = [nf, nc]
            if nf == 7 and nc == 7:
                self.modo = "MENU"
                self.texto = "¡GANASTE PABLO ALI! ERES PRO"

    def dibujar_menu(self):
        self.screen.fill(COLOR_FONDO)
        font_t = pygame.font.SysFont("Arial", 30, bold=True)
        font_o = pygame.font.SysFont("Arial", 22, bold=True)
        
        self.screen.blit(font_t.render("MENU DEL B-BOT", True, COLOR_VIVO), (280, 40))
        opciones = ["1. LABERINTO", "2. MASCOTA", "3. CHISTES", "4. CUENTOS"]
        for i, opt in enumerate(opciones):
            pygame.draw.rect(self.screen, (255, 255, 255), (200, 100 + i*60, 400, 45), border_radius=10)
            self.screen.blit(font_o.render(opt, True, (50, 50, 80)), (250, 110 + i*60))

    def dibujar_laberinto(self):
        self.screen.fill((40, 40, 60))
        tam, ox, oy = 40, 240, 40
        for f in range(8):
            for c in range(8):
                color = (80, 80, 150) if self.mapa[f][c] == 1 else (220, 220, 250)
                if f == 7 and c == 7: color = (255, 215, 0)
                pygame.draw.rect(self.screen, color, (ox + c*tam, oy + f*tam, tam-4, tam-4), border_radius=8)
        # Pablo Alí
        pygame.draw.circle(self.screen, COLOR_VIVO, (ox + self.pos_pablo[1]*tam + 18, oy + self.pos_pablo[0]*tam + 18), 15)

    def run(self):
        while self.running:
            ahora = time.time()
            
            # Dibujar según el modo
            if self.modo == "MENU":
                self.dibujar_menu()
            elif self.modo == "JUEGO":
                self.dibujar_laberinto()
            else:
                # Fondo simple para chistes/cuentos/mascota
                self.screen.fill(COLOR_FONDO)
                font = pygame.font.SysFont("Arial", 24, bold=True)
                self.screen.blit(font.render(self.texto.upper(), True, (255, 255, 255)), (50, 180))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False

                if event.type == pygame.JOYBUTTONDOWN:
                    self.ultima_accion ahora
                    if self.modo == "MENU":
                        if event.button == 0: self.iniciar_laberinto()
                        elif event.button == 1: self.modo = "MASCOTA"; self.texto = "¡HOLA! TENGO HAMBRE"
                        elif event.button == 2: self.modo = "CHISTES"; self.texto = obtener_chiste()
                        elif event.button == 3: self.modo = "CUENTOS"; self.texto = "HABIA UNA VEZ UN ROBOT..."
                    elif event.button in [6, 7, 8, 9]: # Salir al menú
                        self.modo = "MENU"

                if self.modo == "JUEGO":
                    if event.type == pygame.JOYHATMOTION:
                        hx, hy = event.value
                        if hx != 0: self.mover(0, hx)
                        if hy != 0: self.mover(-hy, 0)

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConsola()
    app.run()
    pygame.quit()
