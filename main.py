import pygame
import json
import os
import time
import math
import random
import requests
import threading

# --- CONFIGURACIÓN ---
ANCHO, ALTO = 800, 400
CONFIG_FILE = "config_pablo.json"
SPRITE_SHEET = "bbot_sprite_sheet.PNG" 
JSON_CONFIG = "bbot_mascota.json"
FUENTE_RETRO = "Courier New"

# API CLIMA PABLO
API_KEY_WEATHER = "2f9b383d006c73b7d2d11226c5fdd10d"
CIUDAD = "Guatemala City"

# ==========================================
# GESTORES (CLIMA ASÍNCRONO)
# ==========================================

class WeatherManager:
    def __init__(self):
        self.clima_actual = "Clear"
        self.es_noche = False
        self.temp = 25
        self.actualizando = False
        self.particulas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(50)]
        self.ultimo_check = 0

    def pedir_clima_thread(self):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={CIUDAD}&appid={API_KEY_WEATHER}&units=metric"
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                data = r.json()
                self.clima_actual = data["weather"][0]["main"]
                self.temp = int(data["main"]["temp"])
                hora = time.localtime().tm_hour
                self.es_noche = hora < 6 or hora > 18
        except: pass
        self.actualizando = False

    def actualizar(self):
        ahora = pygame.time.get_ticks()
        if (ahora - self.ultimo_check > 600000 or self.ultimo_check == 0) and not self.actualizando:
            self.actualizando = True
            self.ultimo_check = ahora
            threading.Thread(target=self.pedir_clima_thread, daemon=True).start()

    def dibujar_efectos(self, sc):
        if self.clima_actual in ["Rain", "Drizzle", "Snow"]:
            col = (180, 180, 255) if "Rain" in self.clima_actual else (255, 255, 255)
            for p in self.particulas:
                p[1] += 10 if "Rain" in self.clima_actual else 2
                if p[1] > 400: p[1] = -10; p[0] = random.randint(0, 800)
                pygame.draw.line(sc, col, (p[0], p[1]), (p[0], p[1]+5), 1)

    def obtener_fondo(self):
        if self.es_noche: return (10, 10, 30)
        climas = {"Clear": (135, 206, 235), "Clouds": (160, 175, 190), "Rain": (75, 85, 95)}
        return climas.get(self.clima_actual, (173, 216, 230))

# ==========================================
# LÓGICA DE MASCOTA Y SPRITES
# ==========================================

class BBotSpriteManager:
    def __init__(self, atlas_path, json_path):
        if not os.path.exists(atlas_path):
            self.atlas = pygame.Surface((1024, 1024), pygame.SRCALPHA)
        else:
            self.atlas = pygame.image.load(atlas_path).convert_alpha()
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
        self.pensamiento = "¡Hola Pablo!"
        self.chistes = [
            {"s": "¿Qué le dice un jaguar a otro?", "p": "Jaguar you!"},
            {"s": "¿Por qué el libro de mates está triste?", "p": "Muchos problemas..."},
            {"s": "¿Qué hace una abeja en el gimnasio?", "p": "¡Zumba!"},
            {"s": "¿Cómo se dice pañuelo en japonés?", "p": "Saca-moko"},
            {"s": "¿Cuál es el baile del tomate?", "p": "¡La salsa!"}
        ]
        self.chiste_actual = self.chistes[0]

    def clock_tick(self, clima):
        ahora = pygame.time.get_ticks()
        if ahora - self.last_tick > 8000:
            if not self.is_sleeping:
                self.hunger = min(100, self.hunger + 3)
                self.energy = max(0, self.energy - 2)
                if self.hunger > 80: self.is_sick = True
                if clima == "Rain": self.pensamiento = "¡Está lloviendo!"
                elif random.random() < 0.2: self.pensamiento = "¡Bip Bup Bap!"
            else:
                self.energy = min(100, self.energy + 10)
                if self.energy >= 100: self.is_sleeping = False
            self.last_tick = ahora

    def mood(self):
        if self.is_sick: return "error"
        if self.is_sleeping: return "durmiendo"
        if self.hunger > 70: return "triste"
        return "neutral"

