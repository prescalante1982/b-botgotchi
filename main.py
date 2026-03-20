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
        pygame.display.set_caption("B-Botgotchi v3.4 - Pablo Alí")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "BOTON 1", "BOTON 4"]
        self.indice_cfg = 0
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            self.modo = "MENU"
        else:
            self.modo = "CONFIG"

        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.hambre = 50; self.energia = 50
        self.estado_bot = "NORMAL"; self.timer_emo = 0
        self.menu_activo = None; self.sel_sub = 0
        
        # Cuentos
        self.lista_cuentos = []; self.sel_cuento_idx = 0
        self.lineas_render = []; self.scroll_y = 0
        self.modo_lectura = "LISTA"; self.texto_pantalla = "¡HOLA PABLO ALÍ!"
        self.mapa = []; self.px = self.py = 0

    def cargar_lista_tales(self):
        if not os.path.exists(TALES_DIR): os.makedirs(TALES_DIR)
        archivos = [f for f in os.listdir(TALES_DIR) if f.endswith(".txt")]
        return archivos if archivos else []

    def preparar_cuento(self, archivo):
        """Carga el texto y lo divide para que quepa en el ancho del cuadro."""
        ruta = os.path.join(TALES_DIR, archivo)
        lineas_finales = []
        fuente = pygame.font.SysFont("Arial", 22)
        ancho_max = 440 # El cuadro mide 480, dejamos margen
        
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read().splitlines()
                for parrafo in contenido:
                    palabras = parrafo.split(' ')
                    linea_actual = ""
                    for palabra in palabras:
                        test_linea = linea_actual + palabra + " "
                        if fuente.size(test_linea)[0] < ancho_max:
                            linea_actual = test_linea
                        else:
                            lineas_finales.append(linea_actual)
                            linea_actual = palabra + " "
                    lineas_finales.append(linea_actual)
            return lineas_finales
        except:
            return ["Error al leer el archivo."]

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
        pygame.draw.rect(self.screen, (255,255,255), (cx-50*escala, cy-60*escala, 100*escala, 110*escala), border_radius=int(30*escala))
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

            if self.modo == "CONFIG":
                self.mostrar_texto("CONFIGURACIÓN", y=60, color=COLOR_NEON, size=30)
                self.mostrar_texto(f"PABLO, PRESIONA: {self.pasos_config[self.indice_cfg]}", y=180, size=28)

            elif self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    sel = (self.seleccion == i)
                    c = (255,200,0) if sel else (60,60,90)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    txt_btn = pygame.font.SysFont("Arial", 18, True).render(opt, True, (0,0,0) if sel else (255,255,255))
                    self.screen.blit(txt_btn, (125+i*190-txt_btn.get_width()//2, 322))

            elif self.modo == "CUENTOS":
                if self.modo_lectura == "LISTA":
                    self.mostrar_texto("BIBLIOTECA", y=40, color=COLOR_NEON, size=30)
                    if not self.lista_cuentos: self.mostrar_texto("No hay archivos en /.tales", y=200, color=(200,50,50))
                    else:
                        for i, cuento in enumerate(self.lista_cuentos):
                            col = (255, 255, 0) if self.sel_cuento_idx == i else (150, 150, 150)
                            self.mostrar_texto(cuento.replace(".txt","").upper(), y=120+i*40, color=col, size=24)
                elif self.modo_lectura == "LEYENDO":
                    self.dibujar_bot(t, x=140, y_base=200, escala=0.9)
                    rect_txt = pygame.Rect(280, 40, 480, 320)
                    pygame.draw.rect(self.screen, (30, 30, 60), rect_txt, border_radius=15)
                    pygame.draw.rect(self.screen, COLOR_NEON, rect_txt, 2, border_radius=15)
                    f_c = pygame.font.SysFont("Arial", 22)
                    for i, linea in enumerate(self.lineas_render):
                        y_p = 60 + (i * 30) - (self.scroll_y * 30)
                        if 50 < y_p < 330: self.screen.blit(f_c.render(linea.strip(), True, COLOR_TEXTO), (300, y_p))

            elif self.modo == "MASCOTA":
                self.dibujar_bot(t); self.mostrar_texto(f"HAMBRE: {self.hambre}% | ENERGÍA: {self.energia}%", y=60, color=COLOR_NEON)
                if not self.menu_activo: self.mostrar_texto("B1: COMIDA | ARRIBA: ENERGÍA", y=280)
                else:
                    it = ["PIZZA", "BURGER", "AGUA"] if self.menu_activo == "COMIDA" else ["DORMIR", "VITAMINA", "JUGAR"]
                    for i, item in enumerate(it):
                        col = (255,255,255) if self.sel_sub == i else (100,100,100)
                        self.mostrar_texto(f"> {item}" if self.sel_sub==i else item, y=240+i*30, color=col)

            elif self.modo == "JUGAR":
                for r in range(8):
                    for c in range(8):
                        cb = (40,40,60) if self.mapa[r][c] == 1 else (200,200,200)
                        if r==7 and c==7: cb=(255,50,50)
                        pygame.draw.rect(self.screen, cb, (240+c*40, 40+r*40, 38, 38), border_radius=5)
                pygame.draw.circle(self.screen, COLOR_NEON, (240+self.py*40+20, 40+self.px*40+20), 15)

            elif self.modo == "CHISTES":
                self.dibujar_bot(t); self.mostrar_texto(self.texto_pantalla, y=260, size=20)

            # --- EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                entrada = None
                if event.type == pygame.JOYBUTTONDOWN: entrada = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION and event.value != (0, 0): entrada = {"tipo": "hat", "val": list(event.value)}
                elif event.type == pygame.JOYAXISMOTION and abs(event.value) > 0.5: entrada = {"tipo": "axis", "val": [event.axis, 1 if event.value > 0 else -1]}

                if entrada:
                    if self.modo == "CONFIG":
                        self.controles[self.pasos_config[self.indice_cfg]] = entrada
                        self.indice_cfg += 1
                        if self.indice_cfg >= len(self.pasos_config):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                        pygame.time.wait(600)
                    
                    elif entrada == self.controles.get("BOTON 4"):
                        if self.modo == "CUENTOS" and self.modo_lectura == "LEYENDO": self.modo_lectura = "LISTA"
                        else: self.modo = "MENU"; self.menu_activo = None

                    elif self.modo == "MENU":
                        if entrada == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                        elif entrada == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                        elif entrada == self.controles.get("BOTON 1"):
                            self.modo = self.opciones[self.seleccion]
                            if self.modo == "CUENTOS": 
                                self.lista_cuentos = self.cargar_lista_tales()
                                self.modo_lectura = "LISTA"; self.sel_cuento_idx = 0
                            elif self.modo == "CHISTES": self.texto_pantalla = obtener_chiste(); self.cambiar_emo("RISA")
                            elif self.modo == "JUGAR": self.mapa = generar_laberinto(); self.px = self.py = 0

                    elif self.modo == "CUENTOS":
                        if self.modo_lectura == "LISTA" and self.lista_cuentos:
                            if entrada == self.controles.get("ABAJO"): self.sel_cuento_idx = (self.sel_cuento_idx+1)%len(self.lista_cuentos)
                            elif entrada == self.controles.get("ARRIBA"): self.sel_cuento_idx = (self.sel_cuento_idx-1)%len(self.lista_cuentos)
                            elif entrada == self.controles.get("BOTON 1"):
                                # USAMOS LA NUEVA FUNCIÓN DE PREPARAR CUENTO
                                self.lineas_render = self.preparar_cuento(self.lista_cuentos[self.sel_cuento_idx])
                                self.scroll_y = 0; self.modo_lectura = "LEYENDO"
                        elif self.modo_lectura == "LEYENDO":
                            if entrada == self.controles.get("ABAJO"): self.scroll_y += 1
                            elif entrada == self.controles.get("ARRIBA"): self.scroll_y = max(0, self.scroll_y - 1)

                    elif self.modo == "MASCOTA":
                        if not self.menu_activo:
                            if entrada == self.controles.get("BOTON 1"): self.menu_activo = "COMIDA"; self.sel_sub = 0
                            elif entrada == self.controles.get("ARRIBA"): self.menu_activo = "ENERGIA"; self.sel_sub = 0
                        else:
                            if entrada == self.controles.get("ABAJO"): self.sel_sub = (self.sel_sub+1)%3
                            elif entrada == self.controles.get("ARRIBA"): self.sel_sub = (self.sel_sub-1)%3
                            elif entrada == self.controles.get("BOTON 1"):
                                if self.menu_activo == "COMIDA": self.hambre = min(100, self.hambre+20); self.cambiar_emo("RISA")
                                else:
                                    if self.sel_sub == 0: self.energia = 100; self.cambiar_emo("SUEÑO", 3)
                                    else: self.energia = min(100, self.energia+25); self.cambiar_emo("RISA")
                                self.menu_activo = None

                    elif self.modo == "JUGAR":
                        nx, ny = self.px, self.py
                        if entrada == self.controles.get("DERECHA"): ny += 1
                        elif entrada == self.controles.get("IZQUIERDA"): ny -= 1
                        elif entrada == self.controles.get("ARRIBA"): nx -= 1
                        elif entrada == self.controles.get("ABAJO"): nx += 1
                        if 0 <= nx < 8 and 0 <= ny < 8 and self.mapa[nx][ny] == 0:
                            self.px, self.py = nx, ny
                            if self.px == 7 and self.py == 7: self.cambiar_emo("RISA", 3); self.modo = "MENU"

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    BBotConsola().run()
