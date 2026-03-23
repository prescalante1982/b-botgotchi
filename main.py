import pygame
import json
import os
import time
import math
import random

# --- CONFIGURACIÓN ESTÉTICA ---
ANCHO, ALTO = 800, 400
CELESTE_CIELO = (173, 216, 230)
NEGRO_ESPACIO = (10, 10, 30)
CONFIG_FILE = "config_pablo.json"
FUENTE_RETRO = "Courier New"

# ==========================================
# LÓGICA DE JUEGOS
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []; self.puntos = 0; self.vidas = 3
        self.estrellas = [[random.randint(0, 800), random.randint(0, 400), random.random()] for _ in range(60)]
    def actualizar(self, accion):
        if accion == "IZQUIERDA": self.x = max(30, self.x - 45)
        elif accion == "DERECHA": self.x = min(770, self.x + 45)
        elif accion == "X": self.balas.append([self.x, 340])
        if random.random() < 0.08: self.enemigos.append([random.randint(50,750), -40])
        for b in self.balas[:]:
            b[1] -= 20
            if b[1] < 0: self.balas.remove(b)
        for e in self.enemigos[:]:
            e[1] += (6 + self.puntos//100)
            if e[1] > 330 and abs(e[0]-self.x) < 40:
                self.vidas -= 1; self.enemigos = []; return self.vidas <= 0
            for b in self.balas[:]:
                if abs(e[0]-b[0])<30 and abs(e[1]-b[1])<30:
                    if e in self.enemigos: self.enemigos.remove(e)
                    self.balas.remove(b); self.puntos += 10; break
            if e[1] > 400: self.enemigos.remove(e)
        return False
    def dibujar(self, sc):
        sc.fill(NEGRO_ESPACIO)
        for s in self.estrellas: 
            s[0] = (s[0] - s[2]*2) % 800
            pygame.draw.circle(sc, (255,255,255), (int(s[0]), s[1]), 1)
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 350, 40, 10))
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 335, 8, 15))
        pygame.draw.rect(sc, (0,200,255), (self.x+12, 335, 8, 15))
        pygame.draw.rect(sc, (255,255,255), (self.x-2, 330, 4, 20))
        for e in self.enemigos:
            pygame.draw.ellipse(sc, (200,100,255), (e[0]-22, e[1]-10, 44, 22))
            pygame.draw.circle(sc, (200,255,255), (e[0], e[1]-5), 8)
        for b in self.balas: pygame.draw.rect(sc, (255,255,0), (b[0]-2, b[1], 4, 10))
        self.HUD(sc)
    def HUD(self, sc):
        f = pygame.font.SysFont(FUENTE_RETRO, 18, True)
        sc.blit(f.render(f"PUNTOS: {self.puntos}", True, (255,255,255)), (20, 20))
        sc.blit(f.render(f"VIDAS: {self.vidas}", True, (255,50,50)), (680, 20))

class JuegoCarreras:
    def __init__(self):
        self.x = 400; self.obs = []; self.v = 5; self.vidas = 3; self.puntos = 0; self.flash = 0
    def actualizar(self, accion):
        if self.flash > 0: self.flash -= 1
        if accion == "IZQUIERDA": self.x = max(200, self.x - 35)
        elif accion == "DERECHA": self.x = min(600, self.x + 35)
        if random.random() < 0.07: self.obs.append([random.randint(210, 590), -100])
        for o in self.obs[:]:
            o[1] += int(self.v + 3); self.puntos += 1
            if 310 < o[1] < 385 and abs(self.x - o[0]) < 45:
                self.vidas -= 1; self.flash = 15; self.obs = []; self.v = 5
            elif o[1] > 450: self.obs.remove(o)
        return self.vidas <= 0
    def dibujar(self, sc):
        sc.fill((34, 139, 34))
        pygame.draw.rect(sc, (110, 110, 110), (180, 0, 440, 400))
        pygame.draw.rect(sc, (255, 255, 255), (395, 0, 10, 400))
        if self.flash > 0: sc.fill((200, 0, 0), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(sc, (200, 0, 0), (self.x-20, 330, 40, 60), border_radius=6)
        pygame.draw.rect(sc, (150, 200, 255), (self.x-12, 345, 24, 12))
        for o in self.obs: pygame.draw.rect(sc, (255,140,0), (o[0]-20, o[1], 40, 60), border_radius=6)
        f = pygame.font.SysFont(FUENTE_RETRO, 18, True)
        sc.blit(f.render(f"KM: {self.puntos//10}", True, (255,255,255)), (20, 20))

class JuegoPacman:
    def __init__(self):
        self.mapa = [[1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],[0,0,1,1,1,0,1,1,1,0,1,1,1,0,0],[1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],[1,0,1,1,1,1,0,0,0,1,1,1,1,0,1],[1,1,1,1,1,1,0,1,1,1,1,1,1,1,1]]
        self.px, self.py = 1, 1; self.pts = [[r, c] for r in range(7) for c in range(15) if self.mapa[r][c] == 0]
    def actualizar(self, accion):
        nx, ny = self.px, self.py
        if accion == "IZQUIERDA": ny -= 1
        elif accion == "DERECHA": ny += 1
        elif accion == "ARRIBA": nx -= 1
        elif accion == "ABAJO": nx += 1
        if ny < 0: ny = 14
        elif ny > 14: ny = 0
        if 0 <= nx < 7 and self.mapa[nx][ny] == 0: self.px, self.py = nx, ny
        if [self.px, self.py] in self.pts: self.pts.remove([self.px, self.py])
        return len(self.pts) == 0
    def dibujar(self, sc):
        sc.fill((0,0,30))
        for r in range(7):
            for c in range(15):
                if self.mapa[r][c] == 1: pygame.draw.rect(sc, (0,80,255), (25+c*50+5, 25+r*50+5, 40, 40), border_radius=10)
                elif [r,c] in self.pts: pygame.draw.circle(sc, (255,255,200), (25+c*50+25, 25+r*50+25), 4)
        pygame.draw.circle(sc, (255,255,0), (25+self.py*50+25, 25+self.px*50+25), 20)

# ==========================================
# CONSOLA PRINCIPAL B-BOT
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()
        
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED)
        pygame.display.set_caption("B-Bot Consola")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.idx_cfg = 0

        if not os.path.exists(CONFIG_FILE): 
            self.modo = "CONFIG"
        else:
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.seleccion = 0; self.sel_juego = 0; self.juego = None
        
        # --- Configuración de Cuentos Dinámicos ---
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.tales_dir = os.path.join(self.base_path, "tales")
        if not os.path.exists(self.tales_dir):
            os.makedirs(self.tales_dir)
        
        self.lista_cuentos = []
        self.idx_cuento = 0
        self.paginas_cuento = []
        self.pagina_actual = 0
    
    def obtener_accion(self, ev):
        if not self.controles: return None
        for accion, m in self.controles.items():
            if ev.type == pygame.JOYBUTTONDOWN and m.get("tipo") == "btn" and ev.button == m["val"]: return accion
            if ev.type == pygame.JOYHATMOTION and m.get("tipo") == "hat" and list(ev.value) == m["val"]: return accion
            if ev.type == pygame.JOYAXISMOTION and m.get("tipo") == "axis" and ev.axis == m["axis
