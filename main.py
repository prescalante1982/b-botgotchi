import pygame
import json
import os
import time
import math
from utils import obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
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
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Mando
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

        # Configuración inicial
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            self.modo = "MENU"
        else: self.modo = "CONFIG"

        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.hambre = 50; self.energia = 50
        self.estado_bot = "NORMAL"; self.timer_emo = 0
        
        # --- NUEVAS VARIABLES PARA CUENTOS ---
        self.lista_cuentos = []
        self.sel_cuento_idx = 0
        self.lineas_cuento = []
        self.scroll_y = 0 # Para navegar arriba/abajo
        self.modo_lectura = "LISTA" # LISTA o LEYENDO

    def cargar_lista_tales(self):
        if not os.path.exists(TALES_DIR): os.makedirs(TALES_DIR)
        archivos = [f for f in os.listdir(TALES_DIR) if f.endswith(".txt")]
        return archivos if archivos else ["No hay cuentos.txt"]

    def cargar_contenido_cuento(self, nombre_archivo):
        ruta = os.path.join(TALES_DIR, nombre_archivo)
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                return f.readlines()
        except: return ["Error al abrir el archivo."]

    def mostrar_texto_centrado(self, txt, y, color=COLOR_TEXTO, size=22):
        font = pygame.font.SysFont("Arial", size, True)
        s = font.render(str(txt), True, color)
        self.screen.blit(s, (400 - s.get_width()//2, y))

    def dibujar_bot(self, t, x=400, y_base=130):
        f = math.sin(t * 0.005) * 10
        cx, cy = x, y_base + f
        pygame.draw.rect(self.screen, (255,255,255), (cx-50, cy-60, 100, 110), border_radius=30)
        pygame.draw.rect(self.screen, (20,20,30), (cx-35, cy-35, 70, 50), border_radius=10)
        col = (255,255,0) if self.estado_bot == "RISA" else COLOR_NEON
        if self.estado_bot == "SUEÑO":
            pygame.draw.line(self.screen, (100,100,255), (cx-20, cy-15), (cx-5, cy-15), 4)
            pygame.draw.line(self.screen, (100,100,255), (cx+5, cy-15), (cx+20, cy-15), 4)
        else:
            pygame.draw.circle(self.screen, col, (cx-15, cy-15), 8)
            pygame.draw.circle(self.screen, col, (cx+15, cy-15), 8)

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            if time.time() > self.timer_emo: self.estado_bot = "NORMAL"
            self.screen.fill(COLOR_FONDO)

            if self.modo == "CONFIG":
                self.mostrar_texto_centrado("MODO CONFIGURACIÓN", 150)
            
            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    sel = (self.seleccion == i)
                    c = (255,200,0) if sel else (60,60,90)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    txt = pygame.font.SysFont("Arial", 18, True).render(opt, True, (0,0,0) if sel else (255,255,255))
                    self.screen.blit(txt, (125+i*190-txt.get_width()//2, 322))

            elif self.modo == "CUENTOS":
                if self.modo_lectura == "LISTA":
                    self.mostrar_texto_centrado("BIBLIOTECA DE PABLO ALÍ", 40, COLOR_NEON, 28)
                    for i, cuento in enumerate(self.lista_cuentos):
                        col = (255, 255, 0) if self.sel_cuento_idx == i else (150, 150, 150)
                        self.mostrar_texto_centrado(cuento.replace(".txt",""), 120 + i*40, col, 24)
                
                elif self.modo_lectura == "LEYENDO":
                    # B-Bot a la izquierda
                    self.dibujar_bot(t, x=150, y_base=200)
                    # Cuadro de lectura a la derecha
                    rect_lector = pygame.Rect(280, 40, 480, 320)
                    pygame.draw.rect(self.screen, (40, 40, 80), rect_lector, border_radius=15)
                    pygame.draw.rect(self.screen, COLOR_NEON, rect_lector, 3, border_radius=15)
                    
                    # Renderizar texto con Scroll
                    font_cuento = pygame.font.SysFont("Arial", 22)
                    for i, linea in enumerate(self.lineas_cuento):
                        y_pos = 60 + (i * 30) - (self.scroll_y * 30)
                        if 50 < y_pos < 330: # Solo dibujar lo que cabe en el cuadro
                            txt_surf = font_cuento.render(linea.strip(), True, COLOR_TEXTO)
                            self.screen.blit(txt_surf, (300, y_pos))

            elif self.modo == "MASCOTA":
                self.dibujar_bot(t); self.mostrar_texto_centrado(f"H: {self.hambre}% E: {self.energia}%", 280)

            elif self.modo == "JUGAR":
                for r in range(8):
                    for c in range(8):
                        col = (40,40,60) if self.mapa[r][c] == 1 else (200,200,200)
                        pygame.draw.rect(self.screen, col, (240+c*40, 40+r*40, 38, 38), border_radius=5)
                pygame.draw.circle(self.screen, COLOR_NEON, (240+self.py*40+20, 40+self.px*40+20), 15)

            elif self.modo == "CHISTES":
                self.dibujar_bot(t); self.mostrar_texto_centrado(self.texto_pantalla, 250)

            # --- EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                entrada = None
                if event.type == pygame.JOYBUTTONDOWN: entrada = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION and event.value != (0,0): entrada = {"tipo": "hat", "val": list(event.value)}

                if entrada:
                    if self.modo == "CONFIG":
                        self.controles[self.pasos_config[self.indice_cfg]] = entrada
                        self.indice_cfg += 1
                        if self.indice_cfg >= len(self.pasos_config):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                    
                    elif entrada == self.controles.get("BOTON 4"): 
                        if self.modo_lectura == "LEYENDO": self.modo_lectura = "LISTA"
                        else: self.modo = "MENU"

                    elif self.modo == "MENU":
                        if entrada == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                        elif entrada == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                        elif entrada == self.controles.get("BOTON 1"):
                            self.modo = self.opciones[self.seleccion]
                            if self.modo == "CUENTOS": 
                                self.lista_cuentos = self.cargar_lista_tales()
                                self.modo_lectura = "LISTA"
                            elif self.modo == "CHISTES": self.texto_pantalla = obtener_chiste()
                            elif self.modo == "JUGAR": self.mapa = generar_laberinto(); self.px = self.py = 0

                    elif self.modo == "CUENTOS":
                        if self.modo_lectura == "LISTA":
                            if entrada == self.controles.get("ABAJO"): self.sel_cuento_idx = (self.sel_cuento_idx + 1) % len(self.lista_cuentos)
                            elif entrada == self.controles.get("ARRIBA"): self.sel_cuento_idx = (self.sel_cuento_idx - 1) % len(self.lista_cuentos)
                            elif entrada == self.controles.get("BOTON 1"):
                                self.lineas_cuento = self.cargar_contenido_cuento(self.lista_cuentos[self.sel_cuento_idx])
                                self.scroll_y = 0; self.modo_lectura = "LEYENDO"
                        elif self.modo_lectura == "LEYENDO":
                            if entrada == self.controles.get("ABAJO"): self.scroll_y += 1
                            elif entrada == self.controles.get("ARRIBA"): self.scroll_y = max(0, self.scroll_y - 1)

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    BBotConsola().run()
