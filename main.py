import pygame
import json
import os
import time
import math
from utils import obtener_chiste, obtener_cuento_dinamico, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (20, 20, 40)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_pablo.json"

class BBotConsola:
    def __init__(self):
        pygame.init()
        pygame.joystick.init() # Inicialización crítica
        self.screen = pygame.display.set_mode((800, 400))
        pygame.display.set_caption("B-Botgotchi v2.6 - Pablo Alí")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Detectar Mando
        self.mando_conectado = pygame.joystick.get_count() > 0
        if self.mando_conectado:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

        # Cargar o Iniciar Configuración
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "BOTON 1", "BOTON 4"]
        self.indice_cfg = 0
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.controles = json.load(f)
            self.modo = "MENU"
        else:
            self.modo = "CONFIG"

        # Estados de la Mascota y Juego
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.hambre = 50
        self.energia = 50
        self.estado_bot = "NORMAL"
        self.timer_emo = 0
        self.menu_activo = None # "COMIDA" o "ENERGIA"
        self.sel_sub = 0
        self.items_comida = ["PIZZA", "HAMBURGUESA", "AGUA"]
        self.items_energia = ["DORMIR", "VITAMINA", "JUGAR"]
        
        self.texto_pantalla = "¡HOLA PABLO ALÍ!"
        self.mapa = []
        self.px = self.py = 0
        self.historia = []
        self.idx_cuento = 0

    def cambiar_emo(self, emo, seg=2):
        self.estado_bot = emo
        self.timer_emo = time.time() + seg

    def mostrar_texto(self, txt, y_ini=200, color=(255,255,255), size=24):
        font = pygame.font.SysFont("Arial", size, True)
        s = font.render(str(txt), True, color)
        self.screen.blit(s, (400 - s.get_width()//2, y_ini))

    def dibujar_bot(self, t):
        f = math.sin(t * 0.005) * 10
        cx, cy = 400, 130 + f
        pygame.draw.rect(self.screen, (255,255,255), (cx-60, cy-70, 120, 130), border_radius=35)
        pygame.draw.rect(self.screen, (20,20,30), (cx-45, cy-45, 90, 60), border_radius=10)
        
        col = (255,255,0) if self.estado_bot == "RISA" else COLOR_NEON
        if self.estado_bot == "SUEÑO":
            pygame.draw.line(self.screen, (100,100,255), (cx-30, cy-15), (cx-10, cy-15), 4)
            pygame.draw.line(self.screen, (100,100,255), (cx+10, cy-15), (cx+30, cy-15), 4)
        else:
            pygame.draw.circle(self.screen, col, (cx-20, cy-15), 10)
            pygame.draw.circle(self.screen, col, (cx+20, cy-15), 10)

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            if time.time() > self.timer_emo: self.estado_bot = "NORMAL"
            self.screen.fill(COLOR_FONDO)

            # --- LÓGICA DE VISUALIZACIÓN ---
            if pygame.joystick.get_count() == 0:
                self.mostrar_texto("¡CONECTA EL MANDO!", 180, (255,50,50), 30)
            
            elif self.modo == "CONFIG":
                self.mostrar_texto("CONFIGURACIÓN DE BOTONES", 100, COLOR_NEON)
                self.mostrar_texto(f"PABLO, PRESIONA: {self.pasos_config[self.indice_cfg]}", 200, (255,255,255), 28)

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    sel = (self.seleccion == i)
                    c = (255,200,0) if sel else (60,60,90)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    txt = pygame.font.SysFont("Arial", 18, True).render(opt, True, (0,0,0) if sel else (255,255,255))
                    self.screen.blit(txt, (125+i*190-txt.get_width()//2, 322))

            elif self.modo == "MASCOTA":
                self.dibujar_bot(t)
                self.mostrar_texto(f"HAMBRE: {self.hambre}%  |  ENERGÍA: {self.energia}%", 60, COLOR_NEON)
                if not self.menu_activo:
                    self.mostrar_texto("B1: COMER  |  ARRIBA: ENERGÍA", 280)
                else:
                    items = self.items_comida if self.menu_activo == "COMIDA" else self.items_energia
                    for i, item in enumerate(items):
                        col = (255,255,255) if self.sel_sub == i else (100,100,100)
                        self.mostrar_texto(f"> {item}" if self.sel_sub == i else item, 240 + i*30, col)

            elif self.modo == "JUGAR":
                for r in range(8):
                    for c in range(8):
                        col = (40,40,60) if self.mapa[r][c] == 1 else (200,200,200)
                        if r==7 and c==7: col=(255,50,50)
                        pygame.draw.rect(self.screen, col, (240+c*40, 40+r*40, 38, 38), border_radius=5)
                pygame.draw.circle(self.screen, COLOR_NEON, (240+self.py*40+20, 40+self.px*40+20), 15)

            elif self.modo in ["CHISTES", "CUENTOS"]:
                self.dibujar_bot(t)
                self.mostrar_texto(self.texto_pantalla, 270)

            # --- EVENTOS DE ENTRADA ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                entrada = None
                if event.type == pygame.JOYBUTTONDOWN:
                    entrada = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION and event.value != (0,0):
                    entrada = {"tipo": "hat", "val": list(event.value)}

                if entrada:
                    if self.modo == "CONFIG":
                        self.controles[self.pasos_config[self.indice_cfg]] = entrada
                        self.indice_cfg += 1
                        if self.indice_cfg >= len(self.pasos_
