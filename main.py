import pygame
import json
import os
import time
import math
import random

# --- CONFIGURACIÓN DE PANTALLA ---
ANCHO, ALTO = 800, 400
COLOR_FONDO = (173, 216, 230) 
CONFIG_FILE = "config_pablo.json"
FUENTE_RETRO = "Courier New"

# --- CONTENIDO DE TEXTO ---
CUENTOS = [
    ["El Caballero de la E", 
     "Había una vez un valiente piloto llamado Pablo Alí que viajaba en una nave con forma de letra E.",
     "Un día, cruzó un portal de estrellas y llegó a un planeta donde los UFOs tenían cúpulas de cristal.",
     "Con su puntería láser, logró proteger a los robots locales y se convirtió en el héroe del sector 100."],
    ["Los Túneles Mágicos",
     "Pac-Man descubrió que las paredes de su mundo tenían secretos: si caminaba hacia la izquierda total...",
     "¡Aparecía mágicamente por la derecha! Engañó a los dos fantasmas que lo perseguían sin descanso.",
     "Desde ese día, usa los atajos para comer todas las frutas y ganar muchos puntos."]
]

CHISTES = ["¿Qué le dice un cable a otro?... ¡Somos los elegidos!", "¿Qué hace un pez en el cine?... ¡Nada!", "Había una vez un perro que se llamaba Chiste, se cayó y... ¡se acabó el chiste!"]

# --- FUNCIONES DE APOYO ---
def envolver_texto(texto, fuente, ancho_max):
    palabras = texto.split(' ')
    lineas = []; linea_act = ""
    for p in palabras:
        if fuente.size(linea_act + p)[0] < ancho_max: linea_act += p + " "
        else: lineas.append(linea_act); linea_act = p + " "
    lineas.append(linea_act)
    return lineas

def mapa_arcade():
    return [
        [1,1,1,1,1,1,0,1,1,1,1,1,1,1,1], # Túnel Arriba
        [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
        [0,0,1,1,1,0,1,1,1,0,1,1,1,0,0], # Túneles Laterales
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,0,1,1,0,1,0,1,1,0,1,1,1],
        [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0], # Túneles Laterales
        [1,0,1,1,1,1,0,0,0,1,1,1,1,0,1],
        [1,1,1,1,1,1,0,1,1,1,1,1,1,1,1]  # Túnel Abajo
    ]

