import pygame
import json
import os
import time
import math
import random
from utils import obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_controles.json"

class BBotConsolaFinal:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Cargar Controles de Pablo Alí
        self.controles = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
        
        self.opciones_menu = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        self.modo = "MENU"
        self.seleccion = 0
        
        # Datos de Cuentos
        self.biblioteca_cuentos = [
            ["Había una vez un robot en Guatemala...", "Encontró un joystick de oro puro.", "Al tocarlo, ¡aprendió a jugar fútbol!", "Ahora es el campeón de la liga robótica."],
            ["B-Bot quería conocer el volcán de Agua.", "Cargó sus baterías con energía solar.", "En la cima, vio las nubes desde arriba.", "Fue el día más feliz de su vida electrónica."],
            ["Pablo Alí y B-Bot hicieron un equipo.", "Programaron un código secreto de colores.", "El código abrió un portal a la Luna.", "Allí jugaron escondite con los astronautas."]
        ]
        
        self.texto_pantalla = ""
        self.historia_actual = []
        self.indice_cuento = 0

        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

    def dibujar_bbot(self, t):
        flotar = math.sin(t * 0.005) * 15
        cx, cy = 400, 140 + flotar
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 130), border_radius=30)
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx-20, cy-15), 10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx+20, cy-15), 10)

    def mostrar_texto_centrado(self, texto):
        f = pygame.font.SysFont("Arial", 22, bold=True)
        palabras = texto.split()
        linea, y_txt = "", 260
        for p in palabras:
            if len(linea + p) < 40: linea += p + " "
            else:
                ts = f.render(linea, True, (255, 255, 255))
                self.screen.blit(ts, (400 - ts.get_width()//2, y_txt))
                y_txt += 30; linea = p + " "
        ts = f.render(linea, True, (255, 255, 255))
        self.screen.blit(ts, (400 - ts.get_width()//2, y_txt))

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            self.screen.fill(COLOR_FONDO)

            if self.modo == "MENU":
                self.dibujar_bbot(t)
                for i, opt in enumerate(self.opciones_menu):
                    es_sel = (self.seleccion == i)
                    col = (255, 200, 0) if es_sel else (100, 100, 150)
                    pygame.draw.rect(self.screen, col, (80 + i*170, 300, 150, 50), border_radius=15)
                    txt = pygame.font.SysFont("Arial", 18, bold=True).render(opt, True, (30,30,60) if es_sel else (255,255,255))
                    self.screen.blit(txt, (155+i*170 - txt.get_width()//2, 312))

            elif self.modo in ["CHISTES", "CUENTOS"]:
                self.dibujar_bbot(t)
                self.mostrar_texto_centrado(self.texto_pantalla)
                guia = "BOTON 1: SIGUIENTE | BOTON 4: SALIR" if self.modo == "CUENTOS" else "BOTON 1: OTRO CHISTE | BOTON 4: SALIR"
                self.screen.blit(pygame.font.SysFont("Arial", 14).render(guia, True, COLOR_NEON), (280, 370))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                input_act = None
                if event.type == pygame.JOYBUTTONDOWN: input_act = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION: input_act = {"tipo": "hat", "val": list(event.value)}

                if input_act:
                    # SALIR CON BOTÓN 4
                    if input_act == self.controles.get("BOTON 4"):
                        self.modo = "MENU"
                        continue

                    if self.modo == "MENU":
                        if input_act == self.controles.get("DERECHA"): self.seleccion = (self.seleccion + 1) % 4
                        elif input_act == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion - 1) % 4
                        elif input_act == self.controles.get("BOTON 1"):
                            self.modo = self.opciones_menu[self.seleccion]
                            if self.modo == "CHISTES":
                                self.texto_pantalla = obtener_chiste()
                            elif self.modo == "CUENTOS":
                                # ELEGIR UN CUENTO NUEVO AL AZAR CADA VEZ QUE ENTRA
                                self.historia_actual = random.choice(self.biblioteca_cuentos)
                                self.indice_cuento = 0
                                self.texto_pantalla = self.historia_actual[0]

                    elif self.modo == "CHISTES":
                        if input_act == self.controles.get("BOTON 1"):
                            self.texto_pantalla = obtener_chiste()

                    elif self.modo == "CUENTOS":
                        if input_act == self.controles.get("BOTON 1"):
                            self.indice_cuento = (self.indice_cuento + 1) % len(self.historia_actual)
                            self.texto_pantalla = self.historia_actual[self.indice_cuento]

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConsolaFinal(); app.run()
