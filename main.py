import pygame
import json
import os
import time
import math
import random
import requests

# --- CONFIGURACIÓN ESTÉTICA ---
ANCHO, ALTO = 800, 400
CELESTE_CIELO = (173, 216, 230)
NEGRO_ESPACIO = (10, 10, 30)
CONFIG_FILE = "config_pablo.json"
SPRITE_SHEET = "bbot_sprite_sheet.PNG" 
JSON_CONFIG = "bbot_mascota.json"
FUENTE_RETRO = "Courier New"

# ==========================================
# GESTOR DE SPRITES B-BOT
# ==========================================

class BBotSpriteManager:
    def __init__(self, atlas_path, json_path):
        if not os.path.exists(atlas_path):
            self.atlas = pygame.Surface((1024, 1024), pygame.SRCALPHA)
        else:
            self.atlas = pygame.image.load(atlas_path).convert_alpha()
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        self.sprites = {}
        for name, pos in self.data["expressions"].items():
            rect = pygame.Rect(pos["x"], pos["y"], pos["w"], pos["h"])
            self.sprites[name] = self.atlas.subsurface(rect)

    def get_sprite(self, name, size=None):
        sprite = self.sprites.get(name, self.sprites.get("neutral"))
        if size: return pygame.transform.scale(sprite, (size, size))
        return sprite

# ==========================================
# LÓGICA DE LA MASCOTA AVANZADA
# ==========================================

class BBotPet:
    def __init__(self, name="B-Bot"):
        self.name = name
        self.hunger = 0
        self.boredom = 0
        self.energy = 100
        self.bathroom = 0
        self.last_tick = pygame.time.get_ticks()

    def clock_tick(self):
        ahora = pygame.time.get_ticks()
        if ahora - self.last_tick > 10000: # Cada 10 segundos actualiza
            self.hunger = min(100, self.hunger + 2)
            self.boredom = min(100, self.boredom + 3)
            self.energy = max(0, self.energy - 1)
            self.bathroom = min(100, self.bathroom + 2)
            self.last_tick = ahora

    def mood_expression(self):
        if self.energy < 20: return "durmiendo"
        if self.hunger > 70: return "triste"
        if self.bathroom > 80: return "enfermo" # Ganas de ir al baño
        if self.boredom > 70: return "pensativo"
        if self.hunger < 20 and self.boredom < 20: return "alegre"
        return "neutral"

# ==========================================
# LÓGICA DE JUEGOS (Naves, Carreras, Pacman)
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

