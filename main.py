import pygame
import json
import os
import time
import math
import random

# --- CONFIGURACIÓN ESTÉTICA ---
ANCHO, ALTO = 800, 400
CELESTE_CIELO = (173, 216, 230)
NEGRO_ESPACIO = (10, 10, 30)
CONFIG_FILE = "config_pablo.json"
SPRITE_SHEET = "bbot_sprite_sheet.PNG" 
JSON_CONFIG = "bbot_mascota.json"
FUENTE_RETRO = "Courier New"

# ==========================================
# LÓGICA DE LA MASCOTA (ADAPTADA)
# ==========================================

class BBotPet:
    def __init__(self, name="B-Bot"):
        self.name = name
        self.hunger = random.randrange(5)
        self.boredom = random.randrange(5)
        self.hunger_threshold = 10
        self.boredom_threshold = 10
        self.last_tick = pygame.time.get_ticks()

    def clock_tick(self):
        # Cada 5 segundos las necesidades aumentan
        ahora = pygame.time.get_ticks()
        if ahora - self.last_tick > 5000: 
            self.hunger += 1
            self.boredom += 1
            self.last_tick = ahora

    def mood_expression(self):
        # Mapeo de la lógica de humor a tus Sprites
        if self.hunger > self.hunger_threshold:
            return "triste" # Tiene hambre
        elif self.boredom > self.boredom_threshold:
            return "pensativo" # Está aburrido
        elif self.hunger < 3 and self.boredom < 3:
            return "alegre" # Está súper bien
        else:
            return "neutral"

    def feed(self):
        self.hunger = max(0, self.hunger - 4)

    def play(self):
        self.boredom = max(0, self.boredom - 4)

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
# JUEGOS (NAVES, CARRERAS, PACMAN) - [Se mantienen igual]
# ==========================================
# (Aquí van tus clases JuegoNaves, JuegoCarreras, JuegoPacman de los turnos anteriores)

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
        pygame.display.set_caption("B-Bot OS")
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock(); self.running = True; self.modo = "MENU"
        self.controles = {}
        
        self.sprite_manager = BBotSpriteManager(SPRITE_SHEET, JSON_CONFIG)
        self.mascota = BBotPet("B-Bot") # Inicializar mascota
        
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.idx_cfg = 0
        if not os.path.exists(CONFIG_FILE): self.modo = "CONFIG"
        else:
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.seleccion = 0; self.sel_juego = 0; self.juego = None
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.tales_dir = os.path.join(self.base_path, "tales")
        self.lista_cuentos = []
        self.idx_cuento = 0; self.paginas_cuento = []; self.pagina_actual = 0
        self.rect_cuento = pygame.Rect(320, 55, 440, 285)

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
            if ev.key == pygame.K_x: return "X" # Para jugar
            if ev.key == pygame.K_y: return "Y" # Para alimentar
            if ev.key == pygame.K_ESCAPE: return "SELECT"
        return None

    # [Cargar cuentos, preparar paginas, wrap, leer cuento - Se mantienen igual]

    def run(self):
        while self.running:
            self.screen.fill(CELESTE_CIELO)
            t = pygame.time.get_ticks()
            self.mascota.clock_tick() # Actualizar necesidades del B-Bot
            accion = None
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                accion = self.obtener_accion(ev)

            if accion == "SELECT": self.modo = "MENU"; self.juego = None

            if self.modo == "MENU":
                # El humor del B-Bot afecta su expresión en el menú
                expresion = self.mascota.mood_expression()
                sprite = self.sprite_manager.get_sprite(expresion, size=160)
                flotacion = math.sin(t * 0.005) * 12
                self.screen.blit(sprite, (400 - 80, 100 + flotacion))
                
                opts = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (40+i*185, 310, 165, 50), border_radius=15)
                    self.mostrar_t(opt, 40+i*185+82, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                if accion == "DERECHA": self.seleccion = (self.seleccion+1)%4
                elif accion == "IZQUIERDA": self.seleccion = (self.seleccion-1)%4
                elif accion == "A": self.modo = "SUB_" + opts[self.seleccion]

            elif self.modo == "SUB_MASCOTA":
                # Lógica visual de la Mascota
                exp = self.mascota.mood_expression()
                sprite = self.sprite_manager.get_sprite(exp, size=220)
                self.screen.blit(sprite, (ANCHO//2 - 110, 50))
                
                # Barras de estado
                pygame.draw.rect(self.screen, (0,0,0), (50, 300, 200, 20), 2) # Hambre
                pygame.draw.rect(self.screen, (200,50,50), (52, 302, min(196, self.mascota.hunger*15), 16))
                self.mostrar_t("HAMBRE", 150, 280, (0,0,0), 16)

                pygame.draw.rect(self.screen, (0,0,0), (550, 300, 200, 20), 2) # Aburrimiento
                pygame.draw.rect(self.screen, (50,50,200), (552, 302, min(196, self.mascota.boredom*15), 16))
                self.mostrar_t("ABURRIMIENTO", 650, 280, (0,0,0), 16)

                self.mostrar_t(f"¡HOLA, SOY {self.mascota.name}!", y=20, color=(0,0,0), size=25)
                self.mostrar_t("Y: Alimentar | X: Jugar", y=360, color=(50,50,50), size=18)

                if accion == "Y": 
                    self.mascota.feed()
                    # Feedback visual rápido
                    self.screen.blit(self.sprite_manager.get_sprite("comiendo", 220), (ANCHO//2 - 110, 50))
                    pygame.display.flip(); pygame.time.delay(500)
                elif accion == "X": 
                    self.mascota.play()
                    self.screen.blit(self.sprite_manager.get_sprite("picaron", 220), (ANCHO//2 - 110, 50))
                    pygame.display.flip(); pygame.time.delay(500)

            # [Resto de modos: LEYENDO_CUENTO, SUB_JUGAR, EN_JUEGO se mantienen igual]

            pygame.display.flip(); self.clock.tick(60)

    def mostrar_t(self, txt, x=400, y=200, color=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

if __name__ == "__main__":
    BBotConsola().run()
