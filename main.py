import pygame
import json
import os
import time
import math
import random
from utils import obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (15, 15, 30)
COLOR_NEON = (0, 255, 200)
COLOR_TEXTO = (255, 255, 255)
CONFIG_FILE = "config_pablo.json"
TALES_DIR = ".tales"

# ==========================================
# 1. CLASES DE JUEGOS (LOS "CARTUCHOS")
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []; self.score = 0
        self.estrellas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(25)]
    def actualizar(self, ent, ctrl):
        for s in self.estrellas: s[1] = (s[1] + 3) % 400
        if ent == ctrl.get("IZQUIERDA"): self.x = max(50, self.x - 35)
        elif ent == ctrl.get("DERECHA"): self.x = min(750, self.x + 35)
        elif ent == ctrl.get("A"): self.balas.append([self.x, 350])
        for b in self.balas[:]:
            b[1] -= 15
            if b[1] < 0: self.balas.remove(b)
        if random.random() < 0.08: self.enemigos.append({'x': random.randint(50, 750), 'y': -20})
        for e in self.enemigos[:]:
            e['y'] += 6
            for b in self.balas[:]:
                if abs(e['x'] - b[0]) < 25 and abs(e['y'] - b[1]) < 25:
                    self.enemigos.remove(e); self.balas.remove(b); self.score += 10
            if e['y'] > 400: return True
        return False
    def dibujar(self, sc):
        for s in self.estrellas: pygame.draw.circle(sc, (100, 100, 150), s, 1)
        pygame.draw.polygon(sc, COLOR_NEON, [(self.x, 340), (self.x-20, 370), (self.x+20, 370)])
        for b in self.balas: pygame.draw.line(sc, (255, 255, 0), (b[0], b[1]), (b[0], b[1]-10), 3)
        for e in self.enemigos: pygame.draw.rect(sc, (255, 50, 100), (e['x']-15, e['y']-15, 30, 30), border_radius=8)

class JuegoCarreras:
    def __init__(self):
        self.x = 380; self.obs = []; self.v = 8; self.offset = 0
    def actualizar(self, ent, ctrl):
        if ent == ctrl.get("IZQUIERDA"): self.x = max(270, self.x - 30)
        elif ent == ctrl.get("DERECHA"): self.x = min(490, self.x + 30)
        self.offset = (self.offset + self.v) % 100
        if random.random() < 0.1: self.obs.append([random.randint(280, 480), -50])
        for o in self.obs[:]:
            o[1] += self.v
            if 330 < o[1] < 380 and abs(self.x - o[0]) < 35: return True
            if o[1] > 400: self.obs.remove(o); self.v += 0.05
        return False
    def dibujar(self, sc):
        pygame.draw.rect(sc, (40, 40, 40), (250, 0, 300, 400))
        for i in range(-100, 400, 100): pygame.draw.rect(sc, (200, 200, 200), (395, i + self.offset, 10, 40))
        pygame.draw.rect(sc, (0, 150, 255), (self.x-20, 330, 40, 60), border_radius=5)
        for o in self.obs: pygame.draw.rect(sc, (255, 50, 50), (o[0]-20, o[1], 40, 50), border_radius=5)

class JuegoPacman:
    def __init__(self):
        self.px, self.py = 4, 4; self.pts = [[1,1], [1,6], [6,1], [6,6], [3,3], [2,4], [5,2]]
        self.fantasmas = [{'x':1, 'y':1, 'c':(255,0,0)}, {'x':6, 'y':6, 'c':(0,255,255)}]
    def actualizar(self, ent, ctrl):
        if ent == ctrl.get("IZQUIERDA"): self.py = max(0, self.py-1)
        elif ent == ctrl.get("DERECHA"): self.py = min(7, self.py+1)
        elif ent == ctrl.get("ARRIBA"): self.px = max(0, self.px-1)
        elif ent == ctrl.get("ABAJO"): self.px = min(7, self.px+1)
        if [self.px, self.py] in self.pts: self.pts.remove([self.px, self.py])
        for f in self.fantasmas:
            if random.random() < 0.2:
                f['x'] += 1 if f['x'] < self.px else -1
                f['y'] += 1 if f['y'] < self.py else -1
            if f['x'] == self.px and f['y'] == self.py: return True
        return len(self.pts) == 0
    def dibujar(self, sc):
        for r in range(8):
            for c in range(8): pygame.draw.rect(sc, (0, 0, 80), (240+c*40, 40+r*40, 40, 40), 1)
        for p in self.pts: pygame.draw.circle(sc, (255,255,200), (240+p[1]*40+20, 40+p[0]*40+20), 4)
        pygame.draw.circle(sc, (255,255,0), (240+self.py*40+20, 40+self.px*40+20), 16)
        for f in self.fantasmas: pygame.draw.circle(sc, f['c'], (240+f['y']*40+20, 40+f['x']*40+20), 16)

