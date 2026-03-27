import pygame
import json
import os
import time
import math
import random
import requests
import threading
import subprocess

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 800, 400
CONFIG_FILE = "config_pablo.json"
SPRITE_SHEET = "bbot_sprite_sheet.PNG" 
JSON_CONFIG = "bbot_mascota.json"
FUENTE_RETRO = "Courier New"

# --- RUTAS CORREGIDAS ---
PICO8_FOLDER = "/home/pi/Pico-8"
PICO8_PATH = "/home/pi/Pico-8/pico8"

API_KEY_WEATHER = "2f9b383d006c73b7d2d11226c5fdd10d"
CIUDAD = "Guatemala City"

# ==========================================
# GESTORES DE ENTORNO
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
                self.ultimo_check = pygame.time.get_ticks()
        except: pass
        self.actualizando = False

    def actualizar(self):
        ahora = pygame.time.get_ticks()
        if (ahora - self.ultimo_check > 600000 or self.ultimo_check == 0) and not self.actualizando:
            self.actualizando = True
            threading.Thread(target=self._request_weather, daemon=True).start()

    def dibujar_efectos(self, sc):
        color = (180, 180, 255) if self.clima_actual == "Rain" else (255, 255, 255)
        if self.clima_actual in ["Rain", "Drizzle", "Snow", "Clouds"]:
            for p in self.particulas:
                p[1] += 12 if "Rain" in self.clima_actual else 2
                if p[1] > 400: p[1] = -10; p[0] = random.randint(0, 800)
                pygame.draw.circle(sc, color, (int(p[0]), int(p[1])), 2)

    def obtener_fondo(self):
        if self.es_noche: return (15, 15, 45)
        climas = {"Clear": (135, 206, 235), "Clouds": (160, 175, 190), "Rain": (75, 85, 95), "Snow": (220, 230, 240)}
        return climas.get(self.clima_actual, (173, 216, 230))

# ==========================================
# LÓGICA DE MASCOTA
# ==========================================

class BBotSpriteManager:
    def __init__(self, atlas_path, json_path):
        if not os.path.exists(atlas_path): self.atlas = pygame.Surface((1024, 1024), pygame.SRCALPHA)
        else: self.atlas = pygame.image.load(atlas_path).convert_alpha()
        try:
            with open(json_path, 'r') as f: self.data = json.load(f)
        except: self.data = {"expressions": {"neutral": {"x":0, "y":0, "w":100, "h":100}}}
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
        self.chistes_esp = [{"s": "¿Qué le dice un jaguar a otro?", "p": "¡Jaguar you!"}, {"s": "¿Qué hace un perro con un taladro?", "p": "¡Está b-adrando!"}]

    def clock_tick(self, clima):
        ahora = pygame.time.get_ticks()
        if ahora - self.last_tick > 8000:
            if not self.is_sleeping:
                self.hunger = min(100, self.hunger + 3); self.energy = max(0, self.energy - 2)
                self.hygiene = max(0, self.hygiene - 2)
                if (self.hygiene < 20 or self.hunger > 80) and random.random() < 0.2: self.is_sick = True
                if clima == "Rain": self.pensamiento = "¡Mejor adentro!"
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
# JUEGOS INTERNOS (Omitidos los detalles para ahorrar espacio, mantén los tuyos)
# ==========================================

class JuegoNaves:
    def __init__(self): self.puntos = 0; self.vidas = 0
    def actualizar(self, a): return True
    def dibujar(self, s): pass

class JuegoCarreras:
    def __init__(self): self.puntos = 0; self.vidas = 0
    def actualizar(self, a): return True
    def dibujar(self, s): pass

class JuegoPacman:
    def __init__(self): self.puntos = 0; self.vidas = 0
    def actualizar(self, a): return True
    def dibujar(self, s): pass

