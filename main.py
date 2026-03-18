import pygame
import json
import os
import time
import math
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_controles.json"

class BBotGamer:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Cargar Controles
        self.controles = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.opciones_menu = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.modo = "MENU"
        self.seleccion = 0
        
        # Estados de las secciones
        self.texto_pantalla = ""
        self.deseo_mascota = ""
        self.indice_cuento = 0
        self.historia_actual = []

        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

    def obtener_nuevo_cuento(self):
        # Lista de partes de un cuento
        return [
            "Había una vez un robot que vivía en Guatemala...",
            "Un día, encontró un joystick mágico enterrado.",
            "Al tocarlo, ¡sus ojos brillaron de color neón!",
            "Ahora ayuda a Pablo Alí a ganar todos los juegos.",
            "FIN. ¡Presiona Botón 4 para volver!"
        ]

    def dibujar_bbot(self, t, estado="NORMAL"):
        # Animación base
        flotar = math.sin(t * 0.005) * 15
        color_ojos = COLOR_NEON
        if estado == "FELIZ": color_ojos = (255, 255, 0) # Amarillo
        if estado == "TRISTE": color_ojos = (255, 100, 100) # Rojo
        
        cx, cy = 400, 140 + flotar
        # Cabeza
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 130), border_radius=30)
        # Pantalla
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        # Ojos
        pygame.draw.circle(self.screen, color_ojos, (cx-20, cy-15), 10)
        pygame.draw.circle(self.screen, color_ojos, (cx+20, cy-15), 10)

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            self.screen.fill(COLOR_FONDO)

            # --- RENDERIZADO SEGÚN EL MODO ---
            if self.modo == "MENU":
                self.dibujar_bbot(t)
                for i, opt in enumerate(self.opciones_menu):
                    es_sel = (self.seleccion == i)
                    col = (255, 200, 0) if es_sel else (100, 100, 150)
                    pygame.draw.rect(self.screen, col, (80 + i*170, 300, 150, 50), border_radius=15)
                    f = pygame.font.SysFont("Arial", 18, bold=True)
                    txt = f.render(opt, True, (30,30,60) if es_sel else (255,255,255))
                    self.screen.blit(txt, (155+i*170 - txt.get_width()//2, 312))

            elif self.modo == "MASCOTA":
                self.dibujar_bbot(t, "NORMAL" if self.deseo_mascota else "FELIZ")
                f = pygame.font.SysFont("Arial", 24, bold=True)
                txt = f.render(f"PABLO, EL BOT DICE: {self.deseo_mascota}", True, (255, 255, 255))
                self.screen.blit(txt, (400 - txt.get_width()//2, 250))
                # Guía de botones
                guia = pygame.font.SysFont("Arial", 16).render("1:COMER | 2:BAÑO | 3:DORMIR | 4:SALIR", True, COLOR_NEON)
                self.screen.blit(guia, (240, 350))

            elif self.modo in ["CHISTES", "CUENTOS"]:
                self.dibujar_bbot(t)
                f = pygame.font.SysFont("Arial", 20, bold=True)
                # Mostrar texto
                palabras = self.texto_pantalla.split()
                linea, y_txt = "", 260
                for p in palabras:
                    if len(linea + p) < 45: linea += p + " "
                    else:
                        ts = f.render(linea, True, (255,255,255))
                        self.screen.blit(ts, (400 - ts.get_width()//2, y_txt))
                        y_txt += 30; linea = p + " "
                ts = f.render(linea, True, (255,255,255))
                self.screen.blit(ts, (400 - ts.get_width()//2, y_txt))

            # --- LÓGICA DE ENTRADAS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                input_act = None
                if event.type == pygame.JOYBUTTONDOWN: input_act = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION: input_act = {"tipo": "hat", "val": list(event.value)}

                if input_act:
                    # SALIR SIEMPRE CON BOTÓN 4
                    if input_act == self.controles.get("BOTON 4") and self.modo != "MENU":
                        self.modo = "MENU"
                        continue

                    if self.modo == "MENU":
                        if input_act == self.controles.get("DERECHA"): self.seleccion = (self.seleccion + 1) % 4
                        elif input_act == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion - 1) % 4
                        elif input_act == self.controles.get("BOTON 1"):
                            self.modo = self.opciones_menu[self.seleccion]
                            if self.modo == "MASCOTA": self.deseo_mascota = random.choice(["TENGO HAMBRE", "QUIERO BAÑO", "TENGO SUEÑO"])
                            elif self.modo == "CHISTES": self.texto_pantalla = obtener_chiste()
                            elif self.modo == "CUENTOS": 
                                self.historia_actual = self.obtener_nuevo_cuento()
                                self.indice_cuento = 0
                                self.texto_pantalla = self.historia_actual[0]

                    elif self.modo == "MASCOTA":
                        # Verificar si Pablo presionó lo que el bot pedía
                        if input_act == self.controles.get("BOTON 1") and "HAMBRE" in self.deseo_mascota:
                            self.deseo_mascota = "¡GRACIAS! QUÉ RICO"
                        elif input_act == self.controles.get("BOTON 2") and "BAÑO" in self.deseo_mascota:
                            self.deseo_mascota = "¡QUÉ LIMPIO ESTOY!"
                        elif input_act == self.controles.get("BOTON 3") and "SUEÑO" in self.deseo_mascota:
                            self.deseo_mascota = "ZZZ... HASTA MAÑANA"
                        # Después de 2 segundos, pedir otra cosa
                        
                    elif self.modo == "CHISTES":
                        if input_act in [self.controles.get("BOTON 1"), self.controles.get("BOTON 2")]:
                            self.texto_pantalla = obtener_chiste()

                    elif self.modo == "CUENTOS":
                        if input_act == self.controles.get("BOTON 1"): # Siguiente parte
                            self.indice_cuento = (self.indice_cuento + 1) % len(self.historia_actual)
                            self.texto_pantalla = self.historia_actual[self.indice_cuento]

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotGamer(); app.run()
