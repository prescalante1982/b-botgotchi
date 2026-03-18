import pygame
import json
import os
import time
import math
import random
from utils import obtener_chiste, obtener_cuento_dinamico, generar_laberinto, obtener_dato_wikipedia

# Colores Neón 2026
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_pablo.json"

class BBotConsola:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        # Modo ventana o pantalla completa para Raspberry
        self.screen = pygame.display.set_mode((800, 400))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Configuración de Controles
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "BOTON 1", "BOTON 2", "BOTON 3", "BOTON 4"]
        self.indice_cfg = 0
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            self.modo = "MENU"
        else:
            self.modo = "CONFIG"

        # Estados de Juego
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.texto_pantalla = "¡HOLA PABLO ALI!"
        self.estado_bot = "NORMAL" # NORMAL, RISA, LEYENDO
        self.timer_emo = 0
        
        # Variables de sub-modos
        self.mapa = []; self.px = 0; self.py = 0
        self.historia = []; self.idx_cuento = 0
        self.deseo_mascota = ""

        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

    def cambiar_emo(self, emo, seg=1.5):
        self.estado_bot = emo
        self.timer_emo = time.time() + seg

    def dibujar_bot(self, t):
        vel = 0.01 if self.estado_bot == "RISA" else 0.005
        f = math.sin(t * vel) * (20 if self.estado_bot == "RISA" else 10)
        cx, cy = 400, 140 + f
        
        # Cuerpo y Pantalla
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 130), border_radius=35)
        pygame.draw.rect(self.screen, (20, 20, 30), (cx-45, cy-45, 90, 60), border_radius=10)
        
        # Ojos dinámicos
        col = (255, 255, 0) if self.estado_bot == "RISA" else COLOR_NEON
        if self.estado_bot == "RISA":
            pygame.draw.lines(self.screen, col, False, [(cx-30, cy-15), (cx-20, cy-25), (cx-10, cy-15)], 4)
            pygame.draw.lines(self.screen, col, False, [(cx+10, cy-15), (cx+20, cy-25), (cx+30, cy-15)], 4)
        else:
            pygame.draw.circle(self.screen, col, (cx-20, cy-15), 10)
            pygame.draw.circle(self.screen, col, (cx+20, cy-15), 10)

    def mostrar_texto(self, txt, y_ini=260):
        font = pygame.font.SysFont("Arial", 20, bold=True)
        palabras = txt.split()
        linea = ""
        for p in palabras:
            if len(linea + p) < 45: linea += p + " "
            else:
                s = font.render(linea, True, (255,255,255))
                self.screen.blit(s, (400 - s.get_width()//2, y_ini))
                y_ini += 25; linea = p + " "
        s = font.render(linea, True, (255,255,255))
        self.screen.blit(s, (400 - s.get_width()//2, y_ini))

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            if time.time() > self.timer_emo: self.estado_bot = "NORMAL"
            self.screen.fill(COLOR_FONDO)

            if self.modo == "CONFIG":
                txt = pygame.font.SysFont("Arial", 30).render(f"PRESIONA: {self.pasos_config[self.indice_cfg]}", True, COLOR_NEON)
                self.screen.blit(txt, (400 - txt.get_width()//2, 180))
            
            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    sel = (self.seleccion == i)
                    c = (255, 200, 0) if sel else (100, 100, 150)
                    pygame.draw.rect(self.screen, c, (80 + i*170, 300, 150, 50), border_radius=15)
                    ti = pygame.font.SysFont("Arial", 18, True).render(opt, True, (30,30,60) if sel else (255,255,255))
                    self.screen.blit(ti, (155+i*170 - ti.get_width()//2, 312))

            elif self.modo == "JUGAR":
                for r in range(8):
                    for c in range(8):
                        col = (50, 50, 80) if self.mapa[r][c] == 1 else (200, 200, 220)
                        pygame.draw.rect(self.screen, col, (240+c*40, 40+r*40, 38, 38), border_radius=4)
                pygame.draw.circle(self.screen, COLOR_NEON, (240+self.py*40+20, 40+self.px*40+20), 15)

            elif self.modo in ["CHISTES", "CUENTOS", "MASCOTA"]:
                self.dibujar_bot(t)
                self.mostrar_texto(self.texto_pantalla)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                # CAPTURA DE INPUT
                val = None
                if event.type == pygame.JOYBUTTONDOWN: val = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION and event.value != (0,0): val = {"tipo": "hat", "val": list(event.value)}

                if val:
                    if self.modo == "CONFIG":
                        self.controles[self.pasos_config[self.indice_cfg]] = val
                        self.indice_cfg += 1
                        time.sleep(0.3)
                        if self.indice_cfg >= len(self.pasos_config):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                    else:
                        if val == self.controles.get("BOTON 4"): self.modo = "MENU"; continue
                        
                        if self.modo == "MENU":
                            if val == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                            elif val == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                            elif val == self.controles.get("BOTON 1"):
                                self.modo = self.opciones[self.seleccion]
                                if self.modo == "CHISTES": self.texto_pantalla = obtener_chiste(); self.cambiar_emo("RISA")
                                elif self.modo == "CUENTOS": self.historia = obtener_cuento_dinamico(); self.idx_cuento = 0; self.texto_pantalla = self.historia[0]
                                elif self.modo == "JUGAR": self.mapa = generar_laberinto(); self.px = self.py = 0
                                elif self.modo == "MASCOTA": self.texto_pantalla = "TENGO HAMBRE (Presiona 1)"; self.deseo_mascota = "COMER"

                        elif self.modo == "JUGAR":
                            if val == self.controles.get("DERECHA") and self.py < 7 and self.mapa[self.px][self.py+1]==0: self.py += 1
                            elif val == self.controles.get("IZQUIERDA") and self.py > 0 and self.mapa[self.px][self.py-1]==0: self.py -= 1

                        elif self.modo == "CHISTES":
                            if val == self.controles.get("BOTON 1"): self.texto_pantalla = obtener_chiste(); self.cambiar_emo("RISA")

                        elif self.modo == "CUENTOS":
                            if val == self.controles.get("BOTON 1"):
                                self.idx_cuento = (self.idx_cuento + 1) % len(self.historia)
                                self.texto_pantalla = self.historia[self.idx_cuento]
                                if self.idx_cuento == 0: self.historia = obtener_cuento_dinamico(); self.texto_pantalla = self.historia[0]

                        elif self.modo == "MASCOTA":
                            if val == self.controles.get("BOTON 1"): self.texto_pantalla = "¡YUM! GRACIAS PABLO"; self.cambiar_emo("RISA")

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    BBotConsola().run()