# ==========================================
# CONSOLA PRINCIPAL
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init(); pygame.joystick.init()
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        self.sprite_manager = BBotSpriteManager(SPRITE_SHEET, JSON_CONFIG)
        self.mascota = BBotPet(); self.weather = WeatherManager()
        self.chiste_actual = {"setup": "Cargando...", "punch": ""}
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.idx_cfg = 0
        if not os.path.exists(CONFIG_FILE): self.modo = "CONFIG"
        else:
            try:
                with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            except: self.modo = "CONFIG"
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.tales_dir = os.path.join(self.base_path, "tales")
        if not os.path.exists(self.tales_dir): os.makedirs(self.tales_dir)
        self.rect_cuento = pygame.Rect(320, 55, 440, 285)
        self.seleccion = 0; self.sel_juego = 0; self.idx_cuento = 0; self.pagina_actual = 0; self.paginas_cuento = []

    # --- MÉTODO PARA LANZAR PICO-8 (NUEVA ESTRATEGIA) ---
    def lanzar_pico8(self):
        # Usamos flags con formato de un solo bloque para evitar que PICO-8 se pierda
        # -windowed 1 -width 384 -height 384 -x 208 -y 8
        cmd = [
            PICO8_PATH,
            "-splore",
            "-windowed", "1",
            "-width", "384",
            "-height", "384",
            "-x", "208",
            "-y", "8"
        ]
        
        pygame.display.iconify() 
        try:
            # shell=False es más limpio, cwd es obligatorio
            subprocess.run(cmd, cwd=PICO8_FOLDER)
        except Exception as e:
            print(f"Fallo total: {e}")
            
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED)
        self.modo = "MENU"

    def obtener_nuevo_chiste(self):
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
                if (ev.value > 0.8 and m["val"] == 1) or (ev.value < -0.8 and m["val"] == -1): return accion
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
            t = pygame.time.get_ticks(); self.mascota.clock_tick(self.weather.clima_actual)
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
                        self.idx_cfg += 1; pygame.time.delay(600)
                        if self.idx_cfg >= len(self.pasos_cfg):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                else: accion = self.obtener_accion(ev)
            
            if accion == "SELECT": self.modo = "MENU"; self.juego = None
            
            if self.modo == "CONFIG":
                self.mostrar_t("CONFIGURA TU MANDO", y=100, color=(0,0,0), size=30)
                self.mostrar_t(f"PULSA: {self.pasos_cfg[self.idx_cfg]}", y=220, color=(200,0,0), size=24)
            elif self.modo == "MENU":
                col_t = (255,255,255) if self.weather.es_noche else (0,0,0)
                self.mostrar_t(f"{CIUDAD}: {self.weather.temp}C", 180, 10, col_t, 14)
                lat = 1.0 + math.sin(t * 0.003) * 0.05
                flo = math.sin(t * 0.005) * 12
                spr = self.sprite_manager.get_sprite(self.mascota.mood_expression(), size=160 * lat)
                self.screen.blit(spr, (ANCHO//2 - spr.get_width()//2, 100 + flo))
                
                opts = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS", "ARCADE"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    x_btn = 15 + i*158 
                    pygame.draw.rect(self.screen, c, (x_btn, 310, 145, 50), border_radius=15)
                    self.mostrar_t(opt, x_btn+72, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=16)
                
                if accion == "DERECHA": self.seleccion = (self.seleccion+1)%len(opts)
                elif accion == "IZQUIERDA": self.seleccion = (self.seleccion-1)%len(opts)
                elif accion == "A": 
                    if opts[self.seleccion] == "ARCADE": self.lanzar_pico8()
                    else: self.modo = "SUB_" + opts[self.seleccion]
            
            # (Resto de estados: SUB_MASCOTA, SUB_CHISTES, etc. omitidos por brevedad)
            pygame.display.flip(); self.clock.tick(60)

    def mostrar_t(self, txt, x=400, y=200, color=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

if __name__ == "__main__": BBotConsola().run()
