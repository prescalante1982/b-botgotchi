import pygame
import json
import os
import time
import math
import random
from utils import obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN VISUAL ---
COLOR_FONDO = (173, 216, 230)  # Celeste Sky
COLOR_TEXTO_DARK = (40, 40, 60)
CONFIG_FILE = "config_pablo.json"

# ==========================================
# CLASES DE JUEGOS (ARCADE)
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []
        self.estrellas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(25)]
    def actualizar(self, ent, ctrl):
        for s in self.estrellas: s[1] = (s[1] + 5) % 400
        if ent == ctrl.get("IZQUIERDA"): self.x = max(30, self.x - 25)
        elif ent == ctrl.get("DERECHA"): self.x = min(770, self.x + 25)
        elif ent == ctrl.get("A"): self.balas.append([self.x, 340])
        if random.random() < 0.07: self.enemigos.append([random.randint(50, 750), -20])
        for b in self.balas[:]:
            b[1] -= 15
            if b[1] < 0: self.balas.remove(b)
        for e in self.enemigos[:]:
            e[1] += 5
            for b in self.balas[:]:
                if abs(e[0] - b[0]) < 25 and abs(e[1] - b[1]) < 25:
                    if e in self.enemigos: self.enemigos.remove(e)
                    if b in self.balas: self.balas.remove(b)
            if e[1] > 400: return True
        return False
    def dibujar(self, sc):
        sc.fill((10, 10, 30))
        for s in self.estrellas: pygame.draw.circle(sc, (255, 255, 255), s, 1)
        pygame.draw.polygon(sc, (0, 255, 200), [(self.x, 340), (self.x-20, 370), (self.x+20, 370)])
        for b in self.balas: pygame.draw.line(sc, (255, 255, 0), (b[0], b[1]), (b[0], b[1]-10), 3)
        for e in self.enemigos: pygame.draw.rect(sc, (255, 50, 100), (e[0]-15, e[1]-15, 30, 30), border_radius=8)

class JuegoCarreras:
    def __init__(self):
        self.x = 400; self.obs = []; self.v = 10; self.offset = 0
    def actualizar(self, ent, ctrl):
        self.offset = (self.offset + self.v) % 100
        if ent == ctrl.get("IZQUIERDA"): self.x = max(275, self.x - 20)
        elif ent == ctrl.get("DERECHA"): self.x = min(485, self.x + 20)
        if random.random() < 0.08: self.obs.append([random.randint(280, 480), -60])
        for o in self.obs[:]:
            o[1] += self.v
            if 330 < o[1] < 380 and abs(self.x - o[0]) < 35: return True
            if o[1] > 400: self.obs.remove(o)
        return False
    def dibujar(self, sc):
        sc.fill((50, 100, 50))
        pygame.draw.rect(sc, (40, 40, 40), (250, 0, 300, 400)) 
        for i in range(-100, 500, 100): pygame.draw.rect(sc, (255, 255, 255), (395, i + self.offset, 10, 45))
        pygame.draw.rect(sc, (0, 150, 255), (self.x-12, 330, 24, 50), border_radius=3)
        pygame.draw.rect(sc, (255, 255, 255), (self.x-25, 335, 50, 8))
        pygame.draw.rect(sc, (255, 255, 255), (self.x-25, 365, 50, 8))
        for o in self.obs: pygame.draw.rect(sc, (200, 50, 50), (o[0]-15, o[1], 30, 45), border_radius=5)

class JuegoPacman:
    def __init__(self):
        self.mapa = generar_laberinto()
        self.px, self.py = 0, 0; self.pts = []
        for r in range(8):
            for c in range(8):
                if self.mapa[r][c] == 0: self.pts.append([r, c])
        self.fantasmas = [{'x':7.0, 'y':7.0, 'c':(255,50,50)}]
    def actualizar(self, ent, ctrl):
        nx, ny = self.px, self.py
        if ent == ctrl.get("IZQUIERDA"): ny -= 1
        elif ent == ctrl.get("DERECHA"): ny += 1
        elif ent == ctrl.get("ARRIBA"): nx -= 1
        elif ent == ctrl.get("ABAJO"): nx += 1
        if 0 <= nx < 8 and 0 <= ny < 8 and self.mapa[nx][ny] == 0:
            self.px, self.py = nx, ny
        if [self.px, self.py] in self.pts: self.pts.remove([self.px, self.py])
        f = self.fantasmas[0]
        if random.random() < 0.15:
            if f['x'] < self.px: f['x'] += 1
            elif f['x'] > self.px: f['x'] -= 1
            if f['y'] < self.py: f['y'] += 1
            elif f['y'] > self.py: f['y'] -= 1
        return len(self.pts) == 0 or (int(f['x']) == self.px and int(f['y']) == self.py)
    def dibujar(self, sc):
        sc.fill((0, 0, 20))
        for r in range(8):
            for c in range(8):
                if self.mapa[r][c] == 1: pygame.draw.rect(sc, (0, 0, 200), (240+c*40, 40+r*40, 38, 38), 2, border_radius=5)
        for p in self.pts: pygame.draw.circle(sc, (255, 255, 255), (240+p[1]*40+20, 40+p[0]*40+20), 4)
        pygame.draw.circle(sc, (255, 255, 0), (240+self.py*40+20, 40+self.px*40+20), 16)
        f = self.fantasmas[0]
        pygame.draw.circle(sc, f['c'], (240+int(f['y'])*40+20, 40+int(f['x'])*40+20), 16)

