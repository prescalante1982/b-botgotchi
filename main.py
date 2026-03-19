import pygame
import json
import os
import time
import math
from utils import obtener_chiste, obtener_cuento_dinamico, generar_laberinto

COLOR_FONDO = (20, 20, 40)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_pablo.json"

class BBotConsola:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Configuración de controles
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "BOTON 1", "BOTON 4"]
        self.indice_cfg = 0
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            self.modo = "MENU"
        else: self.modo = "CONFIG"

        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.texto_pantalla = "¡HOLA PABLO ALÍ!"
        
        # Variables Mascota
        self.hambre = 60
        self.energia = 80
        self.estado_bot = "NORMAL"
        self.timer_emo = 0
        self.sub_modo_comida = False
        self.sel_comida = 0
        self.comidas = ["PIZZA", "HAMBURGUESA", "AGUA"]

        # Variables Juego
        self.mapa = []; self.px = 0; self.py = 0
        self.historia = []; self.idx_cuento = 0

        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

    def cambiar_emo(self, emo, seg=2):
        self.estado_bot = emo
        self.timer_emo = time.time() + seg

    def mostrar_texto(self, txt, y_ini=260, color=(255,255,255)):
        font = pygame.font.SysFont("Arial", 22, True)
        palabras = txt.split()
        linea = ""
        for p in palabras:
            if len(linea + p) < 40: linea += p + " "
            else:
                s = font.render(linea, True, color)
                self.screen.blit(s, (400 - s.get_width()//2, y_ini))
                y_ini += 28; linea = p + " "
        s = font.render(linea, True, color)
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

            if self.modo == "MENU":
                self.dibujar_bot(t)
                for i, opt in enumerate(self.opciones):
                    sel = (self.seleccion == i)
                    c = (255,200,0) if sel else (60,60,90)
                    pygame.draw.rect(self.screen, c, (40+i*190, 310, 170, 50), border_radius=15)
                    txt = pygame.font.SysFont("Arial", 18, True).render(opt, True, (0,0,0) if sel else (255,255,255))
                    self.screen.blit(txt, (125+i*190-txt.get_width()//2, 322))

            elif self.modo == "MASCOTA":
                self.dibujar_bot(t)
                info = f"HAMBRE: {self.hambre}% | ENERGÍA: {self.energia}%"
                self.mostrar_texto(info, 240, COLOR_NEON)
                if not self.sub_modo_comida:
                    self.mostrar_texto(self.texto_pantalla, 280)
                else:
                    # Menú de Comida estilo 90s
                    for i, comida in enumerate(self.comidas):
                        col = (255,255,255) if self.sel_comida == i else (100,100,100)
                        txt = pygame.font.SysFont("Arial", 20, True).render(f"> {comida}" if self.sel_comida==i else comida, True, col)
                        self.screen.blit(txt, (400 - txt.get_width()//2, 280 + i*25))

            elif self.modo == "JUGAR":
                for r in range(8):
                    for c in range(8):
                        col = (40,40,60) if self.mapa[r][c] == 1 else (200,200,200)
                        if r == 7 and c == 7: col = (255,50,50)
                        pygame.draw.rect(self.screen, col, (240+c*40, 40+r*40, 38, 38), border_radius=5)
                pygame.draw.circle(self.screen, COLOR_NEON, (240+self.py*40+20, 40+self.px*40+20), 15)

            elif self.modo in ["CHISTES", "CUENTOS"]:
                self.dibujar_bot(t); self.mostrar_texto(self.texto_pantalla)

            # --- EVENTOS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                entrada = None
                if event.type == pygame.JOYBUTTONDOWN: entrada = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION and event.value != (0,0): entrada = {"tipo": "hat", "val": list(event.value)}

                if entrada:
                    if entrada == self.controles.get("BOTON 4"): 
                        self.modo = "MENU"; self.sub_modo_comida = False; continue

                    if self.modo == "MENU":
                        if entrada == self.controles.get("DERECHA"): self.seleccion = (self.seleccion+1)%4
                        elif entrada == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion-1)%4
                        elif entrada == self.controles.get("BOTON 1"):
                            self.modo = self.opciones[self.seleccion]
                            if self.modo == "CHISTES": self.texto_pantalla = obtener_chiste(); self.cambiar_emo("RISA")
                            elif self.modo == "CUENTOS": 
                                self.historia = obtener_cuento_dinamico()
                                self.idx_cuento = 0; self.texto_pantalla = self.historia[0]
                            elif self.modo == "JUGAR": self.mapa = generar_laberinto(); self.px = self.py = 0
                            elif self.modo == "MASCOTA": self.texto_pantalla = "B-Bot tiene hambre. (Boton 1)"

                    elif self.modo == "MASCOTA":
                        if not self.sub_modo_comida:
                            if entrada == self.controles.get("BOTON 1"): self.sub_modo_comida = True
                            elif entrada == self.controles.get("ARRIBA"): 
                                self.energia = 100; self.cambiar_emo("SUEÑO", 3); self.texto_pantalla = "Zzz..."
                        else:
                            if entrada == self.controles.get("ABAJO"): self.sel_comida = (self.sel_comida+1)%3
                            elif entrada == self.controles.get("ARRIBA"): self.sel_comida = (self.sel_comida-1)%3
                            elif entrada == self.controles.get("BOTON 1"):
                                comida = self.comidas[self.sel_comida]
                                self.hambre = max(0, self.hambre - 25)
                                self.texto_pantalla = f"¡ÑAM! LA {comida} ESTABA RICA."
                                self.cambiar_emo("RISA"); self.sub_modo_comida = False

                    elif self.modo == "JUGAR":
                        nx, ny = self.px, self.py
                        if entrada == self.controles.get("DERECHA"): ny += 1
                        elif entrada == self.controles.get("IZQUIERDA"): ny -= 1
                        elif entrada == self.controles.get("ARRIBA"): nx -= 1
                        elif entrada == self.controles.get("ABAJO"): nx += 1
                        if 0 <= nx < 8 and 0 <= ny < 8 and self.mapa[nx][ny] == 0:
                            self.px, self.py = nx, ny
                            if self.px == 7 and self.py == 7: self.cambiar_emo("RISA", 3); self.modo = "MENU"

                    elif self.modo == "CUENTOS" and entrada == self.controles.get("BOTON 1"):
                        self.idx_cuento += 1
                        if self.idx_cuento < len(self.historia): self.texto_pantalla = self.historia[self.idx_cuento]
                        else: self.modo = "MENU"

                    elif self.modo == "CHISTES" and entrada == self.controles.get("BOTON 1"):
                        self.texto_pantalla = obtener_chiste(); self.cambiar_emo("RISA")

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    BBotConsola().run()
