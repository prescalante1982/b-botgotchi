import pygame
import json
import os
import time
import math
import random
from utils import obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (10, 10, 20)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_pablo.json"
TALES_DIR = ".tales"

# ==========================================
# JUEGOS CON LÓGICA AUTÓNOMA
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []
        self.estrellas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(30)]
    
    def actualizar(self, ent, ctrl):
        # Movimiento del fondo siempre activo
        for s in self.estrellas: s[1] = (s[1] + 4) % 400
        
        # Lógica de enemigos (Independiente del control)
        if random.random() < 0.05:
            self.enemigos.append({'x': random.randint(100, 700), 'y': -30, 'dir': random.choice([-1, 1])})
        
        for e in self.enemigos[:]:
            e['y'] += 3
            e['x'] += math.sin(pygame.time.get_ticks() * 0.005) * 2 # Oscilación tipo Galaxian
            if e['y'] > 400: return True # Perdió
            for b in self.balas[:]:
                if abs(e['x'] - b[0]) < 25 and abs(e['y'] - b[1]) < 25:
                    self.enemigos.remove(e); self.balas.remove(b)

        # Balas
        for b in self.balas[:]:
            b[1] -= 12
            if b[1] < 0: self.balas.remove(b)

        # Entrada de Pablo
        if ent == ctrl.get("IZQUIERDA"): self.x = max(50, self.x - 20)
        elif ent == ctrl.get("DERECHA"): self.x = min(750, self.x + 20)
        elif ent == ctrl.get("A"): self.balas.append([self.x, 350])
        return False

    def dibujar(self, sc):
        for s in self.estrellas: pygame.draw.circle(sc, (150, 150, 200), s, 1)
        # Nave Pro
        pygame.draw.polygon(sc, COLOR_NEON, [(self.x, 340), (self.x-15, 370), (self.x+15, 370)])
        pygame.draw.rect(sc, (255,255,255), (self.x-20, 360, 40, 5)) # Alerón
        for e in self.enemigos:
            pygame.draw.circle(sc, (255, 50, 50), (int(e['x']), int(e['y'])), 15)
            pygame.draw.circle(sc, (255, 255, 255), (int(e['x']-5), int(e['y']-2)), 3)

class JuegoCarreras:
    def __init__(self):
        self.x = 400; self.obs = []; self.v = 6; self.offset = 0
    
    def actualizar(self, ent, ctrl):
        self.offset = (self.offset + self.v) % 100
        # Los enemigos caen SOLOS
        if random.random() < 0.04:
            self.obs.append([random.randint(280, 480), -60])
        
        for o in self.obs[:]:
            o[1] += self.v
            if 320 < o[1] < 380 and abs(self.x - o[0]) < 35: return True
            if o[1] > 400: self.obs.remove(o)
        
        if ent == ctrl.get("IZQUIERDA"): self.x = max(270, self.x - 15)
        elif ent == ctrl.get("DERECHA"): self.x = min(490, self.x + 15)
        return False

    def dibujar(self, sc):
        pygame.draw.rect(sc, (30, 30, 30), (250, 0, 300, 400)) # Pista
        for i in range(-100, 500, 100): # Líneas de carretera
            pygame.draw.rect(sc, (200, 200, 0), (395, i + self.offset, 10, 50))
        # Carrito tipo F1 (Atari style)
        pygame.draw.rect(sc, (0, 100, 255), (self.x-10, 330, 20, 50)) # Cuerpo
        pygame.draw.rect(sc, (255, 255, 255), (self.x-25, 335, 50, 10)) # Eje delantero
        pygame.draw.rect(sc, (255, 255, 255), (self.x-25, 365, 50, 10)) # Eje trasero
        for o in self.obs:
            pygame.draw.rect(sc, (200, 50, 50), (o[0]-15, o[1], 30, 45), border_radius=3)

class JuegoPacman:
    def __init__(self):
        self.px, self.py = 4, 4; self.pts = [[1,1], [1,6], [6,1], [6,6], [3,2], [5,5]]
        self.fantasmas = [{'x':1.0, 'y':1.0, 'c':(255,0,0)}, {'x':6.0, 'y':1.0, 'c':(255,182,193)}]
        self.last_move = 0

    def actualizar(self, ent, ctrl):
        ahora = pygame.time.get_ticks()
        # Los fantasmas se mueven cada 500ms automáticamente
        if ahora - self.last_move > 500:
            for f in self.fantasmas:
                f['x'] += 0.2 if f['x'] < self.px else -0.2
                f['y'] += 0.2 if f['y'] < self.py else -0.2
            self.last_move = ahora

        if ent == ctrl.get("IZQUIERDA"): self.py = max(0, self.py-1)
        elif ent == ctrl.get("DERECHA"): self.py = min(7, self.py+1)
        elif ent == ctrl.get("ARRIBA"): self.px = max(0, self.px-1)
        elif ent == ctrl.get("ABAJO"): self.px = min(7, self.px+1)
        
        if [self.px, self.py] in self.pts: self.pts.remove([self.px, self.py])
        for f in self.fantasmas:
            if abs(f['x'] - self.px) < 0.5 and abs(f['y'] - self.py) < 0.5: return True
        return len(self.pts) == 0

    def dibujar(self, sc):
        # Puntos
        for p in self.pts: pygame.draw.circle(sc, (255,255,255), (240+p[1]*40+20, 40+p[0]*40+20), 4)
        # Pacman
        pygame.draw.circle(sc, (255,255,0), (240+self.py*40+20, 40+self.px*40+20), 16)
        # Fantasmas con faldita (Atari)
        for f in self.fantasmas:
            fx, fy = 240+f['y']*40+20, 40+f['x']*40+20
            pygame.draw.circle(sc, f['c'], (int(fx), int(fy)), 16) # Cabeza
            pygame.draw.rect(sc, f['c'], (int(fx-16), int(fy), 32, 12)) # Cuerpo
            # Ojos
            pygame.draw.circle(sc, (255,255,255), (int(fx-6), int(fy-2)), 4)
            pygame.draw.circle(sc, (255,255,255), (int(fx+6), int(fy-2)), 4)

