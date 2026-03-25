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

# CLIMA (API de Pablo)
API_KEY_WEATHER = "2f9b383d006c73b7d2d11226c5fdd10d"
CIUDAD = "Guatemala City"

# ==========================================
# GESTOR DE CLIMA (AHORA ASÍNCRONO)
# ==========================================

class WeatherManager:
    def __init__(self):
        self.clima_actual = "Clear"
        self.es_noche = False
        self.temp = 25
        self.actualizando = False
        self.particulas = [[random.randint(0, 800), random.randint(0, 400)] for _ in range(40)]

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
        # Solo intenta conectar cada 10 minutos y si no está ya buscando
        if not self.actualizando:
            self.actualizando = True
            threading.Thread(target=self.pedir_clima_thread, daemon=True).start()

    def dibujar_efectos(self, sc):
        if self.clima_actual in ["Rain", "Drizzle", "Snow"]:
            color = (180, 180, 255) if "Rain" in self.clima_actual else (255, 255, 255)
            for p in self.particulas:
                p[1] += 10 if "Rain" in self.clima_actual else 2
                if p[1] > 400: p[1] = -10; p[0] = random.randint(0, 800)
                pygame.draw.circle(sc, color, (int(p[0]), int(p[1])), 2)

    def obtener_fondo(self):
        if self.es_noche: return (10, 10, 30)
        climas = {"Clear": (135, 206, 235), "Clouds": (160, 175, 190), "Rain": (75, 85, 95)}
        return climas.get(self.clima_actual, (173, 216, 230))

# ==========================================
# LÓGICA DE MASCOTA Y CHISTES
# ==========================================

class BBotPet:
    def __init__(self):
        self.hunger, self.energy, self.hygiene, self.training = 20, 100, 100, 0
        self.is_sleeping = self.is_sick = False
        self.last_tick = pygame.time.get_ticks()
        self.pensamiento = "¡Hola Pablo!"
        self.lista_chistes = [
            {"s": "¿Qué le dice un jaguar a otro?", "p": "Jaguar you!"},
            {"s": "¿Cuál es el baile favorito del tomate?", "p": "¡La salsa!"},
            {"s": "¿Qué hace una abeja en el gimnasio?", "p": "¡Zumba!"},
            {"s": "¿Cómo se dice pañuelo en japonés?", "p": "Saca-moko"},
            {"s": "¿Por qué el libro de matemáticas está triste?", "p": "Porque tiene muchos problemas"},
            {"s": "¿Qué le dice una impresora a otra?", "p": "¿Esa hoja es tuya o es una impresión mía?"}
        ]
        self.chiste_actual = self.lista_chistes[0]

    def nuevo_chiste(self):
        self.chiste_actual = random.choice(self.lista_chistes)

    def clock_tick(self, clima):
        ahora = pygame.time.get_ticks()
        if ahora - self.last_tick > 8000:
            if not self.is_sleeping:
                self.hunger = min(100, self.hunger + 2)
                self.energy = max(0, self.energy - 1)
                if self.hunger > 80: self.is_sick = True
                self.pensamiento = "¡Bip Bup!" if clima != "Rain" else "¡Odio mojarme!"
            else:
                self.energy = min(100, self.energy + 8)
                if self.energy >= 100: self.is_sleeping = False
            self.last_tick = ahora

# ==========================================
# CONSOLA PRINCIPAL (OPTIMIZADA)
# ==========================================

