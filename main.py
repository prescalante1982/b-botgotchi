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
# LÓGICA DE JUEGOS (Naves y Carreras)
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
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 350, 40, 10))
        pygame.draw.rect(sc, (0,200,255), (self.x-20, 335, 8, 15))
        pygame.draw.rect(sc, (0,200,255), (self.x+12, 335, 8, 15))
        pygame.draw.rect(sc, (255,255,255), (self.x-2, 330, 4, 20))
        for e in self.enemigos:
            pygame.draw.ellipse(sc, (200,100,255), (e[0]-22, e[1]-10, 44, 22))
            pygame.draw.circle(sc, (200,255,255), (e[0], e[1]-5), 8)
        for b in self.balas: pygame.draw.rect(sc, (255,255,0), (b[0]-2, b[1], 4, 10))

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
        """Detecta cualquier tipo de entrada (Botón, Cruz/Hat o Eje de Palanca)"""
        if ev.type == pygame.JOYBUTTONDOWN:
            return {"tipo": "btn", "val": ev.button}
        if ev.type == pygame.JOYHATMOTION and ev.value != (0,0):
            return {"tipo": "hat", "val": list(ev.value)}
        if ev.type == pygame.JOYAXISMOTION:
            if ev.value > 0.8: return {"tipo": "axis", "axis": ev.axis, "val": 1}
            if ev.value < -0.8: return {"tipo": "axis", "axis": ev.axis, "val": -1}
        return None

    def obtener_accion(self, ev_actual):
        """Compara la entrada actual con el archivo de configuración"""
        if not self.controles: return None
        for accion, mapeo in self.controles.items():
            if ev_actual.type == pygame.JOYBUTTONDOWN and mapeo.get("tipo") == "btn":
                if ev_actual.button == mapeo["val"]: return accion
            if ev_actual.type == pygame.JOYHATMOTION and mapeo.get("tipo") == "hat":
                if list(ev_actual.value) == mapeo["val"]: return accion
            if ev_actual.type == pygame.JOYAXISMOTION and mapeo.get("tipo") == "axis":
                if ev_actual.axis == mapeo["axis"]:
                    if (ev_actual.value > 0.8 and mapeo["val"] == 1) or (ev_actual.value < -0.8 and mapeo["val"] == -1):
                        return accion
        return None

    def run(self):
        while self.running:
            self.screen.fill(CELESTE_CIELO)
            t = pygame.time.get_ticks()
            accion_detectada = None

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                
                if self.modo == "CONFIG":
                    mapeo = self.detectar_entrada(ev)
                    if mapeo:
                        self.controles[self.pasos_cfg[self.idx_cfg]] = mapeo
                        self.idx_cfg += 1
                        pygame.time.delay(500) # Pausa para que sueltes el botón
                        if self.idx_cfg >= len(self.pasos_cfg):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                else:
                    accion_detectada = self.obtener_accion(ev)

            if accion_detectada == "L": self.modo = "MENU"; self.juego = None

            if self.modo == "CONFIG":
                self.mostrar_t("CONFIGURACIÓN DE MANDO", y=100, color=(0,0,0), size=30)
                self.mostrar_t(f"PRESIONA: {self.pasos_cfg[self.idx_cfg]}", y=220, color=(200,0,0), size=40)

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                opts = ["JUGAR", "CUENTOS"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (200+i*220, 310, 180, 50), border_radius=15)
                    self.mostrar_t(opt, 200+i*220+90, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if accion_detectada == "DERECHA": self.seleccion = (self.seleccion+1)%len(opts)
                elif accion_detectada == "IZQUIERDA": self.seleccion = (self.seleccion-1)%len(opts)
                elif accion_detectada == "A": self.modo = opts[self.seleccion]

            elif self.modo == "JUGAR":
                if not self.juego:
                    self.mostrar_t("A: NAVES", y=200, color=(0,0,0), size=30)
                    if accion_detectada == "A": self.juego = JuegoNaves()
                else:
                    if self.juego.actualizar(accion_detectada): self.juego = None
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