# ==========================================
# CLASES DE JUEGOS
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []; self.puntos = 0; self.vidas = 3
        self.colores = [(0,200,255), (0,255,100), (200,100,255), (255,150,0)]
    def actualizar(self, ent, ctrl):
        if ent == ctrl.get("IZQUIERDA"): self.x = max(30, self.x - 40)
        elif ent == ctrl.get("DERECHA"): self.x = min(770, self.x + 40)
        elif ent == ctrl.get("X"): self.balas.append([self.x, 340])
        if random.random() < 0.08:
            c = self.colores[(self.puntos//100)%len(self.colores)]
            self.enemigos.append([random.randint(50,750), -40, c])
        for b in self.balas[:]:
            b[1] -= 15
            if b[1] < 0: self.balas.remove(b)
        for e in self.enemigos[:]:
            e[1] += (5 + self.puntos//100)
            for b in self.balas[:]:
                if abs(e[0]-b[0])<30 and abs(e[1]-b[1])<30:
                    self.enemigos.remove(e); self.balas.remove(b); self.puntos += 10; break
            if e[1] > 340 and abs(e[0]-self.x) < 40:
                self.vidas -= 1; self.enemigos = []; return self.vidas <= 0
            elif e[1] > 400: self.enemigos.remove(e)
        return False
    def dibujar(self, sc):
        sc.fill((10,10,30))
        c = self.colores[(self.puntos//100)%len(self.colores)]
        pygame.draw.rect(sc, c, (self.x-20, 350, 40, 10)) # Base E
        pygame.draw.rect(sc, c, (self.x-20, 335, 8, 15)); pygame.draw.rect(sc, c, (self.x+12, 335, 8, 15))
        pygame.draw.rect(sc, (255,255,255), (self.x-2, 330, 4, 20)) # Cañón
        for e in self.enemigos:
            pygame.draw.ellipse(sc, e[2], (e[0]-22, e[1]-10, 44, 22))
            pygame.draw.circle(sc, (200,255,255), (e[0], e[1]-5), 8) # Cúpula
        for b in self.balas: pygame.draw.rect(sc, (255,255,0), (b[0]-2, b[1], 4, 10))
        f = pygame.font.SysFont(FUENTE_RETRO, 20, True)
        sc.blit(f.render(f"PUNTOS: {self.puntos} - VIDAS: {self.vidas}", True, (255,255,255)), (20,20))

class JuegoCarreras:
    def __init__(self):
        self.x = 400; self.obs = []; self.v = 5; self.vidas = 3; self.flash = 0
    def actualizar(self, ent, ctrl):
        if self.flash > 0: self.flash -= 1
        joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if joy:
            if joy.get_button(ctrl.get("A", {}).get("val", 0)): self.v = min(20, self.v + 0.5)
            elif joy.get_button(ctrl.get("B", {}).get("val", 1)): self.v = max(0, self.v - 1)
            else: self.v = max(5, self.v - 0.2)
        if ent == ctrl.get("IZQUIERDA"): self.x = max(200, self.x - 30)
        elif ent == ctrl.get("DERECHA"): self.x = min(600, self.x + 30)
        if random.random() < 0.07: self.obs.append([random.randint(210, 590), -60, (255,100,0)])
        for o in self.obs[:]:
            o[1] += int(self.v + 4)
            if 320 < o[1] < 380 and abs(self.x - o[0]) < 40:
                self.vidas -= 1; self.flash = 15; self.obs = []; self.v = 5
            elif o[1] > 400: self.obs.remove(o)
        return self.vidas <= 0
    def dibujar(self, sc):
        sc.fill((34, 139, 34))
        pygame.draw.rect(sc, (100, 100, 100), (180, 0, 440, 400)) # Carretera Gris Claro
        pygame.draw.rect(sc, (255, 255, 255), (395, 0, 10, 400))
        if self.flash > 0: sc.fill((200, 0, 0), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(sc, (200,0,0), (self.x-20, 330, 40, 60), border_radius=6) # Carro
        pygame.draw.rect(sc, (150,200,255), (self.x-12, 345, 24, 12)) # Vidrio
        for o in self.obs: pygame.draw.rect(sc, o[2], (o[0]-20, o[1], 40, 60), border_radius=6)
        f = pygame.font.SysFont(FUENTE_RETRO, 25 if self.flash > 0 else 20, True)
        sc.blit(f.render(f"VIDAS: {self.vidas}", True, (255,255,255)), (20,20))

class JuegoPacman:
    def __init__(self):
        self.mapa = mapa_arcade(); self.px, self.py = 1, 1; self.vidas = 3; self.puntos = 0
        self.fantasmas = [{'x': 6, 'y': 13, 'c': (255,0,0)}, {'x': 1, 'y': 13, 'c': (255,182,193)}]
        self.pts = [[r, c] for r in range(8) for c in range(15) if self.mapa[r][c] == 0]
    def actualizar(self, ent, ctrl):
        nx, ny = self.px, self.py
        if ent == ctrl.get("IZQUIERDA"): ny -= 1
        elif ent == ctrl.get("DERECHA"): ny += 1
        elif ent == ctrl.get("ARRIBA"): nx -= 1
        elif ent == ctrl.get("ABAJO"): nx += 1
        # Túneles
        if ny < 0: ny = 14
        elif ny > 14: ny = 0
        if nx < 0: nx = 7
        elif nx > 7: nx = 0
        if self.mapa[nx][ny] == 0: self.px, self.py = nx, ny
        if [self.px, self.py] in self.pts: self.pts.remove([self.px, self.py]); self.puntos += 10
        for f in self.fantasmas:
            if random.random() < 0.2: # IA simple
                dx = 1 if f['x'] < self.px else -1 if f['x'] > self.px else 0
                dy = 1 if f['y'] < self.py else -1 if f['y'] > self.py else 0
                if dx != 0 and self.mapa[int(f['x']+dx)][int(f['y'])] == 0: f['x'] += dx
                elif dy != 0 and self.mapa[int(f['x'])][int(f['y']+dy)] == 0: f['y'] += dy
            if int(f['x']) == self.px and int(f['y']) == self.py:
                self.vidas -= 1; self.px, self.py = 1, 1; return self.vidas <= 0
        return False
    def dibujar(self, sc):
        sc.fill((0,0,20))
        for r in range(8):
            for c in range(15):
                x, y = 25+c*50, 10+r*50
                if self.mapa[r][c] == 1: pygame.draw.rect(sc, (0,50,180), (x+5, y+5, 40, 40), border_radius=8)
                elif [r,c] in self.pts: pygame.draw.circle(sc, (255,255,200), (x+25, y+25), 4)
        px, py = 25+self.py*50+25, 10+self.px*50+25
        pygame.draw.circle(sc, (255,255,0), (px, py), 18) # Pacman
        pygame.draw.circle(sc, (0,0,0), (px+5, py-8), 3) # Ojo
        for f in self.fantasmas:
            fx, fy = 25+f['y']*50+12, 10+f['x']*50+12
            pygame.draw.circle(sc, f['c'], (fx+13, fy+13), 15) # Cabeza U
            pygame.draw.rect(sc, f['c'], (fx-2, fy+13, 30, 15))
            pygame.draw.circle(sc, (255,255,255), (fx+7, fy+10), 4); pygame.draw.circle(sc, (255,255,255), (fx+19, fy+10), 4)

# ==========================================
# CONSOLA CENTRAL
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joy: self.joy.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        else: self.modo = "CONFIG"
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.idx_cfg = 0; self.seleccion = 0; self.item_idx = 0; self.linea_idx = 0; self.juego = None
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]

    def run(self):
        while self.running:
            self.screen.fill(COLOR_FONDO); t = pygame.time.get_ticks(); ent = None
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                if ev.type == pygame.JOYBUTTONDOWN: ent = {"tipo": "btn", "val": ev.button}
                if ev.type == pygame.JOYHATMOTION and ev.value != (0,0): ent = {"tipo": "hat", "val": list(ev.value)}
            
            if ent == self.controles.get("L"): self.modo = "MENU"; self.juego = None

            if self.modo == "CONFIG":
                self.mostrar_t(f"PULSA: {self.pasos_cfg[self.idx_cfg]}", y=200, size=40)
                if ent: 
                    self.controles[self.pasos_cfg[self.idx_cfg]] = ent
                    self.idx_cfg += 1; time.sleep(0.2)
                    if self.idx_cfg >= len(self.pasos_cfg):
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                        self.modo = "MENU"

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    self.mostrar_t(opt, 40+i*190+85, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if ent == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                elif ent == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                elif ent == self.controles.get("A"): self.modo = self.opciones[self.seleccion]; self.item_idx=0; self.linea_idx=0

            elif self.modo == "JUGAR":
                if not self.juego:
                    self.mostrar_t("A: NAVES | B: CARROS | X: PACMAN", y=200, size=30)
                    if ent == self.controles.get("A"): self.juego = JuegoNaves()
                    elif ent == self.controles.get("B"): self.juego = JuegoCarreras()
                    elif ent == self.controles.get("X"): self.juego = JuegoPacman()
                else:
                    if self.juego.actualizar(ent, self.controles): self.juego = None
                    else: self.juego.dibujar(self.screen)

            elif self.modo == "CUENTOS":
                self.dibujar_bot(t, x=680)
                rect = pygame.Rect(40, 40, 520, 320)
                pygame.draw.rect(self.screen, (255,255,240), rect, border_radius=15)
                pygame.draw.rect(self.screen, (100,80,60), rect, 3, border_radius=15)
                c = CUENTOS[self.item_idx]; f_c = pygame.font.SysFont(FUENTE_RETRO, 18)
                self.mostrar_t(c[0], 300, 60, (150,0,0), 28)
                lineas = envolver_texto(c[self.linea_idx+1], f_c, 480)
                for i, l in enumerate(lineas): self.screen.blit(f_c.render(l, True, (0,0,0)), (60, 110+i*25))
                if ent == self.controles.get("A"):
                    self.linea_idx += 1
                    if self.linea_idx >= len(c)-1: self.linea_idx=0; self.item_idx=(self.item_idx+1)%len(CUENTOS)

            elif self.modo == "CHISTES":
                self.dibujar_bot(t, x=150)
                self.mostrar_t(CHISTES[self.item_idx], y=200, color=(0,0,0), size=20)
                if ent == self.controles.get("A"): self.item_idx = (self.item_idx+1)%len(CHISTES)

            pygame.display.flip(); self.clock.tick(60)

    def mostrar_t(self, txt, x=400, y=200, color=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

    def dibujar_bot(self, t, x=400):
        f = math.sin(t * 0.005) * 12
        pygame.draw.rect(self.screen, (255,255,255), (x-50, 100+f, 100, 110), border_radius=25)
        pygame.draw.circle(self.screen, (0,0,0), (x-20, 135+f), 8); pygame.draw.circle(self.screen, (0,0,0), (x+20, 135+f), 8)
        pygame.draw.rect(self.screen, (0,0,0), (x-15, 155+f, 30, 4), border_radius=2)

if __name__ == "__main__":
    BBotConsola().run()
