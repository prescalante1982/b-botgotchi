import pygame
import json
import os
import time
import math
import random
import requests
import threading

# --- CONFIGURACIÓN ESTÉTICA Y API ---
ANCHO, ALTO = 800, 400
CELESTE_CIELO = (173, 216, 230)
NEGRO_ESPACIO = (10, 10, 30)
CONFIG_FILE = "config_pablo.json"
SPRITE_SHEET = "bbot_sprite_sheet.PNG" 
JSON_CONFIG = "bbot_mascota.json"
FUENTE_RETRO = "Courier New"

# CONFIGURACIÓN CLIMA
API_KEY_WEATHER = "2f9b383d006c73b7d2d11226c5fdd10d"
CIUDAD = "Guatemala City"

# ==========================================
# GESTORES DE ENTORNO (CLIMA ASÍNCRONO)
# ==========================================

class WeatherManager:
    def __init__(self):
        self.clima_actual = "Clear"
        self.es_noche = False
        self.ultimo_check = 0
        self.temp = 25
        self.actualizando = False
        self.particulas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(60)]

    def _request_weather(self):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={CIUDAD}&appid={API_KEY_WEATHER}&units=metric"
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                data = r.json()
                self.clima_actual = data["weather"][0]["main"]
                self.temp = int(data["main"]["temp"])
                hora = time.localtime().tm_hour
                self.es_noche = hora < 6 or hora > 18
        except:
            pass
        self.actualizando = False

    def actualizar(self):
        ahora = pygame.time.get_ticks()
        # Cada 10 min y si no hay otra petición en curso
        if (ahora - self.ultimo_check > 600000 or self.ultimo_check == 0) and not self.actualizando:
            self.actualizando = True
            self.ultimo_check = ahora
            threading.Thread(target=self._request_weather, daemon=True).start()

    def dibujar_efectos(self, sc):
        color = (180, 180, 255) if self.clima_actual == "Rain" else (255, 255, 255)
        if self.clima_actual in ["Rain", "Drizzle", "Snow", "Clouds"]:
            for p in self.particulas:
                if self.clima_actual in ["Rain", "Drizzle"]:
                    p[1] += 12
                    pygame.draw.line(sc, color, (p[0], p[1]), (p[0], p[1]+6), 1)
                elif self.clima_actual == "Snow":
                    p[1] += 2
                    p[0] += math.sin(pygame.time.get_ticks() * 0.002)
                    pygame.draw.circle(sc, color, (int(p[0]), int(p[1])), 2)
                
                if p[1] > 400: p[1] = -10; p[0] = random.randint(0, 800)

    def obtener_fondo(self):
        if self.es_noche: return (15, 15, 45)
        climas = {"Clear": (135, 206, 235), "Clouds": (160, 175, 190), "Rain": (75, 85, 95), "Snow": (220, 230, 240)}
        return climas.get(self.clima_actual, CELESTE_CIELO)

# ==========================================
# LÓGICA DE MASCOTA
# ==========================================

class BBotSpriteManager:
    def __init__(self, atlas_path, json_path):
        if not os.path.exists(atlas_path):
            self.atlas = pygame.Surface((1024, 1024), pygame.SRCALPHA)
        else:
            self.atlas = pygame.image.load(atlas_path).convert_alpha()
        try:
            with open(json_path, 'r') as f: self.data = json.load(f)
        except:
            self.data = {"expressions": {"neutral": {"x":0, "y":0, "w":100, "h":100}}}
        
        self.sprites = {}
        for name, pos in self.data["expressions"].items():
            rect = pygame.Rect(pos["x"], pos["y"], pos["w"], pos["h"])
            self.sprites[name] = self.atlas.subsurface(rect)

    def get_sprite(self, name, size=None):
        sprite = self.sprites.get(name, self.sprites.get("neutral"))
        if size: return pygame.transform.scale(sprite, (int(size), int(size)))
        return sprite