# ==========================================
# CONSOLA PRINCIPAL (EL MOTOR)
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400))
        self.clock = pygame.time.Clock(); self.running = True
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()
        
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.indice_cfg = 0
        self.modo = "MENU" if os.path.exists(CONFIG_FILE) else "CONFIG"
        if self.modo == "MENU":
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)

        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.juegos_lista = ["NAVES", "CARRERAS", "PAC-MAN"]
        self.sel_juego = 0; self.sub_modo = "MENU_JUEGOS"; self.juego_actual = None
        self.texto_chiste = ""

    def run(self):
        while self.running:
            self.screen.fill(COLOR_FONDO)
            t = pygame.time.get_ticks()
            entrada_pablo = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                entrada_pablo = self.obtener_entrada(event)

            # Lógica de Gatillos Siempre Activa
            if entrada_pablo == self.controles.get("L"): self.modo = "MENU"; self.juego_actual = None
            if entrada_pablo == self.controles.get("R") and self.modo == "MENU":
                self.modo = self.opciones[self.seleccion]; self.sub_modo = "MENU_JUEGOS"

            if self.modo == "CONFIG":
                self.mostrar_texto(f"CONFIGURA: {self.pasos_config[self.indice_cfg]}", y=200)
                if entrada_pablo:
                    self.controles[self.pasos_config[self.indice_cfg]] = entrada_pablo
                    self.indice_cfg += 1
                    if self.indice_cfg >= len(self.pasos_config):
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                        self.modo = "MENU"

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    c = (0, 255, 150) if self.seleccion == i else (50, 50, 80)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=10)
                    self.mostrar_texto(opt, 40+i*190+85, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if entrada_pablo == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                elif entrada_pablo == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4

            elif self.modo == "JUGAR":
                if self.sub_modo == "MENU_JUEGOS":
                    self.mostrar_texto("ARCADE CENTER", y=50, color=COLOR_NEON, size=35)
                    for i, jg in enumerate(self.juegos_lista):
                        col = (255,255,0) if self.sel_juego == i else (150,150,150)
                        self.mostrar_texto(jg, y=140+i*60, color=col, size=30)
                    if entrada_pablo == self.controles.get("ABAJO"): self.sel_juego = (self.sel_juego+1)%3
                    elif entrada_pablo == self.controles.get("ARRIBA"): self.sel_juego = (self.sel_juego-1)%3
                    elif entrada_pablo == self.controles.get("A"):
                        if self.sel_juego == 0: self.juego_actual = JuegoNaves()
                        elif self.sel_juego == 1: self.juego_actual = JuegoCarreras()
                        elif self.sel_juego == 2: self.juego_actual = JuegoPacman()
                        self.sub_modo = "JUGANDO"
                else:
                    # AQUÍ ESTÁ LA MAGIA: El juego se actualiza SIEMPRE, haya entrada o no
                    if self.juego_actual.actualizar(entrada_pablo, self.controles):
                        self.sub_modo = "MENU_JUEGOS"
                    self.juego_actual.dibujar(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    def obtener_entrada(self, event):
        if event.type == pygame.JOYBUTTONDOWN: return {"tipo": "btn", "val": event.button}
        if event.type == pygame.JOYHATMOTION and event.value != (0,0): return {"tipo": "hat", "val": list(event.value)}
        if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.5: 
            return {"tipo": "axis", "val": [event.axis, 1 if event.value > 0 else -1]}
        return None

    def mostrar_texto(self, txt, x=400, y=200, color=(255,255,255), size=22, centrar=True):
        font = pygame.font.SysFont("Arial", size, True)
        s = font.render(str(txt), True, color)
        pos = (x - s.get_width()//2, y) if centrar else (x, y)
        self.screen.blit(s, pos)

    def dibujar_bot(self, t):
        f = math.sin(t * 0.005) * 15
        pygame.draw.rect(self.screen, (255,255,255), (350, 100+f, 100, 100), border_radius=20)
        pygame.draw.circle(self.screen, (0,0,0), (380, 130+f), 6)
        pygame.draw.circle(self.screen, (0,0,0), (420, 130+f), 6)

if __name__ == "__main__":
    BBotConsola().run()
