import pygame
import json
import os
import time
import math
import random

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 800, 400
CELESTE_CIELO = (173, 216, 230)
CONFIG_FILE = "config_pablo.json"
FUENTE_RETRO = "Courier New"

# ==========================================
# JUEGOS
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []; self.puntos = 0; self.vidas = 3
        self.estrellas = [[random.randint(0, 800), random.randint(0, 400), random.random()] for _ in range(50)]
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
        sc.fill((10, 10, 30))
        for s in self.estrellas: 
            s[0] = (s[0] - s[2]*2) % 800
            pygame.draw.circle(sc, (255,255,255), (int(s[0]), s[1]), 1)
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 350, 40, 10)) # NAVE E
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 335, 8, 15)); pygame.draw.rect(sc, (0,200,255), (self.x+12, 335, 8, 15))
        pygame.draw.rect(sc, (255,255,255), (self.x-2, 330, 4, 20))
        for e in self.enemigos:
            pygame.draw.ellipse(sc, (200,100,255), (e[0]-22, e[1]-10, 44, 22))
            pygame.draw.circle(sc, (200,255,255), (e[0], e[1]-5), 8)
        for b in self.balas: pygame.draw.rect(sc, (255,255,0), (b[0]-2, b[1], 4, 10))

class JuegoCarreras:
    def __init__(self):
        self.x = 400; self.obs = []; self.v = 5; self.vidas = 3; self.flash = 0
    def actualizar(self, accion):
        if self.flash > 0: self.flash -= 1
        if accion == "IZQUIERDA": self.x = max(200, self.x - 35)
        elif accion == "DERECHA": self.x = min(600, self.x + 35)
        if random.random() < 0.07: self.obs.append([random.randint(210, 590), -100])
        for o in self.obs[:]:
            o[1] += int(self.v + 3)
            if 310 < o[1] < 385 and abs(self.x - o[0]) < 45:
                self.vidas -= 1; self.flash = 12; self.obs = []; self.v = 5
            elif o[1] > 450: self.obs.remove(o)
        return self.vidas <= 0
    def dibujar(self, sc):
        sc.fill((34, 139, 34))
        pygame.draw.rect(sc, (110, 110, 110), (180, 0, 440, 400)) # CARRETERA GRIS
        pygame.draw.rect(sc, (255, 255, 255), (395, 0, 10, 400))
        if self.flash > 0: sc.fill((200, 0, 0), special_flags=pygame.BLEND_ADD)
        pygame.draw.rect(sc, (200, 0, 0), (self.x-20, 330, 40, 60), border_radius=6) # CARRO ROJO
        for o in self.obs: pygame.draw.rect(sc, (255,140,0), (o[0]-20, o[1], 40, 60), border_radius=6)

class JuegoPacman:
    def __init__(self):
        self.mapa = [[1,1,1,1,1,1,0,1,1,1,1,1,1,1,1],[1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],[0,0,1,1,1,0,1,1,1,0,1,1,1,0,0],[1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],[1,0,1,1,1,1,0,0,0,1,1,1,1,0,1],[1,1,1,1,1,1,0,1,1,1,1,1,1,1,1]]
        self.px, self.py = 1, 1; self.vidas = 3; self.dir = "D"; self.frame = 0
        self.pts = [[r, c] for r in range(7) for c in range(15) if self.mapa[r][c] == 0]
    def actualizar(self, accion):
        self.frame += 1; nx, ny = self.px, self.py
        if accion == "IZQUIERDA": ny -= 1; self.dir = "I"
        elif accion == "DERECHA": ny += 1; self.dir = "D"
        elif accion == "ARRIBA": nx -= 1; self.dir = "A"
        elif accion == "ABAJO": nx += 1; self.dir = "B"
        if ny < 0: ny = 14
        elif ny > 14: ny = 0
        if 0 <= nx < 7 and self.mapa[nx][ny] == 0: self.px, self.py = nx, ny
        if [self.px, self.py] in self.pts: self.pts.remove([self.px, self.py])
        return len(self.pts) == 0
    def dibujar(self, sc):
        sc.fill((0,0,20))
        for r in range(7):
            for c in range(15):
                if self.mapa[r][c] == 1: pygame.draw.rect(sc, (0,50,180), (25+c*50+5, 25+r*50+5, 40, 40), border_radius=8)
                elif [r,c] in self.pts: pygame.draw.circle(sc, (255,255,200), (25+c*50+25, 25+r*50+25), 4)
        pygame.draw.circle(sc, (255,255,0), (25+self.py*50+25, 25+self.px*50+25), 18)

# ==========================================
# CONSOLA PRINCIPAL
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        if not os.path.exists(CONFIG_FILE): self.modo = "CONFIG"
        else:
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "L"]
        self.idx_cfg = 0; self.seleccion = 0; self.juego = None

    def detectar_entrada(self, ev):
        if ev.type == pygame.JOYBUTTONDOWN: return {"tipo": "btn", "val": ev.button}
        if ev.type == pygame.JOYHATMOTION and ev.value != (0,0): return {"tipo": "hat", "val": list(ev.value)}
        if ev.type == pygame.JOYAXISMOTION:
            if ev.value > 0.8: return {"tipo": "axis", "axis": ev.axis, "val": 1}
            if ev.value < -0.8: return {"tipo": "axis", "axis": ev.axis, "val": -1}
        return None

    def obtener_accion(self, ev):
        if not self.controles: return None
        for accion, m in self.controles.items():
            if ev.type == pygame.JOYBUTTONDOWN and m.get("tipo") == "btn" and ev.button == m["val"]: return accion
            if ev.type == pygame.JOYHATMOTION and m.get("tipo") == "hat" and list(ev.value) == m["val"]: return accion
            if ev.type == pygame.JOYAXISMOTION and m.get("tipo") == "axis" and ev.axis == m["axis"]:
                if (ev.value > 0.8 and m["val"] == 1) or (ev.value < -0.8 and m["val"] == -1): return accion
        return None

    def run(self):
        while self.running:
            self.screen.fill(CELESTE_CIELO)
            t = pygame.time.get_ticks()
            accion = None
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                if self.modo == "CONFIG":
                    m = self.detectar_entrada(ev)
                    if m:
                        self.controles[self.pasos_cfg[self.idx_cfg]] = m
                        self.idx_cfg += 1
                        pygame.time.delay(500)
                        if self.idx_cfg >= len(self.pasos_cfg):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                else: accion = self.obtener_accion(ev)

            if accion == "L": self.modo = "MENU"; self.juego = None

            if self.modo == "MENU":
                self.dibujar_bot(t)
                opts = ["NAVES", "CARROS", "PACMAN"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (60+i*240, 310, 200, 50), border_radius=15)
                    self.mostrar_t(opt, 60+i*240+100, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if accion == "DERECHA": self.seleccion = (self.seleccion+1)%3
                elif accion == "IZQUIERDA": self.seleccion = (self.seleccion-1)%3
                elif accion == "A":
                    self.modo = "JUGANDO"
                    if self.seleccion == 0: self.juego = JuegoNaves()
                    elif self.seleccion == 1: self.juego = JuegoCarreras()
                    else: self.juego = JuegoPacman()

            elif self.modo == "JUGANDO":
                if self.juego.actualizar(accion): self.modo = "MENU"
                else: self.juego.dibujar(self.screen)

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
