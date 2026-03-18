import pygame
import json
import os
import time
import math
import random
from utils import obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_controles.json"

class BBotFullSytem:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Cargar Controles
        with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.modo = "MENU"
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        
        # Estados
        self.texto_pantalla = ""
        self.estado_bot = "NORMAL"
        self.timer_bot = 0
        
        # Mascota
        self.necesidad_mascota = ""
        self.felicidad = 100
        
        # Juego
        self.mapa = []
        self.px, self.py = 0, 0

    def dibujar_bbot(self, t):
        # Animación de respiración/baile
        vel = 0.01 if self.estado_bot == "RISA" else 0.005
        flotar = math.sin(t * vel) * 15
        cx, cy = 400, 140 + flotar
        
        # Dibujar Bot (Blanco con pantalla oscura)
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 130), border_radius=30)
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        
        # Ojos dinámicos
        color = (255, 255, 0) if self.estado_bot == "RISA" else COLOR_NEON
        if self.estado_bot == "RISA":
            pygame.draw.circle(self.screen, color, (cx-20, cy-20), 12, 3) # Ojo ^
            pygame.draw.circle(self.screen, color, (cx+20, cy-20), 12, 3)
        else:
            pygame.draw.circle(self.screen, color, (cx-20, cy-15), 10)
            pygame.draw.circle(self.screen, color, (cx+20, cy-15), 10)

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            self.screen.fill(COLOR_FONDO)
            
            if time.time() > self.timer_bot: self.estado_bot = "NORMAL"

            # --- RENDER SEGÚN MODO ---
            if self.modo == "MENU":
                self.dibujar_bbot(t)
                for i, opt in enumerate(self.opciones):
                    es_sel = (self.seleccion == i)
                    col = (255, 200, 0) if es_sel else (100, 100, 150)
                    pygame.draw.rect(self.screen, col, (80 + i*170, 300, 150, 50), border_radius=15)
                    txt = pygame.font.SysFont("Arial", 18, bold=True).render(opt, True, (30,30,60) if es_sel else (255,255,255))
                    self.screen.blit(txt, (155+i*170 - txt.get_width()//2, 312))

            elif self.modo == "JUGAR":
                # Dibujar Laberinto 8x8
                for r in range(len(self.mapa)):
                    for c in range(len(self.mapa[0])):
                        color = (50, 50, 80) if self.mapa[r][c] == 1 else (200, 200, 200)
                        pygame.draw.rect(self.screen, color, (240 + c*40, 40 + r*40, 38, 38), border_radius=5)
                # Pablo Alí (Jugador)
                pygame.draw.circle(self.screen, COLOR_NEON, (240 + self.py*40 + 20, 40 + self.px*40 + 20), 15)

            elif self.modo == "MASCOTA":
                self.dibujar_bbot(t)
                f = pygame.font.SysFont("Arial", 25, bold=True)
                msg = f.render(f"PABLO, EL BOT: {self.necesidad_mascota}", True, (255,255,255))
                self.screen.blit(msg, (400 - msg.get_width()//2, 260))

            # --- LÓGICA DE CONTROLES ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                # Captura Universal de Input
                act = None
                if event.type == pygame.JOYBUTTONDOWN: act = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION: act = {"tipo": "hat", "val": list(event.value)}

                if act:
                    if act == self.controles.get("BOTON 4"): self.modo = "MENU"; continue

                    if self.modo == "MENU":
                        if act == self.controles.get("DERECHA"): self.seleccion = (self.seleccion + 1) % 4
                        elif act == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion - 1) % 4
                        elif act == self.controles.get("BOTON 1"):
                            self.modo = self.opciones[self.seleccion]
                            if self.modo == "JUGAR": self.mapa = generar_laberinto(8); self.px, self.py = 0, 0
                            if self.modo == "CHISTES": self.texto_pantalla = obtener_chiste(); self.estado_bot = "RISA"; self.timer_bot = time.time()+2
                            if self.modo == "MASCOTA": self.necesidad_mascota = "¡TENGO SUEÑO!"

                    elif self.modo == "JUGAR":
                        # Mover a Pablo por el laberinto
                        if act == self.controles.get("DERECHA") and self.py < 7: self.py += 1
                        if act == self.controles.get("IZQUIERDA") and self.py > 0: self.py -= 1
                        if act == self.controles.get("BOTON 1"): # Botón para reiniciar mapa
                             self.mapa = generar_laberinto(8); self.px, self.py = 0, 0

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotFullSytem(); app.run()
