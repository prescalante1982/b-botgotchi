import pygame
import json
import os
import time
import math
import random

# --- CONFIGURACIÓN GLOBAL ---
COLOR_FONDO = (173, 216, 230) 
COLOR_TEXTO_DARK = (40, 40, 60)
CONFIG_FILE = "config_pablo.json"
FUENTE_RETRO = "Courier New" # Fuente con estilo pixel/monospaced

def generar_mapa_ancho():
    return [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
        [1,0,1,1,1,0,1,1,1,0,1,1,1,0,1],
        [1,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
        [1,1,1,0,1,1,0,1,0,1,1,0,1,1,1],
        [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
        [1,0,1,1,1,1,0,0,0,1,1,1,1,0,1],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    ]

# ==========================================
# CLASES DE JUEGOS
# ==========================================

class JuegoNaves:
    def __init__(self):
        self.x = 400; self.balas = []; self.enemigos = []
        self.vidas = 3; self.puntos = 0; self.estado = "START"; self.timer_estado = 0
        self.estrellas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(25)]
    
    def actualizar(self, ent, ctrl):
        if self.estado == "START":
            self.timer_estado += 1
            if self.timer_estado > 60: self.estado = "JUGANDO"; self.timer_estado = 0
            return False
        for s in self.estrellas: s[1] = (s[1] + 5) % 400
        if ent == ctrl.get("IZQUIERDA"): self.x = max(30, self.x - 45)
        elif ent == ctrl.get("DERECHA"): self.x = min(770, self.x + 45)
        elif ent == ctrl.get("X"): self.balas.append([self.x, 340]) # Usamos X para disparar para dejar A/B libres
        
        if random.random() < 0.08: 
            self.enemigos.append([random.randint(50, 750), -40, random.choice([(200,0,255), (0,255,100)])])
        for b in self.balas[:]:
            b[1] -= 20
            if b[1] < 0: self.balas.remove(b)
        for e in self.enemigos[:]:
            e[1] += 6
            for b in self.balas[:]:
                if abs(e[0] - b[0]) < 30 and abs(e[1] - b[1]) < 30:
                    if e in self.enemigos: self.enemigos.remove(e)
                    if b in self.balas: self.balas.remove(b)
                    self.puntos += 10
            if e[1] > 330 and abs(e[0] - self.x) < 40:
                self.vidas -= 1; self.enemigos = []; self.estado = "START"; self.timer_estado = 0
            elif e[1] > 400: self.enemigos.remove(e)
        return self.vidas <= 0

    def dibujar(self, sc):
        sc.fill((10, 10, 30))
        for s in self.estrellas: pygame.draw.circle(sc, (255, 255, 255), s, 1)
        c = (0, 200, 255)
        pygame.draw.rect(sc, c, (self.x-20, 350, 40, 10)) 
        pygame.draw.rect(sc, c, (self.x-20, 335, 8, 15))  
        pygame.draw.rect(sc, c, (self.x+12, 335, 8, 15))  
        pygame.draw.rect(sc, (255, 255, 255), (self.x-2, 330, 4, 20)) 
        for b in self.balas: pygame.draw.rect(sc, (255, 255, 0), (b[0]-2, b[1], 4, 10))
        for e in self.enemigos:
            pygame.draw.ellipse(sc, e[2], (e[0]-22, e[1]-10, 44, 22)) 
            pygame.draw.circle(sc, (200, 255, 255), (e[0], e[1]-5), 8) 
        self.mostrar_hud(sc)

    def mostrar_hud(self, sc):
        font = pygame.font.SysFont(FUENTE_RETRO, 22, True)
        if self.estado == "START":
            txt = font.render(f"VIDA {4 - self.vidas}", True, (255, 255, 0))
            sc.blit(txt, (400 - txt.get_width()//2, 180))
        sc.blit(font.render(f"HP: {self.vidas}", True, (255, 50, 50)), (20, 20))
        pts_txt = font.render(f"SCORE:{self.puntos}", True, (255, 255, 255))
        sc.blit(pts_txt, (780 - pts_txt.get_width(), 20))

class JuegoCarreras:
    def __init__(self):
        self.x = 400; self.obs = []; self.v = 5; self.vidas = 3; self.estado = "START"
        self.distancia = 0; self.meta = 500; self.nivel = 1; self.timer = 0
    
    def actualizar(self, ent, ctrl):
        if self.estado == "START":
            self.timer += 1
            if self.timer > 60: self.estado = "JUGANDO"; self.timer = 0
            return False
        
        # Sistema de Aceleración y Freno
        # Usamos pygame.joystick directamente para detectar si el botón está presionado continuamente
        joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if joy:
            btn_a = ctrl.get("A", {}).get("val")
            btn_b = ctrl.get("B", {}).get("val")
            if btn_a is not None and joy.get_button(btn_a): self.v = min(25, self.v + 0.5)
            elif btn_b is not None and joy.get_button(btn_b): self.v = max(0, self.v - 0.8)
            else: self.v = max(5, self.v - 0.1) # Deceleración natural

        self.distancia += int(self.v / 5)
        if self.distancia >= self.meta:
            self.nivel += 1; self.meta += 500; self.estado = "START"; self.obs = []; return False

        if ent == ctrl.get("IZQUIERDA"): self.x = max(200, self.x - 30)
        elif ent == ctrl.get("DERECHA"): self.x = min(600, self.x + 30)
        
        if random.random() < 0.07: 
            nx = random.randint(210, 590)
            if not any(abs(nx - o[0]) < 60 and o[1] < 100 for o in self.obs):
                self.obs.append([nx, -80, random.choice([(0,255,100), (255,150,0), (200,100,255)])])
        
        for o in self.obs[:]:
            o[1] += int(self.v + 2)
            if 320 < o[1] < 380 and abs(self.x - o[0]) < 45:
                self.vidas -= 1; self.v = 5; self.obs = []; self.estado = "START"; self.timer = 0
            elif o[1] > 400: self.obs.remove(o)
        return self.vidas <= 0

    def dibujar(self, sc):
        sc.fill((34, 139, 34)) 
        pygame.draw.rect(sc, (60, 60, 60), (180, 0, 440, 400)) 
        pygame.draw.rect(sc, (255, 255, 255), (395, 0, 10, 400)) 
        # Carro Pablo
        for lx, ly in [(-26, 335), (18, 335), (-26, 370), (18, 370)]:
            pygame.draw.rect(sc, (0,0,0), (self.x + lx, ly, 8, 12))
        pygame.draw.rect(sc, (200, 0, 0), (self.x-20, 330, 40, 60), border_radius=6)
        pygame.draw.rect(sc, (150, 200, 255), (self.x-12, 345, 24, 12)) 
        
        for o in self.obs:
            pygame.draw.rect(sc, o[2], (o[0]-20, o[1], 40, 60), border_radius=6)
            
        font = pygame.font.SysFont(FUENTE_RETRO, 20, True)
        sc.blit(font.render(f"LVL:{self.nivel}", True, (255, 255, 255)), (20, 20))
        meta_txt = font.render(f"DIST:{self.distancia}/{self.meta}m", True, (255, 255, 0))
        sc.blit(meta_txt, (780 - meta_txt.get_width(), 20))
        sc.blit(font.render(f"VEL:{int(self.v*10)}km/h", True, (255, 255, 255)), (20, 360))

class JuegoPacman:
    def __init__(self):
        self.mapa = generar_mapa_ancho()
        self.px, self.py = 1, 1; self.pts = []; self.vidas = 3; self.puntos = 0
        self.estado = "START"; self.timer = 0; self.nivel = 1; self.frame = 0
        self.cargar_puntos()
        self.fx, self.fy = 6, 13; self.paso_f = 0
    def cargar_puntos(self):
        self.pts = []
        for r in range(8):
            for c in range(15):
                if self.mapa[r][c] == 0: self.pts.append([r, c])
    def actualizar(self, ent, ctrl):
        if self.estado == "START":
            self.timer += 1
            if self.timer > 60: self.estado = "JUGANDO"; self.timer = 0
            return False
        self.frame += 1
        nx, ny = self.px, self.py
        if ent == ctrl.get("IZQUIERDA"): ny -= 1
        elif ent == ctrl.get("DERECHA"): ny += 1
        elif ent == ctrl.get("ARRIBA"): nx -= 1
        elif ent == ctrl.get("ABAJO"): nx += 1
        if 0 <= nx < 8 and 0 <= ny < 15 and self.mapa[nx][ny] == 0:
            self.px, self.py = nx, ny
        if [self.px, self.py] in self.pts: 
            self.pts.remove([self.px, self.py]); self.puntos += 10
        if not self.pts:
            self.nivel += 1; self.cargar_puntos(); self.estado = "START"; self.timer = 0
        
        self.paso_f += 1
        if self.paso_f > 12: 
            self.paso_f = 0
            dx = 1 if self.fx < self.px else -1 if self.fx > self.px else 0
            dy = 1 if self.fy < self.py else -1 if self.fy > self.py else 0
            if dx != 0 and self.mapa[self.fx + dx][self.fy] == 0: self.fx += dx
            elif dy != 0 and self.mapa[self.fx][self.fy + dy] == 0: self.fy += dy
        if self.fx == self.px and self.fy == self.py:
            self.vidas -= 1; self.fx, self.fy = 6, 13; self.px, self.py = 1, 1; self.estado = "START"; self.timer = 0
        return self.vidas <= 0

    def dibujar(self, sc):
        sc.fill((0,0,20))
        # Laberinto con paredes sólidas
        for r in range(8):
            for c in range(15):
                x, y = 25 + c*50, 10 + r*50
                if self.mapa[r][c] == 1: 
                    pygame.draw.rect(sc, (0,50,180), (x, y, 50, 50))
                    pygame.draw.rect(sc, (0,80,255), (x+2, y+2, 46, 46), 1)
                elif [r,c] in self.pts: pygame.draw.circle(sc, (255, 255, 200), (x+25, y+25), 4)
        
        # Pacman animado con boca y ojo
        px, py = 25 + self.py*50 + 25, 10 + self.px*50 + 25
        pygame.draw.circle(sc, (255, 255, 0), (px, py), 20)
        # Boca (animación simple)
        if (self.frame // 10) % 2 == 0:
            pygame.draw.polygon(sc, (0,0,20), [(px, py), (px+22, py-12), (px+22, py+12)])
        pygame.draw.circle(sc, (0,0,0), (px+5, py-10), 3) # Ojo
        
        # Fantasma
        fx, fy = 25 + self.fy*50 + 12, 10 + self.fx*50 + 12
        pygame.draw.rect(sc, (255, 50, 50), (fx, fy+12, 26, 14)) 
        pygame.draw.circle(sc, (255, 50, 50), (fx+13, fy+13), 13) 
        pygame.draw.circle(sc, (255, 255, 255), (fx+7, fy+10), 4); pygame.draw.circle(sc, (255, 255, 255), (fx+19, fy+10), 4)
        
        font = pygame.font.SysFont(FUENTE_RETRO, 20, True)
        sc.blit(font.render(f"HP:{self.vidas}", True, (255, 255, 255)), (20, 20))
        pts_txt = font.render(f"SCORE:{self.puntos}", True, (255, 255, 0))
        sc.blit(pts_txt, (780 - pts_txt.get_width(), 20))

# ==========================================
# CONSOLA PRINCIPAL
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self.joy: self.joy.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock(); self.running = True
        self.controles = {}
        self.modo = "MENU" if os.path.exists(CONFIG_FILE) else "CONFIG"
        if self.modo == "MENU":
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.indice_cfg = 0
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0; self.sel_juego = 0; self.sub_modo = "MENU_JUEGOS"; self.juego_actual = None

    def run(self):
        while self.running:
            self.screen.fill(COLOR_FONDO)
            t = pygame.time.get_ticks()
            entrada = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
                entrada = self.obtener_entrada(event)

            if entrada == self.controles.get("L"):
                self.modo = "MENU"; self.sub_modo = "MENU_JUEGOS"; self.juego_actual = None

            if self.modo == "CONFIG":
                self.mostrar_texto(f"PULSA: {self.pasos_config[self.indice_cfg]}", y=200, color=(255, 50, 50), size=45)
                if entrada:
                    self.controles[self.pasos_config[self.indice_cfg]] = entrada
                    self.indice_cfg += 1
                    time.sleep(0.3); 
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
                    jgs = ["NAVES", "CARRERAS", "PAC-MAN"]
                    for i, jg in enumerate(jgs):
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
                        self.screen.fill((0,0,0)); self.mostrar_texto("GAME OVER", size=60, color=(255,0,0))
                        pygame.display.flip(); time.sleep(2); self.sub_modo = "MENU_JUEGOS"
                    else: self.juego_actual.dibujar(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    def obtener_entrada(self, event):
        if event.type == pygame.JOYBUTTONDOWN: return {"tipo": "btn", "val": event.button}
        if event.type == pygame.JOYHATMOTION and event.value != (0,0): return {"tipo": "hat", "val": list(event.value)}
        if event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.6: 
            return {"tipo": "axis", "val": [event.axis, 1 if event.value > 0 else -1]}
        return None

    def mostrar_texto(self, txt, x=400, y=200, color=(255,255,255), size=22):
        font = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = font.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

    def dibujar_bot(self, t):
        f = math.sin(t * 0.005) * 12
        pygame.draw.rect(self.screen, (255,255,255), (350, 100+f, 100, 110), border_radius=25)
        pygame.draw.circle(self.screen, (0,0,0), (380, 135+f), 8); pygame.draw.circle(self.screen, (0,0,0), (420, 135+f), 8)
        pygame.draw.rect(self.screen, (0,0,0), (385, 155+f, 30, 4), border_radius=2)

if __name__ == "__main__":
    BBotConsola().run()