class BBotPet:
    def __init__(self):
        self.hunger, self.energy, self.hygiene, self.training = 20, 100, 100, 0
        self.is_sleeping = self.is_sick = False
        self.last_tick = pygame.time.get_ticks()
        self.pensamiento = "¡Hola, Pablo!"
        # Lista de chistes en español integrada
        self.chistes_esp = [
            {"s": "¿Qué le dice un jaguar a otro?", "p": "¡Jaguar you!"},
            {"s": "¿Por qué el libro de matemáticas está triste?", "p": "Porque tiene muchos problemas."},
            {"s": "¿Qué hace una abeja en el gimnasio?", "p": "¡Zumba!"},
            {"s": "¿Cómo se dice pañuelo en japonés?", "p": "Saca-moko."},
            {"s": "¿Cuál es el baile favorito del tomate?", "p": "¡La salsa!"}
        ]

    def clock_tick(self, clima):
        ahora = pygame.time.get_ticks()
        if ahora - self.last_tick > 8000:
            if not self.is_sleeping:
                self.hunger = min(100, self.hunger + 3)
                self.energy = max(0, self.energy - 2)
                self.hygiene = max(0, self.hygiene - 2)
                if (self.hygiene < 20 or self.hunger > 80) and random.random() < 0.2:
                    self.is_sick = True
                if clima == "Rain": self.pensamiento = "¡Prefiero estar seco!"
                elif random.random() < 0.2:
                    self.pensamiento = random.choice(["Bip Bup Bap", "¡Programar es genial!", "Guatemala <3"])
            else:
                self.energy = min(100, self.energy + 10)
                if self.energy >= 100: self.is_sleeping = False
            self.last_tick = ahora

    def mood_expression(self):
        if self.is_sick: return "error"
        if self.is_sleeping: return "durmiendo"
        if self.hunger > 70: return "triste"
        return "neutral"