class JuegoLaberinto:
    def __init__(self):
        self.mapa = generar_laberinto(); self.px = self.py = 0
    def actualizar(self, ent, ctrl):
        nx, ny = self.px, self.py
        if ent == ctrl.get("IZQUIERDA"): ny -= 1
        elif ent == ctrl.get("DERECHA"): ny += 1
        elif ent == ctrl.get("ARRIBA"): nx -= 1
        elif ent == ctrl.get("ABAJO"): nx += 1
        if 0 <= nx < 8 and 0 <= ny < 8 and self.mapa[nx][ny] == 0: self.px, self.py = nx, ny
        return (self.px == 7 and self.py == 7)
    def dibujar(self, sc):
        for r in range(8):
            for c in range(8):
                col = (40,40,70) if self.mapa[r][c] == 1 else (200,200,200)
                pygame.draw.rect(sc, col, (240+c*40, 40+r*40, 38, 38), border_radius=4)
        pygame.draw.circle(sc, COLOR_NEON, (240+self.py*40+20, 40+self.px*40+20), 14)

# ==========================================
# 2. LA CONSOLA (EL CEREBRO PRINCIPAL)
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
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            self.modo = "MENU"
        else: self.modo = "CONFIG"

        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.juegos_lista = ["NAVES", "CARRERAS", "PAC-MAN", "LABERINTO"]
        self.sel_juego = 0; self.sub_modo = "MENU_JUEGOS"; self.juego_actual = None
        
        self.hambre = 50; self.energia = 50; self.estado_bot = "NORMAL"; self.timer_emo = 0
        self.lista_cuentos = []; self.sel_cuento_idx = 0; self.lineas_render = []; self.scroll_y = 0; self.modo_lectura = "LISTA"

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            if time.time() > self.timer_emo: self.estado_bot = "NORMAL"
            self.screen.fill(COLOR_FONDO)

            if self.modo == "CONFIG":
                self.mostrar_texto("CONFIGURACIÓN", y=60, color=COLOR_NEON, size=30)
                self.mostrar_texto(f"PABLO, PRESIONA: {self.pasos_config[self.indice_cfg]}", y=180, size=28)

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    c = (255,200,0) if self.seleccion == i else (60,60,90)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    self.mostrar_texto(opt, 40+i*190+85, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)

            elif self.modo == "JUGAR":
                if self.sub_modo == "MENU_JUEGOS":
                    self.mostrar_texto("ARCADE PABLO ALÍ", y=40, color=COLOR_NEON, size=30)
                    for i, jg in enumerate(self.juegos_lista):
                        col = (255,255,0) if self.sel_juego == i else (150,150,150)
                        self.mostrar_texto(jg, y=120+i*55, color=col, size=30)
                else:
                    if self.juego_actual: self.juego_actual.dibujar(self.screen)

            elif self.modo == "CHISTES":
                self.dibujar_bot(t); self.mostrar_texto(self.texto_pantalla, y=250, size=20)

            elif self.modo == "CUENTOS":
                self.mostrar_texto("CUENTOS", y=40, color=COLOR_NEON)
                if self.modo_lectura == "LISTA":
                    for i, cto in enumerate(self.lista_cuentos):
                        col = (255,255,0) if self.sel_cuento_idx == i else (150,150,150)
                        self.mostrar_texto(cto.replace(".txt","").upper(), y=120+i*40, color=col)
                else:
                    rect = pygame.Rect(280, 40, 480, 320)
                    pygame.draw.rect(self.screen, (30,30,60), rect, border_radius=15)
                    f_c = pygame.font.SysFont("Arial", 20)
                    for i, lin in enumerate(self.lineas_render):
                        yp = 60 + (i*28) - (self.scroll_y*28)
                        if 50 < yp < 330: self.screen.blit(f_c.render(lin.strip(), True, COLOR_TEXTO), (300, yp))

            # --- EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                ent = self.obtener_entrada(event)
                if not ent: continue

                if ent == self.controles.get("R") and self.modo == "MENU": 
                    self.modo = self.opciones[self.seleccion]; self.sub_modo = "MENU_JUEGOS"
                    if self.modo == "CUENTOS": self.lista_cuentos = os.listdir(TALES_DIR)
                    if self.modo == "CHISTES": self.texto_pantalla = obtener_chiste()
                if ent == self.controles.get("L"): self.modo = "MENU"

                if self.modo == "CONFIG":
                    self.controles[self.pasos_config[self.indice_cfg]] = ent
                    self.indice_cfg += 1
                    if self.indice_cfg >= len(self.pasos_config):
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                        self.modo = "MENU"
                    pygame.time.wait(500)

                elif self.modo == "MENU":
                    if ent == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                    elif ent == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                    elif ent == self.controles.get("A"): 
                        self.modo = self.opciones[self.seleccion]
                        if self.modo == "CUENTOS": self.lista_cuentos = os.listdir(TALES_DIR)
                        if self.modo == "CHISTES": self.texto_pantalla = obtener_chiste()

                elif self.modo == "JUGAR":
                    if self.sub_modo == "MENU_JUEGOS":
                        if ent == self.controles.get("ABAJO"): self.sel_juego = (self.sel_juego+1)%len(self.juegos_lista)
                        elif ent == self.controles.get("ARRIBA"): self.sel_juego = (self.sel_juego-1)%len(self.juegos_lista)
                        elif ent == self.controles.get("A"):
                            if self.sel_juego == 0: self.juego_actual = JuegoNaves()
                            elif self.sel_juego == 1: self.juego_actual = JuegoCarreras()
                            elif self.sel_juego == 2: self.juego_actual = JuegoPacman()
                            elif self.sel_juego == 3: self.juego_actual = JuegoLaberinto()
                            self.sub_modo = "JUGANDO"
                    elif self.sub_modo == "JUGANDO":
                        if self.juego_actual.actualizar(ent, self.controles): self.sub_modo = "MENU_JUEGOS"

                elif self.modo == "CUENTOS":
                    if self.modo_lectura == "LISTA":
                        if ent == self.controles.get("ABAJO"): self.sel_cuento_idx = (self.sel_cuento_idx+1)%len(self.lista_cuentos)
                        elif ent == self.controles.get("A"): 
                            self.lineas_render = self.preparar_cuento(self.lista_cuentos[self.sel_cuento_idx])
                            self.modo_lectura = "LEYENDO"; self.scroll_y = 0
                    else:
                        if ent == self.controles.get("ABAJO"): self.scroll_y += 1
                        elif ent == self.controles.get("ARRIBA"): self.scroll_y = max(0, self.scroll_y-1)

            pygame.display.flip(); self.clock.tick(60)

    def obtener_entrada(self, event):
        if event.type == pygame.JOYBUTTONDOWN: return {"tipo": "btn", "val": event.button}
        if event.type == pygame.JOYHATMOTION and event.value != (0,0): return {"tipo": "hat", "val": list(event.value)}
        if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.5: 
            return {"tipo": "axis", "val": [event.axis, 1 if event.value > 0 else -1]}
        return None

    def preparar_cuento(self, archivo):
        ruta = os.path.join(TALES_DIR, archivo); lineas = []
        fuente = pygame.font.SysFont("Arial", 22); ancho_max = 440
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                for parrafo in f.read().splitlines():
                    palabras = parrafo.split(' '); actual = ""
                    for p in palabras:
                        if fuente.size(actual + p)[0] < ancho_max: actual += p + " "
                        else: lineas.append(actual); actual = p + " "
                    lineas.append(actual)
            return lineas
        except: return ["Error."]

    def mostrar_texto(self, txt, x=400, y=200, color=COLOR_TEXTO, size=22, centrar=True):
        font = pygame.font.SysFont("Arial", size, True)
        s = font.render(str(txt), True, color)
        pos = (x - s.get_width()//2, y) if centrar else (x, y)
        self.screen.blit(s, pos)

    def dibujar_bot(self, t):
        f = math.sin(t * 0.005) * 10
        pygame.draw.rect(self.screen, (255,255,255), (350, 70+f, 100, 110), border_radius=30)
        pygame.draw.circle(self.screen, COLOR_NEON, (385, 115+f), 8)
        pygame.draw.circle(self.screen, COLOR_NEON, (415, 115+f), 8)

if __name__ == "__main__":
    BBotConsola().run()
