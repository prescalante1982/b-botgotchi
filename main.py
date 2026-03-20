import pygame
import json
import os
import time
import math
import random

# --- CONFIGURACIÓN VISUAL ---
ANCHO, ALTO = 800, 400
CELESTE_CIELO = (173, 216, 230)
NEGRO_ESPACIO = (10, 10, 30)
CONFIG_FILE = "config_pablo.json"
FUENTE_RETRO = "Courier New"

# --- RECURSOS ---
ESTRELLAS = [[random.randint(0, ANCHO), random.randint(0, ALTO), random.random()] for _ in range(60)]

# ==========================================
# JUEGOS (Naves con Estrellas y Carros Gris)
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []; self.puntos = 0; self.vidas = 3
    def actualizar(self, ent, ctrl):
        if ent == "IZQUIERDA": self.x = max(30, self.x - 45)
        elif ent == "DERECHA": self.x = min(770, self.x + 45)
        elif ent == "X": self.balas.append([self.x, 340])
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
        for s in ESTRELLAS: 
            s[0] = (s[0] - s[2]*2) % ANCHO
            pygame.draw.circle(sc, (255,255,255), (int(s[0]), s[1]), 1)
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
    def actualizar(self, ent, ctrl):
        if self.flash > 0: self.flash -= 1
        if ent == "IZQUIERDA": self.x = max(200, self.x - 35)
        elif ent == "DERECHA": self.x = min(600, self.x + 35)
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
        pygame.draw.rect(sc, (200, 0, 0), (self.x-20, 330, 40, 60), border_radius=6)
        pygame.draw.rect(sc, (150, 200, 255), (self.x-12, 345, 24, 12))
        for o in self.obs: pygame.draw.rect(sc, (255,140,0), (o[0]-20, o[1], 40, 60), border_radius=6)

# ==========================================
# CONSOLA PRINCIPAL
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()
        
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN | pygame.SCALED)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        
        if not os.path.exists(CONFIG_FILE): self.modo = "CONFIG"
        else:
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L"]
        self.idx_cfg = 0; self.seleccion = 0; self.juego = None

    def obtener_entrada_mapeada(self, ev_actual):
        """Convierte evento de Pygame en una acción (ej: 'IZQUIERDA')"""
        if not self.controles: return None
        for accion, mapeo in self.controles.items():
            if ev_actual.type == pygame.JOYBUTTONDOWN and mapeo.get("tipo") == "btn":
                if ev_actual.button == mapeo.get("val"): return accion
            if ev_actual.type == pygame.JOYHATMOTION and mapeo.get("tipo") == "hat":
                if list(ev_actual.value) == mapeo.get("val"): return accion
        return None

    def run(self):
        while self.running:
            self.screen.fill(CELESTE_CIELO)
            t = pygame.time.get_ticks()
            accion = None

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                
                # Captura cruda para CONFIG
                if self.modo == "CONFIG":
                    mapeo_nuevo = None
                    if ev.type == pygame.JOYBUTTONDOWN:
                        mapeo_nuevo = {"tipo": "btn", "val": ev.button}
                    elif ev.type == pygame.JOYHATMOTION and ev.value != (0,0):
                        mapeo_nuevo = {"tipo": "hat", "val": list(ev.value)}
                    
                    if mapeo_nuevo:
                        self.controles[self.pasos_cfg[self.idx_cfg]] = mapeo_nuevo
                        self.idx_cfg += 1
                        pygame.time.delay(400) # Evita saltos locos
                        if self.idx_cfg >= len(self.pasos_cfg):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                
                # Captura mapeada para MENU y JUEGOS
                else:
                    accion = self.obtener_entrada_mapeada(ev)

            # Lógica de navegación
            if accion == "L": self.modo = "MENU"; self.juego = None

            if self.modo == "CONFIG":
                self.mostrar_t("PULSA EL BOTON PARA:", y=150, color=(0,0,0), size=30)
                self.mostrar_t(self.pasos_cfg[self.idx_cfg], y=220, color=(200,0,0), size=45)

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                opts = ["JUGAR", "CHISTES", "CUENTOS"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (100+i*220, 310, 180, 50), border_radius=15)
                    self.mostrar_t(opt, 100+i*220+90, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                
                if accion == "DERECHA": self.seleccion = (self.seleccion+1)%len(opts)
                elif accion == "IZQUIERDA": self.seleccion = (self.seleccion-1)%len(opts)
                elif accion == "A": self.modo = opts[self.seleccion]

            elif self.modo == "JUGAR":
                if not self.juego:
                    self.mostrar_t("A: NAVES | B: CARROS", y=200, color=(0,0,0), size=30)
                    if accion == "A": self.juego = JuegoNaves()
                    elif accion == "B": self.juego = JuegoCarreras()
                else:
                    if self.juego.actualizar(accion, self.controles): self.juego = None
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