class BBotConsola:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("B-Bot Pro v3")
        self.clock = pygame.time.Clock()
        self.running = True
        self.modo = "MENU"
        self.controles = {}
        
        # Cargar configuración o forzar si no existe
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        else: self.modo = "CONFIG"

        # Managers
        try:
            from bbot_logic import BBotSpriteManager # Si tienes el archivo aparte
        except:
            class DummySprite:
                def get_sprite(self, n, size=100): return pygame.Surface((size, size))
            self.sprite_manager = DummySprite()

        self.mascota = BBotPet()
        self.weather = WeatherManager()
        self.weather.actualizar() # Primer carga
        
        # Cuentos
        self.tales_dir = "tales"
        if not os.path.exists(self.tales_dir): os.makedirs(self.tales_dir)
        self.idx_cuento = 0
        self.paginas_cuento = []

    def obtener_accion(self, ev):
        if ev.type == pygame.KEYDOWN:
            keys = {pygame.K_LEFT: "IZQUIERDA", pygame.K_RIGHT: "DERECHA", pygame.K_UP: "ARRIBA", 
                    pygame.K_DOWN: "ABAJO", pygame.K_RETURN: "A", pygame.K_b: "B", 
                    pygame.K_x: "X", pygame.K_y: "Y", pygame.K_l: "L", pygame.K_r: "R", pygame.K_ESCAPE: "SELECT"}
            return keys.get(ev.key)
        return None

    def mostrar_t(self, txt, x, y, col=(255,255,255), size=20):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, col)
        self.screen.blit(s, (x - s.get_width()//2, y))

    def dibujar_barra(self, x, y, nom, val, col):
        pygame.draw.rect(self.screen, (40,40,40), (x, y, 180, 20), border_radius=5)
        pygame.draw.rect(self.screen, col, (x+2, y+2, int(val * 1.76), 16), border_radius=3)
        self.mostrar_t(f"{nom} {int(val)}%", x+90, y-22, (0,0,0) if not self.weather.es_noche else (255,255,255), 16)

    def run(self):
        while self.running:
            # Control de FPS para que no consuma toda la CPU
            self.clock.tick(60)
            
            # Fondo y Clima
            fondo = (20, 20, 40) if self.mascota.is_sleeping else self.weather.obtener_fondo()
            self.screen.fill(fondo)
            if not self.mascota.is_sleeping: self.weather.dibujar_efectos(self.screen)
            
            self.mascota.clock_tick(self.weather.clima_actual)
            accion = None
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                accion = self.obtener_accion(ev)

            if accion == "SELECT": self.modo = "MENU"

            # --- MODO MENU ---
            if self.modo == "MENU":
                self.mostrar_t(f"Guatemala: {self.weather.temp}°C | {self.weather.clima_actual}", 400, 10, (0,0,0) if not self.weather.es_noche else (255,255,255), 14)
                pygame.draw.circle(self.screen, (255,255,255), (400, 180), 80) # Lugar del B-Bot
                self.mostrar_t(self.mascota.pensamiento, 400, 80, (0,0,0), 18)
                
                opts = ["JUEGOS", "MASCOTA", "CHISTES", "CUENTOS"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if (pygame.time.get_ticks()//500)%2==0 else (200,200,200)
                    self.mostrar_t(opt, 100 + i*200, 340, c, 22)
                
                if accion == "A": self.modo = "SUB_" + opts[random.randint(0,3)] # Ejemplo simple

            # --- MODO MASCOTA ---
            elif self.modo == "SUB_MASCOTA":
                self.dibujar_barra(50, 100, "HAMBRE [Y]", self.mascota.hunger, (200,50,50))
                self.dibujar_barra(550, 100, "ENERGÍA [A]", self.mascota.energy, (255,200,0))
                self.mostrar_t("PULSA SELECT PARA VOLVER", 400, 350, (0,0,0), 16)
                if accion == "Y": self.mascota.hunger = max(0, self.mascota.hunger - 20)
                if accion == "A": self.mascota.is_sleeping = not self.mascota.is_sleeping

            # --- MODO CHISTES (EN ESPAÑOL) ---
            elif self.modo == "SUB_CHISTES":
                pygame.draw.rect(self.screen, (255,255,255), (100, 100, 600, 200), border_radius=20)
                self.mostrar_t(self.mascota.chiste_actual["s"], 400, 140, (0,0,0), 18)
                self.mostrar_t(self.mascota.chiste_actual["p"], 400, 210, (200,0,0), 24)
                self.mostrar_t("PULSA [A] PARA OTRO", 400, 260, (100,100,100), 14)
                if accion == "A": self.mascota.nuevo_chiste()

            # --- MODO CUENTOS (CORREGIDO) ---
            elif self.modo == "SUB_CUENTOS":
                try:
                    archivos = [f for f in os.listdir(self.tales_dir) if f.endswith('.txt')]
                    if not archivos:
                        self.mostrar_t("No hay cuentos en la carpeta /tales", 400, 200, (0,0,0), 20)
                    else:
                        for i, f in enumerate(archivos[:5]):
                            col = (255,255,0) if i == self.idx_cuento else (255,255,255)
                            self.mostrar_t(f.replace(".txt",""), 400, 100 + i*40, col, 20)
                except:
                    self.mostrar_t("Error al leer cuentos", 400, 200, (255,0,0), 20)

            pygame.display.flip()

if __name__ == "__main__":
    BBotConsola().run()
