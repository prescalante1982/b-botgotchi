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
FUENTE_RETRO = "Courier New"

# ==========================================
# GESTOR DE SPRITES B-BOT
# ==========================================

class BBotSpriteManager:
    def __init__(self, atlas_path, json_path):
        # Cargamos la imagen y el JSON de configuración
        self.atlas = pygame.image.load(atlas_path).convert_alpha()
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        self.sprites = {}
        # Recortamos cada expresión según las coordenadas del JSON
        for name, pos in self.data["expressions"].items():
            rect = pygame.Rect(pos["x"], pos["y"], pos["w"], pos["h"])
            self.sprites[name] = self.atlas.subsurface(rect)

    def get_sprite(self, name, size=None):
        sprite = self.sprites.get(name, self.sprites.get("neutral"))
        if size:
            return pygame.transform.scale(sprite, (size, size))
        return sprite

# ==========================================
# LÓGICA DE JUEGOS (Se mantienen igual)
# ==========================================
# [Clases JuegoNaves, JuegoCarreras, JuegoPacman se mantienen igual que en tu código]

# (Aquí irían tus clases de juegos...)

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
        
        # --- CARGAR SPRITES REALES ---
        # Asegúrate de que los nombres de archivos coincidan
        self.sprite_manager = BBotSpriteManager("bbot_sprite_sheet.PNG", "bbot_mascota.json")
        
        self.pasos_cfg = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "A", "B", "X", "Y", "L", "R", "SELECT", "START"]
        self.idx_cfg = 0

        if not os.path.exists(CONFIG_FILE): 
            self.modo = "CONFIG"
        else:
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.seleccion = 0; self.sel_juego = 0; self.juego = None
        
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.tales_dir = os.path.join(self.base_path, "tales")
        if not os.path.exists(self.tales_dir): os.makedirs(self.tales_dir)
        
        self.lista_cuentos = []
        self.idx_cuento = 0
        self.paginas_cuento = []
        self.pagina_actual = 0
        self.rect_cuento = pygame.Rect(320, 55, 440, 285)

    # ... [Métodos obtener_accion, cargar_lista_tales, preparar_paginas, wrap_mejorado, leer_cuento se mantienen igual]

    def run(self):
        while self.running:
            self.screen.fill(CELESTE_CIELO)
            t = pygame.time.get_ticks()
            accion = None
            
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: self.running = False
                # ... (Lógica de configuración y obtener acción)
                accion = self.obtener_accion(ev)

            if accion == "SELECT": self.modo = "MENU"; self.juego = None

            if self.modo == "MENU":
                # Dibujamos al B-Bot alegre en el menú
                sprite = self.sprite_manager.get_sprite("alegre", size=180)
                flotacion = math.sin(t * 0.005) * 15
                self.screen.blit(sprite, (400 - 90, 80 + flotacion))

                opts = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
                for i, opt in enumerate(opts):
                    c = (255,255,255) if self.seleccion == i else (140, 190, 210)
                    pygame.draw.rect(self.screen, c, (40+i*185, 310, 165, 50), border_radius=15)
                    self.mostrar_t(opt, 40+i*185+82, 322, (0,0,0) if self.seleccion==i else (255,255,255), size=18)
                
                if accion == "DERECHA": self.seleccion = (self.seleccion+1)%4
                elif accion == "IZQUIERDA": self.seleccion = (self.seleccion-1)%4
                elif accion == "A": self.modo = "SUB_" + opts[self.seleccion]

            elif self.modo == "LEYENDO_CUENTO":
                self.screen.fill(CELESTE_CIELO)
                
                # B-Bot con expresión de "Leyendo"
                sprite = self.sprite_manager.get_sprite("leyendo", size=200)
                self.screen.blit(sprite, (60, 100))
                
                pygame.draw.rect(self.screen, (255, 255, 245), self.rect_cuento, border_radius=15)
                pygame.draw.rect(self.screen, (0, 0, 0), self.rect_cuento, 3, border_radius=15)
                
                # ... (Resto de lógica de dibujo de texto)

            elif self.modo == "SUB_MASCOTA":
                # Aquí el B-Bot se ve más grande y neutral o parpadeando
                sprite = self.sprite_manager.get_sprite("neutral", size=250)
                flotacion = math.sin(t * 0.002) * 10
                self.screen.blit(sprite, (400 - 125, 60 + flotacion))
                self.mostrar_t("¡HOLA PABLO ALÍ!", y=320, color=(0,0,0), size=35)

            # ... (Resto de modos)

            pygame.display.flip(); self.clock.tick(60)

    def mostrar_t(self, txt, x=400, y=200, color=(255,255,255), size=22):
        f = pygame.font.SysFont(FUENTE_RETRO, size, True)
        s = f.render(str(txt), True, color)
        self.screen.blit(s, (x - s.get_width()//2, y))

if __name__ == "__main__":
    BBotConsola().run()