# ==========================================
# JUEGOS (Sin cambios para estabilidad)
# ==========================================
# (Clases JuegoNaves, JuegoCarreras, JuegoPacman se mantienen igual)
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
        for e in self.enemigos: pygame.draw.ellipse(sc, (200,100,255), (e[0]-22, e[1]-10, 44, 22))
        for b in self.balas: pygame.draw.rect(sc, (255,255,0), (b[0]-2, b[1], 4, 10))

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
        for o in self.obs: pygame.draw.rect(sc, (255,140,0), (o[0]-20, o[1], 40, 60), border_radius=6)

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
        pygame.display.set_caption("B-Bot Consola Pro + Weather")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        
        self.sprite_manager = BBotSpriteManager(SPRITE_SHEET, JSON_CONFIG)
        self.mascota = BBotPet()
        self.weather = WeatherManager()
        self.chiste_actual = {"setup": "Cargando...", "punch": ""}
        
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.idx_cfg = 0

        if not os.path.exists(CONFIG_FILE):
            self.modo = "CONFIG"
        else:
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.tales_dir = os.path.join(self.base_path, "tales")
        if not os.path.exists(self.tales_dir): os.makedirs(self.tales_dir)
        
        self.rect_cuento = pygame.Rect(320, 55, 440, 285)
        self.seleccion = 0; self.sel_juego = 0; self.idx_cuento = 0; self.pagina_actual = 0
        self.paginas_cuento = []

    def obtener_nuevo_chiste(self):
        # Chistes rápidos desde la lista interna (sin lentitud de red)
        ch = random.choice(self.mascota.chistes_esp)
        self.chiste_actual = {"setup": ch["s"], "punch": ch["p"]}

    def wrap_mejorado(self, texto, fuente, ancho_max):
        lineas = []; parrafos = texto.split('\n')
        for p in parrafos:
            palabras = p.split(' '); l_act = ""
            for pal in palabras:
                if fuente.size(l_act + pal)[0] < ancho_max: l_act += pal + " "
                else: lineas.append(l_act.strip()); l_act = pal + " "
            lineas.append(l_act.strip())
        return lineas

    def obtener_accion(self, ev):
        if not self.controles: return None
        for accion, m in self.controles.items():
            if ev.type == pygame.JOYBUTTONDOWN and m.get("tipo") == "btn" and ev.button == m["val"]: return accion
            if ev.type == pygame.JOYHATMOTION and m.get("tipo") == "hat" and list(ev.value) == m["val"]: return accion
            if ev.type == pygame.JOYAXISMOTION and m.get("tipo") == "axis" and ev.axis == m["axis"]:
                if (ev.value > 0.7 and m["val"] == 1) or (ev.value < -0.7 and m["val"] == -1): return accion
        if ev.type == pygame.KEYDOWN:
            keys = {pygame.K_LEFT: "IZQUIERDA", pygame.K_RIGHT: "DERECHA", pygame.K_UP: "ARRIBA", 
                    pygame.K_DOWN: "ABAJO", pygame.K_RETURN: "A", pygame.K_b: "B", 
                    pygame.K_x: "X", pygame.K_y: "Y", pygame.K_l: "L", pygame.K_r: "R", pygame.K_ESCAPE: "SELECT"}
            return keys.get(ev.key)
        return None

    def run(self):
        while self.running:
            self.weather.actualizar()
            fondo = (20, 20, 50) if self.mascota.is_sleeping else self.weather.obtener_fondo()
            self.screen.fill(fondo)
            if not self.mascota.is_sleeping: self.weather.dibujar_efectos(self.screen)
            
            t = pygame.time.get_ticks()
            self.mascota.clock_tick(self.weather.clima_actual)
            accion = None
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                if self.modo == "CONFIG":
                    m = None
                    if ev.type == pygame.JOYBUTTONDOWN: m = {"tipo": "btn", "val": ev.button}
                    elif ev.type == pygame.JOYHATMOTION and ev.value != (0,0): m = {"tipo": "hat", "val": list(ev.value)}
                    elif ev.type == pygame.JOYAXISMOTION and abs(ev.value) > 0.8:
                        m = {"tipo": "axis", "axis": ev.axis, "val": 1 if ev.value > 0 else -1}
                    if m:
                        self.controles[self.pasos_cfg[self.idx_cfg]] = m
                        self.idx_cfg += 1
                        pygame.time.delay(400)
                        if self.idx_cfg >= len(self.pasos_cfg):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                else:
                    accion = self.obtener_accion(ev)

            if accion == "SELECT": self.modo = "MENU"; self.juego = None

            if self.modo == "CONFIG":
                self.mostrar_t("CONFIGURAR MANDO", y=100, color=(0,0,0), size=30)
                self.mostrar_t(f"PULSA: {self.pasos_cfg[self.idx_cfg]}", y=220, color=(200,0,0), size=24)

            elif self.modo == "MENU":
                color_txt = (255,255,255) if self.weather.es_noche else (0,0,0)
                self.mostrar_t(f"{CIUDAD}: {self.weather.temp}°C | {self.weather.clima_actual}", 180, 10, color_txt, 14)
                
                latido = 1.0 + math.sin(t * 0.003) * 0.05
                flot = math.sin(t * 0.005) * 12
                sprite = self.sprite_manager.get_sprite(self.mascota.mood_expression(), size=160 * latido)
                self.screen.blit(sprite, (ANCHO//2 - sprite.get_width()//2, 100 + flot))
                
                if not self.mascota.is_sleeping:
                    pygame.draw.ellipse(self.screen, (255,255,255), (ANCHO//2 + 60, 60, 220, 60))
                    self.mostrar_t(self.mascota.pensamiento, ANCHO//2 + 170, 80, (50,50,50), size=16)

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
                self.screen.blit(sprite, (ANCHO//2 - sprite.get_width()//2, 20))
                self.dibujar_barra(50, 240, "HAMBRE [Y]", self.mascota.hunger, (200, 50, 50))
                self.dibujar_barra(50, 310, "HIGIENE [B]", self.mascota.hygiene, (50, 200, 200))
                self.dibujar_barra(550, 240, "ENERGÍA [A]", self.mascota.energy, (255, 200, 0))
                self.dibujar_barra(550, 310, "ENTRENA [L]", self.mascota.training, (100, 255, 100))
                if self.mascota.is_sick: self.mostrar_t("¡ENFERMO! [R]", 400, 220, (255,0,0), 22)
                
                if accion == "Y": self.mascota.hunger = max(0, self.mascota.hunger - 25)
                elif accion == "B": self.mascota.hygiene = 100
                elif accion == "A": self.mascota.is_sleeping = not self.mascota.is_sleeping
                elif accion == "L": self.mascota.training = min(100, self.mascota.training + 10)
                elif accion == "R" and self.mascota.is_sick: self.mascota.is_sick = False

            elif self.modo == "EN_JUEGO":
                if self.juego.actualizar(accion): self.modo = "SUB_JUGAR"
                else: self.juego.dibujar(self.screen)
            
            elif self.modo == "SUB_JUGAR":
                jgs = ["NAVES", "CARROS", "PACMAN"]
                for i, j in enumerate(jgs):
                    c = (255,255,255) if self.sel_juego == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (100+i*210, 200, 180, 60), border_radius=12)
                    self.mostrar_t(j, 100+i*210+90, 215, (0,0,0) if self.sel_juego==i else (255,255,255), size=20)
                if accion == "DERECHA": self.sel_juego = (self.sel_juego+1)%3
                elif accion == "IZQUIERDA": self.sel_juego = (self.sel_juego-1)%3
                elif accion == "A":
                    self.modo = "EN_JUEGO"
                    if self.sel_juego == 0: self.juego = JuegoNaves()
                    elif self.sel_juego == 1: self.juego = JuegoCarreras()
                    else: self.juego = JuegoPacman()

            elif self.modo == "SUB_CHISTES":
                pygame.draw.rect(self.screen, (255,255,255), (100, 100, 600, 200), border_radius=15)
                self.mostrar_t(self.chiste_actual["setup"], 400, 140, (0,0,0), 18)
                self.mostrar_t(self.chiste_actual["punch"], 400, 220, (200,0,0), 22)
                if accion == "A": self.obtener_nuevo_chiste()

            elif self.modo == "SUB_CUENTOS":
                try:
                    archivos = sorted([f for f in os.listdir(self.tales_dir) if f.endswith('.txt')])
                    if not archivos:
                        self.mostrar_t("Añade archivos .txt a la carpeta 'tales'", 400, 200, (0,0,0), 18)
                    else:
                        for i, nombre in enumerate(archivos[:6]):
                            bg = (0, 80, 200) if self.idx_cuento == i else (160, 200, 220)
                            pygame.draw.rect(self.screen, bg, (100, 90 + i*45, 600, 40), border_radius=10)
                            self.mostrar_t(nombre.replace(".txt", ""), 400, 98 + i*45, (255,255,255), size=20)
                        if accion == "ABAJO": self.idx_cuento = (self.idx_cuento + 1) % len(archivos)
                        elif accion == "ARRIBA": self.idx_cuento = (self.idx_cuento - 1) % len(archivos)
                        elif accion == "A":
                            with open(os.path.join(self.tales_dir, archivos[self.idx_cuento]), 'r', encoding='utf-8') as f:
                                txt = f.read()
                                self.paginas_cuento = [self.wrap_mejorado(txt, pygame.font.SysFont(FUENTE_RETRO, 20), 390)[i:i+9] for i in range(0, 1000, 9) if i < len(self.wrap_mejorado(txt, pygame.font.SysFont(FUENTE_RETRO, 20), 390))]
                            self.pagina_actual = 0; self.modo = "LEYENDO_CUENTO"
                except:
                    self.mostrar_t("Error al leer la carpeta de cuentos", 400, 200, (255,0,0), 18)

            elif self.modo == "LEYENDO_CUENTO":
                sprite = self.sprite_manager.get_sprite("leyendo", size=180)
                self.screen.blit(sprite, (50, 100))
                pygame.draw.rect(self.screen, (255, 255, 245), self.rect_cuento, border_radius=15)
                if self.paginas_cuento and self.pagina_actual < len(self.paginas_cuento):
                    for i, lin in enumerate(self.paginas_cuento[self.pagina_actual]):
                        self.screen.blit(pygame.font.SysFont(FUENTE_RETRO, 20).render(lin, True, (30,30,30)), (345, 85 + i*28))
                if accion in ["DERECHA", "A"] and self.pagina_actual < len(self.paginas_cuento)-1: self.pagina_actual += 1
                elif accion == "IZQUIERDA" and self.pagina_actual > 0: self.pagina_actual -= 1

            pygame.display.flip(); self.clock.tick(60)

    def dibujar_barra(self, x, y, nom, val, col):
        pygame.draw.rect(self.screen, (50,50,50), (x, y, 200, 25), border_radius=5)
        pygame.draw.rect(self.screen, col, (x+2, y+2, int(val * 1.96), 21), border_radius=5)
        self.mostrar_t(f"{nom}: {int(val)}%", x + 100, y - 25, (0,0,0) if not self.mascota.is_sleeping and not self.weather.es_noche else (255,255,255), 18)

    def mostrar_t(self, txt, x=400, y=200, color=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

if __name__ == "__main__": 
    BBotConsola().run()
