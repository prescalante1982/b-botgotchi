import pygame
import json
import os
import time
import math
from utils import obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN VISUAL ---
COLOR_FONDO = (20, 20, 40)
COLOR_NEON = (0, 255, 200)
COLOR_TEXTO = (255, 255, 255)
CONFIG_FILE = "config_pablo.json"
TALES_DIR = ".tales"

class BBotConsola:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400))
        pygame.display.set_caption("B-Botgotchi v3.0 - Pablo Alí")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicialización de Mando
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

        # Configuración de Controles
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "BOTON 1", "BOTON 4"]
        self.indice_cfg = 0
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.controles = json.load(f)
            self.modo = "MENU"
        else:
            self.modo = "CONFIG"

        # Variables de Estado
        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.hambre = 50
        self.energia = 50
        self.estado_bot = "NORMAL"
        self.timer_emo = 0
        self.menu_activo = None # "COMIDA" o "ENERGIA"
        self.sel_sub = 0
        
        # Variables de Cuentos (Locales)
        self.lista_cuentos = []
        self.sel_cuento_idx = 0
        self.lineas_cuento = []
        self.scroll_y = 0
        self.modo_lectura = "LISTA" # "LISTA" o "LEYENDO"
        self.texto_pantalla = "¡HOLA PABLO ALÍ!"
        
        # Variables de Juego
        self.mapa = []
        self.px = self.py = 0

    def cargar_lista_tales(self):
        if not os.path.exists(TALES_DIR):
            os.makedirs(TALES_DIR)
        archivos = [f for f in os.listdir(TALES_DIR) if f.endswith(".txt")]
        return archivos if archivos else []

    def cargar_contenido_cuento(self, nombre_archivo):
        ruta = os.path.join(TALES_DIR, nombre_archivo)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return f.readlines()
        except:
            return ["Error: No se pudo leer el archivo."]

    def cambiar_emo(self, emo, seg=2):
        self.estado_bot = emo
        self.timer_emo = time.time() + seg

    def mostrar_texto(self, txt, x=400, y=200, color=COLOR_TEXTO, size=22, centrar=True):
        font = pygame.font.SysFont("Arial", size, True)
        s = font.render(str(txt), True, color)
        pos = (x - s.get_width()//2, y) if centrar else (x, y)
        self.screen.blit(s, pos)

    def dibujar_bot(self, t, x=400, y_base=130, escala=1.0):
        f = math.sin(t * 0.005) * 10
        cx, cy = x, y_base + f
        # Cuerpo
        pygame.draw.rect(self.screen, (255,255,255), (cx-50*escala, cy-60*escala, 100*escala, 110*escala), border_radius=int(30*escala))
        # Pantalla cara
        pygame.draw.rect(self.screen, (20,20,30), (cx-35*escala, cy-35*escala, 70*escala, 50*escala), border_radius=int(10*escala))
        
        col = (255,255,0) if self.estado_bot == "RISA" else COLOR_NEON
        if self.estado_bot == "SUEÑO":
            pygame.draw.line(self.screen, (100,100,255), (cx-20*escala, cy-15*escala), (cx-5*escala, cy-15*escala), 4)
            pygame.draw.line(self.screen, (100,100,255), (cx+5*escala, cy-15*escala), (cx+20*escala, cy-15*escala), 4)
        else:
            pygame.draw.circle(self.screen, col, (int(cx-15*escala), int(cy-15*escala)), int(8*escala))
            pygame.draw.circle(self.screen, col, (int(cx+15*escala), int(cy-15*escala)), int(8*escala))

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            if time.time() > self.timer_emo: self.estado_bot = "NORMAL"
            self.screen.fill(COLOR_FONDO)

            # --- MODO CONFIGURACIÓN ---
            if self.modo == "CONFIG":
                self.mostrar_texto("CONFIGURACIÓN DE MANDO", y=100, color=COLOR_NEON, size=30)
                self.mostrar_texto(f"PABLO, PRESIONA: {self.pasos_config[self.indice_cfg]}", y=200, size=26)

            # --- MODO MENÚ PRINCIPAL ---
            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    sel = (self.seleccion == i)
                    c = (255,200,0) if sel else (60,60,90)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    txt_btn = pygame.font.SysFont("Arial", 18, True).render(opt, True, (0,0,0) if sel else (255,255,255))
                    self.screen.blit(txt_btn, (125+i*190-txt_btn.get_width()//2, 322))

            # --- MODO CUENTOS ---
            elif self.modo == "CUENTOS":
                if self.modo_lectura == "LISTA":
                    self.mostrar_texto("BIBLIOTECA", y=40, color=COLOR_NEON, size=30)
                    if not self.lista_cuentos:
                        self.mostrar_texto("No hay archivos .txt en /.tales", y=200, color=(200,50,50))
                    else:
                        for i, cuento in enumerate(self.lista_cuentos):
                            col = (255, 255, 0) if self.sel_cuento_idx == i else (150, 150, 150)
                            self.mostrar_texto(cuento.replace(".txt","").upper(), y=120+i*40, color=col, size=24)
                
                elif self.modo_lectura == "LEYENDO":
                    self.dibujar_bot(t, x=140, y_base=200, escala=0.9)
                    rect_txt = pygame.Rect(280, 40, 480, 320)
                    pygame.draw.rect(self.screen, (30, 30, 60), rect_txt, border_radius=15)
                    pygame.draw.rect(self.screen, COLOR_NEON, rect_txt, 2, border_radius=15)
                    
                    font_c = pygame.font.SysFont("
