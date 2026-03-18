import pygame
import json
import os
import time
import math
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_controles.json"

class BBotConsolaPro:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 1. CARGAR CONFIGURACIÓN
        self.controles = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.controles = json.load(f)
            self.modo_sistema = "MENU"
        else:
            self.modo_sistema = "CONFIG" # Si no hay archivo, pedir config (como antes)

        self.opciones = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.texto_pantalla = "¡HOLA PABLO ALI!"
        self.mapa_juego = []
        self.pos_pablo = [0, 0]

        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

    def dibujar_bbot(self, t, y_offset=0):
        flotar = math.sin(t * 0.005) * 15 + y_offset
        cx, cy = 400, 150 + flotar
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 140), border_radius=40)
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx-20, cy-15), 10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx+20, cy-15), 10)

    def dibujar_laberinto(self):
        self.screen.fill((40, 40, 60))
        tam, ox, oy = 40, 240, 40
        for f in range(8):
            for c in range(8):
                color = (80, 80, 150) if self.mapa_juego[f][c] == 1 else (220, 220, 250)
                if f == 7 and c == 7: color = (255, 215, 0) # Meta
                pygame.draw.rect(self.screen, color, (ox+c*tam, oy+f*tam, tam-4, tam-4), border_radius=5)
        # Jugador
        pygame.draw.circle(self.screen, COLOR_NEON, (ox+self.pos_pablo[1]*tam+18, oy+self.pos_pablo[0]*tam+18), 15)

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            self.screen.fill(COLOR_FONDO)

            if self.modo_sistema == "MENU":
                self.dibujar_bbot(t)
                for i, opt in enumerate(self.opciones):
                    es_sel = (self.seleccion == i)
                    col = (255, 200, 0) if es_sel else (100, 100, 150)
                    pygame.draw.rect(self.screen, col, (80 + i*170, 300, 150, 50), border_radius=15)
                    f = pygame.font.SysFont("Arial", 18, bold=True)
                    txt = f.render(opt, True, (30,30,60) if es_sel else (255,255,255))
                    self.screen.blit(txt, (155+i*170 - txt.get_width()//2, 315))
            
            elif self.modo_sistema == "JUGAR":
                self.dibujar_laberinto()
            
            elif self.modo_sistema in ["CHISTES", "CUENTOS", "MASCOTA"]:
                self.dibujar_bbot(t, y_offset=-50)
                f = pygame.font.SysFont("Arial", 22, bold=True)
                # Dividir texto largo para que quepa
                palabras = self.texto_pantalla.split()
                linea = ""
                y_txt = 280
                for p in palabras:
                    if len(linea + p) < 40: linea += p + " "
                    else:
                        ts = f.render(linea, True, (255,255,255))
                        self.screen.blit(ts, (400 - ts.get_width()//2, y_txt))
                        y_txt += 30; linea = p + " "
                ts = f.render(linea, True, (255,255,255))
                self.screen.blit(ts, (400 - ts.get_width()//2, y_txt))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                input_actual = None
                if event.type == pygame.JOYBUTTONDOWN: input_actual = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION: input_actual = {"tipo": "hat", "val": list(event.value)}

                if input_actual:
                    # SALIR SIEMPRE CON BOTON 4
                    if input_actual == self.controles.get("BOTON 4"):
                        self.modo_sistema = "MENU"
                        self.texto_pantalla = "¡DE VUELTA AL MENU!"

                    # LOGICA SEGUN MODO
                    elif self.modo_sistema == "MENU":
                        if input_actual == self.controles.get("DERECHA"): self.seleccion = (self.seleccion + 1) % 4
                        elif input_actual == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion - 1) % 4
                        elif input_actual == self.controles.get("BOTON 1"): # ENTRAR
                            self.modo_sistema = self.opciones[self.seleccion]
                            if self.modo_sistema == "JUGAR":
                                self.mapa_juego = generar_laberinto(8)
                                self.pos_pablo = [0,0]
                            elif self.modo_sistema == "CHISTES": self.texto_pantalla = obtener_chiste()
                            elif self.modo_sistema == "CUENTOS": self.texto_pantalla = "HABIA UNA VEZ UN ROBOT..."

                    elif self.modo_sistema == "CHISTES":
                        if input_actual in [self.controles.get("BOTON 1"), self.controles.get("BOTON 2")]:
                            self.texto_pantalla = obtener_chiste() # Otro chiste

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConsolaPro(); app.run()
