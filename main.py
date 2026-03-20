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

def envolver_texto(texto, fuente, ancho_max):
    palabras = texto.split(' ')
    lineas = []; linea_act = ""
    for p in palabras:
        if fuente.size(linea_act + p)[0] < ancho_max: linea_act += p + " "
        else: lineas.append(linea_act); linea_act = p + " "
    lineas.append(linea_act)
    return lineas

# ==========================================
# JUEGOS MEJORADOS
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
        sc.fill((10, 10, 30))
        for s in self.estrellas: 
            s[0] = (s[0] - s[2]*2) % 800
            pygame.draw.circle(sc, (255,255,255), (int(s[0]), s[1]), 1)
        # NAVE E
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 350, 40, 10))
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 335, 8, 15))
        pygame.draw.rect(sc, (0,200,255), (self.x+12, 335, 8, 15))
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
        pygame.draw.rect(sc, (110, 110, 110), (180, 0, 440, 400))
        pygame.draw.rect(sc, (255, 255, 255), (395, 0, 10, 400))
        if self.flash > 0: sc.fill((200, 0, 0), special_flags=pygame.BLEND_ADD)
        # CARRO ROJO CON VIDRIO
        pygame.draw.rect(sc, (200, 0, 0), (self.x-20, 330, 40, 60), border_radius=6)
        pygame.draw.rect(sc, (150, 200, 255), (self.x-12, 345, 24, 12))
        for o in self.obs: pygame.draw.rect(sc, (255,140,0), (o[0]-20, o[1], 40, 60), border_radius=6)

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
        self.idx_cfg = 0; self.seleccion = 0; self.sel_juego = 0; self.item_idx = 0; self.linea_idx = 0
        self.cuentos = [
            ["La Nave E", "Pablo Alí viajaba en su nave azul por el espacio. Vio un UFO morado y disparó su rayo amarillo."],
            ["B-Bot Aventuras", "B-Bot es un robot blanco que vive en una Raspberry Pi. Le gusta comer electricidad y contar chistes."]
        ]

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
                    m = None
                    if ev.type == pygame.JOYBUTTONDOWN: m = {"tipo": "btn", "val": ev.button}
                    elif ev.type == pygame.JOYHATMOTION and ev.value != (0,0): m = {"tipo": "hat", "val": list(ev.value)}
                    if m:
                        self.controles[self.pasos_cfg[self.idx_cfg]] = m
                        self.idx_cfg += 1; pygame.time.delay(400)
                        if self.idx_cfg >= len(self.pasos_cfg):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                else: accion = self.obtener_accion(ev)

            if accion == "L": self.modo = "MENU"; self.juego = None

            if self.modo == "MENU":
                self.dibujar_bot(t)
                opts = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (40+i*185, 310, 165, 50), border_radius=15)
                    self.mostrar_t(opt, 40+i*185+82, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if accion == "DERECHA": self.seleccion = (self.seleccion+1)%4
                elif accion == "IZQUIERDA": self.seleccion = (self.seleccion-1)%4
                elif accion == "A": self.modo = opts[self.seleccion]; self.linea_idx = 0

            elif self.modo == "CUENTOS":
                self.dibujar_bot(t, x=680)
                rect = pygame.Rect(50, 50, 500, 300)
                pygame.draw.rect(self.screen, (255,255,240), rect, border_radius=15) # PAPEL
                pygame.draw.rect(self.screen, (100,80,60), rect, 4, border_radius=15) # MARCO
                c = self.cuentos[self.item_idx]
                self.mostrar_t(c[0], 300, 80, (150,0,0), 28)
                fuente = pygame.font.SysFont(FUENTE_RETRO, 20)
                lineas = envolver_texto(c[1], fuente, 440)
                for i, l in enumerate(lineas): self.screen.blit(fuente.render(l, True, (0,0,0)), (80, 130+i*30))
                if accion == "A": self.item_idx = (self.item_idx + 1) % len(self.cuentos)

            elif self.modo == "JUGAR":
                self.mostrar_t("A: NAVES | B: CARROS", y=200, color=(0,0,0), size=30)
                if accion == "A": self.juego = JuegoNaves(); self.modo = "JUGANDO"
                elif accion == "B": self.juego = JuegoCarreras(); self.modo = "JUGANDO"

            elif self.modo == "JUGANDO":
                if self.juego.actualizar(accion): self.modo = "JUGAR"
                else: self.juego.dibujar(self.screen)

            elif self.modo == "MASCOTA":
                self.dibujar_bot(t, size_mult=1.5)
                self.mostrar_t("¡HOLA PABLO ALÍ!", y=300, color=(0,0,0), size=35)

            pygame.display.flip(); self.clock.tick(60)

    def mostrar_t(self, txt, x=400, y=200, color=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

    def dibujar_bot(self, t, x=400, size_mult=1.0):
        f = math.sin(t * 0.005) * (12 * size_mult)
        w, h = 100 * size_mult, 110 * size_mult
        pygame.draw.rect(self.screen, (255,255,255), (x-w/2, 100+f, w, h), border_radius=int(25*size_mult))
        pygame.draw.circle(self.screen, (0,0,0), (x-20*size_mult, 135*size_mult+f), 8*size_mult)
        pygame.draw.circle(self.screen, (0,0,0), (x+20*size_mult, 135*size_mult+f), 8*size_mult)
        pygame.draw.rect(self.screen, (0,0,0), (x-15*size_mult, 155*size_mult+f, 30*size_mult, 4*size_mult))

if __name__ == "__main__":
    BBotConsola().run()