# [Clases JuegoCarreras y JuegoPacman se mantienen iguales]
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
        pygame.display.set_caption("B-Bot Consola Pro")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        
        self.sprite_manager = BBotSpriteManager(SPRITE_SHEET, JSON_CONFIG)
        self.mascota = BBotPet("B-Bot")
        self.historial_chistes = []
        self.chiste_actual = {"setup": "Presiona A para un chiste", "punch": ""}
        
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.idx_cfg = 0

        if not os.path.exists(CONFIG_FILE): self.modo = "CONFIG"
        else:
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.seleccion = 0; self.sel_juego = 0; self.juego = None
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.tales_dir = os.path.join(self.base_path, "tales")
        if not os.path.exists(self.tales_dir): os.makedirs(self.tales_dir)
        
        self.lista_cuentos = []; self.idx_cuento = 0
        self.paginas_cuento = []; self.pagina_actual = 0
        self.rect_cuento = pygame.Rect(320, 55, 440, 285)

    def obtener_nuevo_chiste(self):
        try:
            r = requests.get("https://official-joke-api.appspot.com/jokes/random", timeout=3)
            data = r.json()
            if data["setup"] not in self.historial_chistes:
                self.chiste_actual = {"setup": data["setup"], "punch": data["punchline"]}
                self.historial_chistes.append(data["setup"])
                if len(self.historial_chistes) > 10: self.historial_chistes.pop(0)
        except:
            self.chiste_actual = {"setup": "Sin conexión...", "punch": "Revisa el internet de la Pi."}

    def obtener_accion(self, ev):
        if not self.controles: return None
        for accion, m in self.controles.items():
            if ev.type == pygame.JOYBUTTONDOWN and m.get("tipo") == "btn" and ev.button == m["val"]: return accion
            if ev.type == pygame.JOYHATMOTION and m.get("tipo") == "hat" and list(ev.value) == m["val"]: return accion
            if ev.type == pygame.JOYAXISMOTION and m.get("tipo") == "axis" and ev.axis == m["axis"]:
                if (ev.value > 0.7 and m["val"] == 1) or (ev.value < -0.7 and m["val"] == -1): return accion
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_LEFT: return "IZQUIERDA"
            if ev.key == pygame.K_RIGHT: return "DERECHA"
            if ev.key == pygame.K_UP: return "ARRIBA"
            if ev.key == pygame.K_DOWN: return "ABAJO"
            if ev.key in [pygame.K_SPACE, pygame.K_RETURN]: return "A"
            if ev.key == pygame.K_b: return "B"
            if ev.key == pygame.K_x: return "X"
            if ev.key == pygame.K_y: return "Y"
            if ev.key == pygame.K_ESCAPE: return "SELECT"
        return None

    def cargar_lista_tales(self):
        if os.path.exists(self.tales_dir):
            archivos = [f for f in os.listdir(self.tales_dir) if f.endswith('.txt')]
            self.lista_cuentos = sorted(archivos) if archivos else ["No hay cuentos.txt"]

    def preparar_paginas(self, texto):
        f = pygame.font.SysFont(FUENTE_RETRO, 20)
        lineas = []; parrafos = texto.split('\n')
        for p in parrafos:
            palabras = p.split(' '); l_act = ""
            for pal in palabras:
                if f.size(l_act + pal)[0] < 390: l_act += pal + " "
                else: lineas.append(l_act.strip()); l_act = pal + " "
            lineas.append(l_act.strip())
        return [lineas[i:i + 9] for i in range(0, len(lineas), 9)]

    def run(self):
        while self.running:
            self.screen.fill(CELESTE_CIELO); t = pygame.time.get_ticks()
            self.mascota.clock_tick(); accion = None
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                accion = self.obtener_accion(ev)

            if accion == "SELECT": self.modo = "MENU"; self.juego = None

            if self.modo == "MENU":
                sprite = self.sprite_manager.get_sprite(self.mascota.mood_expression(), size=160)
                flot = math.sin(t * 0.005) * 12
                self.screen.blit(sprite, (320, 100 + flot))
                opts = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (40+i*185, 310, 165, 50), border_radius=15)
                    self.mostrar_t(opt, 40+i*185+82, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if accion == "DERECHA": self.seleccion = (self.seleccion+1)%4
                elif accion == "IZQUIERDA": self.seleccion = (self.seleccion-1)%4
                elif accion == "A": 
                    self.modo = "SUB_" + opts[self.seleccion]
                    if self.modo == "SUB_CHISTES": self.obtener_nuevo_chiste()

            elif self.modo == "SUB_MASCOTA":
                sprite = self.sprite_manager.get_sprite(self.mascota.mood_expression(), size=200)
                self.screen.blit(sprite, (300, 40))
                # Barras de estado
                pygame.draw.rect(self.screen, (0,0,0), (50, 260, 150, 15), 2) # Hunger
                pygame.draw.rect(self.screen, (200,0,0), (52, 262, self.mascota.hunger * 1.46, 11))
                self.mostrar_t("HAMBRE", 125, 240, (0,0,0), 14)

                pygame.draw.rect(self.screen, (0,0,0), (50, 310, 150, 15), 2) # Bathroom
                pygame.draw.rect(self.screen, (100,200,0), (52, 312, self.mascota.bathroom * 1.46, 11))
                self.mostrar_t("BAÑO", 125, 290, (0,0,0), 14)

                pygame.draw.rect(self.screen, (0,0,0), (600, 260, 150, 15), 2) # Energy
                pygame.draw.rect(self.screen, (255,200,0), (602, 262, self.mascota.energy * 1.46, 11))
                self.mostrar_t("ENERGÍA", 675, 240, (0,0,0), 14)

                self.mostrar_t("Y:Comer X:Jugar B:Baño A:Dormir", 400, 360, (50,50,50), 18)
                if accion == "Y": self.mascota.hunger = max(0, self.mascota.hunger - 20)
                elif accion == "X": self.mascota.boredom = max(0, self.mascota.boredom - 20)
                elif accion == "B": self.mascota.bathroom = 0
                elif accion == "A": self.mascota.energy = 100

            elif self.modo == "SUB_CHISTES":
                pygame.draw.rect(self.screen, (255,255,255), (100, 100, 600, 200), border_radius=15)
                self.mostrar_t(self.chiste_actual["setup"], 400, 140, (0,0,0), 18)
                self.mostrar_t(self.chiste_actual["punch"], 400, 220, (200,0,0), 22)
                self.mostrar_t("A: OTRO | SELECT: SALIR", 400, 340, (50,50,50), 16)
                if accion == "A": self.obtener_nuevo_chiste(); pygame.time.delay(300)

            elif self.modo == "LEYENDO_CUENTO":
                sprite = self.sprite_manager.get_sprite("leyendo", size=180)
                self.screen.blit(sprite, (50, 100))
                pygame.draw.rect(self.screen, (255, 255, 245), self.rect_cuento, border_radius=15)
                f_c = pygame.font.SysFont(FUENTE_RETRO, 20)
                if self.paginas_cuento:
                    for i, linea in enumerate(self.paginas_cuento[self.pagina_actual]):
                        self.screen.blit(f_c.render(linea, True, (30,30,30)), (345, 85 + i * 28))
                if accion in ["DERECHA", "A"]:
                    if self.pagina_actual < len(self.paginas_cuento)-1: self.pagina_actual+=1; pygame.time.delay(200)
                elif accion == "IZQUIERDA":
                    if self.pagina_actual > 0: self.pagina_actual-=1; pygame.time.delay(200)

            elif self.modo == "EN_JUEGO":
                if self.juego.actualizar(accion): self.modo = "SUB_JUGAR"
                else: self.juego.dibujar(self.screen)

            pygame.display.flip(); self.clock.tick(60)

    def mostrar_t(self, txt, x=400, y=200, color=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

if __name__ == "__main__": BBotConsola().run()