# ==========================================
# CONSOLA PRINCIPAL (TODO JUNTO)
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO), pygame.SCALED)
        pygame.display.set_caption("B-Bot Pro v3 - Edición Pablo")
        self.clock = pygame.time.Clock()
        self.running = True
        self.modo = "MENU"
        self.seleccion = 0
        self.sel_juego = 0
        
        self.sprite_manager = BBotSpriteManager(SPRITE_SHEET, JSON_CONFIG)
        self.mascota = BBotPet()
        self.weather = WeatherManager()
        self.tales_dir = "tales"
        if not os.path.exists(self.tales_dir): os.makedirs(self.tales_dir)
        
        # Cargar mandos
        self.controles = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        else: self.modo = "CONFIG"

    def mostrar_t(self, txt, x, y, col=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, col)
        self.screen.blit(s, (x - s.get_width()//2, y))

    def dibujar_barra(self, x, y, nom, val, col):
        pygame.draw.rect(self.screen, (50,50,50), (x, y, 200, 25), border_radius=5)
        pygame.draw.rect(self.screen, col, (x+2, y+2, int(val * 1.96), 21), border_radius=5)
        color_txt = (0,0,0) if not self.weather.es_noche else (255,255,255)
        self.mostrar_t(f"{nom}: {int(val)}%", x+100, y-25, color_txt, 18)

    def run(self):
        while self.running:
            self.weather.actualizar()
            fondo = (20, 20, 40) if self.mascota.is_sleeping else self.weather.obtener_fondo()
            self.screen.fill(fondo)
            if not self.mascota.is_sleeping: self.weather.dibujar_efectos(self.screen)
            
            t = pygame.time.get_ticks()
            self.mascota.clock_tick(self.weather.clima_actual)
            accion = None
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                if ev.type == pygame.KEYDOWN:
                    keys = {pygame.K_LEFT: "IZQUIERDA", pygame.K_RIGHT: "DERECHA", pygame.K_UP: "ARRIBA", 
                            pygame.K_DOWN: "ABAJO", pygame.K_RETURN: "A", pygame.K_b: "B", 
                            pygame.K_x: "X", pygame.K_y: "Y", pygame.K_l: "L", pygame.K_r: "R", pygame.K_ESCAPE: "SELECT"}
                    accion = keys.get(ev.key)

            if accion == "SELECT": self.modo = "MENU"

            # --- MENU PRINCIPAL ---
            if self.modo == "MENU":
                color_txt = (255,255,255) if self.weather.es_noche else (0,0,0)
                self.mostrar_t(f"Guatemala: {self.weather.temp}°C | {self.weather.clima_actual}", 180, 10, color_txt, 14)
                
                # B-Bot Animado
                latido = 1.0 + math.sin(t * 0.003) * 0.05
                flot = math.sin(t * 0.005) * 12
                sprite = self.sprite_manager.get_sprite(self.mascota.mood(), size=160 * latido)
                self.screen.blit(sprite, (ANCHO//2 - sprite.get_width()//2, 100 + flot))
                
                # Pensamiento
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
                elif accion == "A": self.modo = "SUB_" + opts[self.seleccion]

            # --- SUB MODOS ---
            elif self.modo == "SUB_MASCOTA":
                sprite = self.sprite_manager.get_sprite(self.mascota.mood(), size=200)
                self.screen.blit(sprite, (ANCHO//2 - sprite.get_width()//2, 20))
                self.dibujar_barra(50, 240, "HAMBRE [Y]", self.mascota.hunger, (200, 50, 50))
                self.dibujar_barra(550, 240, "ENERGÍA [A]", self.mascota.energy, (255, 200, 0))
                if accion == "Y": self.mascota.hunger = max(0, self.mascota.hunger - 25)
                if accion == "A": self.mascota.is_sleeping = not self.mascota.is_sleeping

            elif self.modo == "SUB_CHISTES":
                pygame.draw.rect(self.screen, (255,255,255), (100, 100, 600, 200), border_radius=15)
                self.mostrar_t(self.mascota.chiste_actual["s"], 400, 140, (0,0,0), 18)
                self.mostrar_t(self.mascota.chiste_actual["p"], 400, 220, (200,0,0), 22)
                if accion == "A": self.mascota.chiste_actual = random.choice(self.mascota.chistes)

            elif self.modo == "SUB_CUENTOS":
                archivos = sorted([f for f in os.listdir(self.tales_dir) if f.endswith('.txt')])
                if not archivos: self.mostrar_t("Añade cuentos a la carpeta 'tales'", 400, 200, (0,0,0), 20)
                for i, n in enumerate(archivos[:5]):
                    self.mostrar_t(n.replace(".txt",""), 400, 100 + i*45, (255,255,255), 20)

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    BBotConsola().run()
