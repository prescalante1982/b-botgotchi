import pygame
import json
import os
import time
import math
import random

# --- CONFIGURACIÓN GLOBAL ---
COLOR_FONDO = (173, 216, 230)  # Celeste Sky
COLOR_TEXTO_DARK = (40, 40, 60)
CONFIG_FILE = "config_pablo.json"

# --- LÓGICA DE MAPA PARA PAC-MAN ---
def generar_mapa_arcade():
    # 1 = Pared azul, 0 = Camino con puntos
    return [
        [1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,1],
        [1,0,1,1,0,1,0,1],
        [1,0,0,0,0,1,0,1],
        [1,1,1,0,1,1,0,1],
        [1,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,0,1],
        [1,1,1,1,1,1,1,1]
    ]

# ==========================================
# CLASES DE JUEGOS MEJORADOS
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []
        self.vidas = 3; self.estado = "START"; self.timer_estado = 0
        self.estrellas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(25)]
    
    def actualizar(self, ent, ctrl):
        if self.estado == "START":
            self.timer_estado += 1
            if self.timer_estado > 60: self.estado = "JUGANDO"; self.timer_estado = 0
            return False
            
        for s in self.estrellas: s[1] = (s[1] + 5) % 400
        # Movimiento ultra rápido
        if ent == ctrl.get("IZQUIERDA"): self.x = max(30, self.x - 45)
        elif ent == ctrl.get("DERECHA"): self.x = min(770, self.x + 45)
        elif ent == ctrl.get("A"): self.balas.append([self.x, 340])
        
        if random.random() < 0.08: 
            self.enemigos.append([random.randint(50, 750), -20, random.choice([(200,0,255), (0,255,100)])])
        
        for b in self.balas[:]:
            b[1] -= 20
            if b[1] < 0: self.balas.remove(b)
            
        for e in self.enemigos[:]:
            e[1] += 6
            for b in self.balas[:]:
                if abs(e[0] - b[0]) < 30 and abs(e[1] - b[1]) < 30:
                    if e in self.enemigos: self.enemigos.remove(e)
                    if b in self.balas: self.balas.remove(b)
            
            # Colisión con la nave E
            if e[1] > 330 and abs(e[0] - self.x) < 40:
                self.vidas -= 1
                self.enemigos = []; self.balas = []
                self.estado = "START"; self.timer_estado = 0
            elif e[1] > 400: self.enemigos.remove(e)
            
        return self.vidas <= 0

    def dibujar(self, sc):
        sc.fill((10, 10, 30))
        for s in self.estrellas: pygame.draw.circle(sc, (255, 255, 255), s, 1)
        
        # --- DIBUJO NAVE "E" ACOSTADA ---
        c = (0, 200, 255)
        pygame.draw.rect(sc, c, (self.x-20, 350, 40, 10)) # Base larga
        pygame.draw.rect(sc, c, (self.x-20, 335, 8, 15))  # Ala Izquierda
        pygame.draw.rect(sc, c, (self.x+12, 335, 8, 15))  # Ala Derecha
        pygame.draw.rect(sc, (255, 255, 255), (self.x-2, 330, 4, 20)) # Cañón central
        
        for b in self.balas: pygame.draw.rect(sc, (255, 255, 0), (b[0]-2, b[1], 4, 10))
        for e in self.enemigos:
            pygame.draw.ellipse(sc, e[2], (e[0]-22, e[1]-10, 44, 22)) # UFO de color
            pygame.draw.circle(sc, (200, 255, 255), (e[0], e[1]-5), 8) # Cúpula blanca
            
        self.mostrar_hud(sc)

    def mostrar_hud(self, sc):
        font = pygame.font.SysFont("Arial", 30, True)
        if self.estado == "START":
            txt = font.render(f"VIDA {4 - self.vidas} - ¡LISTO!", True, (255, 255, 0))
            sc.blit(txt, (400 - txt.get_width()//2, 180))
        sc.blit(font.render(f"VIDAS: {self.vidas}", True, (255, 50, 50)), (20, 20))

class JuegoCarreras:
    def __init__(self):
        self.x = 400; self.obs = []; self.v = 14; self.vidas = 3; self.estado = "START"; self.timer = 0
    def actualizar(self, ent, ctrl):
        if self.estado == "START":
            self.timer += 1
            if self.timer > 60: self.estado = "JUGANDO"; self.timer = 0
            return False
        if ent == ctrl.get("IZQUIERDA"): self.x = max(200, self.x - 45)
        elif ent == ctrl.get("DERECHA"): self.x = min(600, self.x + 45)
        if random.random() < 0.08: 
            self.obs.append([random.randint(210, 590), -60, random.choice([(0,255,100), (255,150,0)])])
        for o in self.obs[:]:
            o[1] += self.v
            if 320 < o[1] < 380 and abs(self.x - o[0]) < 45:
                self.vidas -= 1; self.obs = []; self.estado = "START"; self.timer = 0
            elif o[1] > 400: self.obs.remove(o)
        return self.vidas <= 0
    def dibujar(self, sc):
        sc.fill((34, 139, 34)) # Pasto
        pygame.draw.rect(sc, (40, 40, 40), (180, 0, 440, 400)) # Pista amplia
        pygame.draw.rect(sc, (255, 255, 255), (395, 0, 10, 400)) # Línea central
        # Auto de Pablo
        pygame.draw.rect(sc, (255, 0, 0), (self.x-20, 330, 40, 60), border_radius=6)
        pygame.draw.rect(sc, (0,0,0), (self.x-26, 335, 10, 18)); pygame.draw.rect(sc, (0,0,0), (self.x+16, 335, 10, 18))
        # Autos enemigos más detallados
        for o in self.obs:
            pygame.draw.rect(sc, o[2], (o[0]-20, o[1], 40, 60), border_radius=6)
            pygame.draw.rect(sc, (0,0,0), (o[0]-26, o[1]+5, 10, 18)); pygame.draw.rect(sc, (0,0,0), (o[0]+16, o[1]+5, 10, 18))
        
        font = pygame.font.SysFont("Arial", 30, True)
        if self.estado == "START":
            txt = font.render(f"VIDA {4 - self.vidas} - ¡DALE!", True, (255, 255, 255))
            sc.blit(txt, (400 - txt.get_width()//2, 180))
        sc.blit(font.render(f"VIDAS: {self.vidas}", True, (255, 255, 255)), (20, 20))

class JuegoPacman:
    def __init__(self):
        self.mapa = generar_mapa_arcade()
        self.px, self.py = 1, 1; self.pts = []; self.vidas = 3; self.estado = "START"; self.timer = 0
        for r in range(8):
            for c in range(8):
                if self.mapa[r][c] == 0: self.pts.append([r, c])
        self.fx, self.fy = 6, 6; self.paso_f = 0
    def actualizar(self, ent, ctrl):
        if self.estado == "START":
            self.timer += 1
            if self.timer > 60: self.estado = "JUGANDO"; self.timer = 0
            return False
        nx, ny = self.px, self.py
        if ent == ctrl.get("IZQUIERDA"): ny -= 1
        elif ent == ctrl.get("DERECHA"): ny += 1
        elif ent == ctrl.get("ARRIBA"): nx -= 1
        elif ent == ctrl.get("ABAJO"): nx += 1
        if 0 <= nx < 8 and 0 <= ny < 8 and self.mapa[nx][ny] == 0:
            self.px, self.py = nx, ny
        if [self.px, self.py] in self.pts: self.pts.remove([self.px, self.py])
        
        # Inteligencia del Fantasma (lento y respeta paredes)
        self.paso_f += 1
        if self.paso_f > 20: 
            self.paso_f = 0
            dx = 1 if self.fx < self.px else -1 if self.fx > self.px else 0
            dy = 1 if self.fy < self.py else -1 if self.fy > self.py else 0
            if dx != 0 and self.mapa[self.fx + dx][self.fy] == 0: self.fx += dx
            elif dy != 0 and self.mapa[self.fx][self.fy + dy] == 0: self.fy += dy
            
        if self.fx == self.px and self.fy == self.py:
            self.vidas -= 1; self.fx, self.fy = 6, 6; self.px, self.py = 1, 1; self.estado = "START"; self.timer = 0
        return self.vidas <= 0 or len(self.pts) == 0

    def dibujar(self, sc):
        sc.fill((0,0,15))
        for r in range(8):
            for c in range(8):
                if self.mapa[r][c] == 1: pygame.draw.rect(sc, (0,50,200), (240+c*40, 40+r*40, 38, 38), border_radius=4)
        for p in self.pts: pygame.draw.circle(sc, (255, 255, 0), (240+p[1]*40+20, 40+p[0]*40+20), 4)
        pygame.draw.circle(sc, (255, 255, 0), (240+self.py*40+20, 40+self.px*40+20), 16) # Pablo
        pygame.draw.circle(sc, (255, 0, 0), (240+self.fy*40+20, 40+self.fx*40+20), 16) # Fantasma
        
        font = pygame.font.SysFont("Arial", 30, True)
        if self.estado == "START":
            txt = font.render(f"VIDA {4 - self.vidas}", True, (255, 255, 255))
            sc.blit(txt, (400 - txt.get_width()//2, 180))

# ==========================================
# CONSOLA PRINCIPAL (TODO EN UNO)
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joy: self.joy.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock(); self.running = True
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.indice_cfg = 0
        self.modo = "MENU" if os.path.exists(CONFIG_FILE) else "CONFIG"
        if self.modo == "MENU":
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0; self.sel_juego = 0; self.sub_modo = "MENU_JUEGOS"
        self.juego_actual = None

    def run(self):
        while self.running:
            self.screen.fill(COLOR_FONDO)
            t = pygame.time.get_ticks()
            entrada = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
                entrada = self.obtener_entrada(event)

            # Lógica de escape global (Botón L del 8BitDo)
            if entrada == self.controles.get("L"):
                self.modo = "MENU"; self.sub_modo = "MENU_JUEGOS"; self.juego_actual = None

            if self.modo == "CONFIG":
                self.mostrar_texto("CONFIGURACIÓN DE MANDO", y=80, color=COLOR_TEXTO_DARK, size=30)
                self.mostrar_texto(f"PULSA: {self.pasos_config[self.indice_cfg]}", y=240, color=(255, 50, 50), size=45)
                if entrada:
                    self.controles[self.pasos_config[self.indice_cfg]] = entrada
                    self.indice_cfg += 1
                    time.sleep(0.3) # Pequeña pausa para no saltar botones
                    if self.indice_cfg >= len(self.pasos_config):
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                        self.modo = "MENU"

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    c = (255, 255, 255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    self.mostrar_texto(opt, 40+i*190+85, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if entrada == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                elif entrada == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                elif entrada == self.controles.get("A"): self.modo = self.opciones[self.seleccion]

            elif self.modo == "JUGAR":
                if self.sub_modo == "MENU_JUEGOS":
                    self.mostrar_texto("ARCADE CENTER", y=40, color=COLOR_TEXTO_DARK, size=35)
                    juegos = ["NAVES", "CARRERAS", "PAC-MAN"]
                    for i, jg in enumerate(juegos):
                        col = (255, 100, 0) if self.sel_juego == i else (100, 100, 120)
                        self.mostrar_texto(jg, y=120+i*55, color=col, size=28)
                    if entrada == self.controles.get("ABAJO"): self.sel_juego = (self.sel_juego+1)%3
                    elif entrada == self.controles.get("ARRIBA"): self.sel_juego = (self.sel_juego-1)%3
                    elif entrada == self.controles.get("A"):
                        if self.sel_juego == 0: self.juego_actual = JuegoNaves()
                        elif self.sel_juego == 1: self.juego_actual = JuegoCarreras()
                        elif self.sel_juego == 2: self.juego_actual = JuegoPacman()
                        self.sub_modo = "JUGANDO"
                else:
                    if self.juego_actual.actualizar(entrada, self.controles):
                        self.screen.fill((0,0,0))
                        self.mostrar_texto("GAME OVER", size=60, color=(255,0,0))
                        pygame.display.flip()
                        time.sleep(2)
                        self.sub_modo = "MENU_JUEGOS"
                    else:
                        self.juego_actual.dibujar(self.screen)

            elif self.modo == "CHISTES":
                self.dibujar_bot(t)
                self.mostrar_texto("¡Toca A para otro chiste!", y=250, color=COLOR_TEXTO_DARK, size=20)

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
        pygame.draw.circle(self.screen, (0,0,0), (380, 135+f), 8)
        pygame.draw.circle(self.screen, (0,0,0), (420, 135+f), 8)
        pygame.draw.rect(self.screen, (0,0,0), (385, 155+f, 30, 4), border_radius=2)

if __name__ == "__main__":
    BBotConsola().run()