# ==========================================
# CONSOLA PRINCIPAL
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        
        # Detector dinámico de mandos
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
            print(f"Conectado a: {self.joy.get_name()}")

        # Modo Maximizado para Raspberry
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("B-Botgotchi - Pablo Alí")
        self.clock = pygame.time.Clock(); self.running = True
        
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.indice_cfg = 0
        self.modo = "MENU" if os.path.exists(CONFIG_FILE) else "CONFIG"
        if self.modo == "MENU":
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0; self.sel_juego = 0; self.sub_modo = "MENU_JUEGOS"
        self.juego_actual = None; self.texto_chiste = ""

    def run(self):
        while self.running:
            self.screen.fill(COLOR_FONDO)
            t = pygame.time.get_ticks()
            entrada = None
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
                entrada = self.obtener_entrada(event)

            # --- CONFIGURACIÓN CON ESPERA ---
            if self.modo == "CONFIG":
                self.mostrar_texto("NUEVO MANDO DETECTADO", y=60, color=COLOR_TEXTO_DARK, size=30)
                self.mostrar_texto(f"PABLO, PULSA Y SUELTA:", y=180, color=(100,100,100), size=20)
                self.mostrar_texto(self.pasos_config[self.indice_cfg], y=240, color=(255, 50, 50), size=45)
                
                if entrada:
                    self.controles[self.pasos_config[self.indice_cfg]] = entrada
                    self.indice_cfg += 1
                    
                    # Ciclo de espera para soltar botón
                    esperando = True
                    while esperando:
                        for ev in pygame.event.get():
                            if ev.type == pygame.JOYBUTTONUP or (ev.type == pygame.JOYHATMOTION and ev.value == (0,0)):
                                esperando = False
                            if ev.type == pygame.JOYAXISMOTION and abs(ev.value) < 0.2:
                                esperando = False
                        pygame.display.flip()
                        self.clock.tick(30)
                    
                    if self.indice_cfg >= len(self.pasos_config):
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                        self.modo = "MENU"

            # --- MENÚ PRINCIPAL ---
            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    c = (255, 255, 255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    self.mostrar_texto(opt, 40+i*190+85, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                
                if entrada == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                elif entrada == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                elif entrada == self.controles.get("A"): self.modo = self.opciones[self.seleccion]

            # --- SISTEMA DE JUEGOS ---
            elif self.modo == "JUGAR":
                if entrada == self.controles.get("L"): # Botón de escape
                    self.sub_modo = "MENU_JUEGOS"; self.juego_actual = None; self.modo = "MENU"
                
                if self.sub_modo == "MENU_JUEGOS":
                    self.mostrar_texto("ARCADE CENTER", y=40, color=COLOR_TEXTO_DARK, size=35)
                    juegos = ["NAVES", "CARRERAS", "PAC-MAN", "LABERINTO"]
                    for i, jg in enumerate(juegos):
                        col = (255, 100, 0) if self.sel_juego == i else (100, 100, 120)
                        self.mostrar_texto(jg, y=120+i*55, color=col, size=28)
                    if entrada == self.controles.get("ABAJO"): self.sel_juego = (self.sel_juego+1)%4
                    elif entrada == self.controles.get("ARRIBA"): self.sel_juego = (self.sel_juego-1)%4
                    elif entrada == self.controles.get("A"):
                        if self.sel_juego == 0: self.juego_actual = JuegoNaves()
                        elif self.sel_juego == 1: self.juego_actual = JuegoCarreras()
                        elif self.sel_juego == 2: self.juego_actual = JuegoPacman()
                        elif self.sel_juego == 3: 
                             from utils import JuegoLaberintoOriginal
                             self.juego_actual = JuegoLaberintoOriginal()
                        self.sub_modo = "JUGANDO"
                else:
                    if self.juego_actual.actualizar(entrada, self.controles): 
                        self.sub_modo = "MENU_JUEGOS"
                    self.juego_actual.dibujar(self.screen)

            # --- CHISTES ---
            elif self.modo == "CHISTES":
                if entrada == self.controles.get("L"): self.modo = "MENU"
                self.dibujar_bot(t)
                if not self.texto_chiste or entrada == self.controles.get("A"):
                    self.texto_chiste = obtener_chiste()
                self.mostrar_texto(self.texto_chiste, y=260, color=COLOR_TEXTO_DARK, size=20)

            pygame.display.flip()
            self.clock.tick(60)

    def obtener_entrada(self, event):
        if event.type == pygame.JOYBUTTONDOWN: return {"tipo": "btn", "val": event.button}
        if event.type == pygame.JOYHATMOTION and event.value != (0,0): return {"tipo": "hat", "val": list(event.value)}
        if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.6: 
            return {"tipo": "axis", "val": [event.axis, 1 if event.value > 0 else -1]}
        return None

    def mostrar_texto(self, txt, x=400, y=200, color=(255,255,255), size=22):
        font = pygame.font.SysFont("Arial", size, True)
        s = font.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

    def dibujar_bot(self, t):
        f = math.sin(t * 0.005) * 12
        pygame.draw.rect(self.screen, (255,255,255), (350, 100+f, 100, 110), border_radius=25)
        # Rostro o _ o
        pygame.draw.circle(self.screen, (0,0,0), (380, 135+f), 8)
        pygame.draw.circle(self.screen, (0,0,0), (420, 135+f), 8)
        pygame.draw.rect(self.screen, (0,0,0), (385, 155+f, 30, 4), border_radius=2)

if __name__ == "__main__":
    BBotConsola().run()
