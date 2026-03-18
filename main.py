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
COLOR_RISA = (255, 255, 0) # Amarillo para la risa
CONFIG_FILE = "config_controles.json"

class BBotConEmociones:
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
        
        self.modo = "MENU"
        self.seleccion = 0
        self.opciones_menu = ["JUGAR", "MASCOTA", "CHISTES", "CUENTOS"]
        
        # Estados de Ánimo
        self.estado_bot = "NORMAL" # NORMAL, RISA, LEYENDO
        self.timer_reaccion = 0
        
        # Contenido
        self.biblioteca_cuentos = [
            ["Había una vez un robot en Guatemala...", "¡Encontró un joystick de oro puro!", "Al tocarlo, ¡aprendió a jugar fútbol!", "Ahora es el campeón de la liga robótica."],
            ["B-Bot quería conocer el volcán de Agua.", "Cargó sus baterías con energía solar.", "En la cima, vio las nubes desde arriba.", "Fue el día más feliz de su vida."]
        ]
        self.texto_pantalla = ""
        self.historia_actual = []
        self.indice_cuento = 0

        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

    def dibujar_bbot_emotivo(self, t):
        # Velocidad de baile según el estado
        velocidad = 0.01 if self.estado_bot == "RISA" else 0.005
        amplitud = 25 if self.estado_bot == "RISA" else 15
        
        flotar = math.sin(t * velocidad) * amplitud
        cx, cy = 400, 140 + flotar
        
        # Cuerpo
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 130), border_radius=30)
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        
        # Dibujar Ojos según emoción
        if self.estado_bot == "RISA":
            # Ojos felices ^ ^
            pygame.draw.lines(self.screen, COLOR_RISA, False, [(cx-35, cy-10), (cx-20, cy-25), (cx-5, cy-10)], 4)
            pygame.draw.lines(self.screen, COLOR_RISA, False, [(cx+5, cy-10), (cx+20, cy-25), (cx+35, cy-10)], 4)
        elif self.estado_bot == "LEYENDO":
            # Ojos de atención - -
            pygame.draw.line(self.screen, COLOR_NEON, (cx-35, cy-15), (cx-5, cy-15), 5)
            pygame.draw.line(self.screen, COLOR_NEON, (cx+5, cy-15), (cx+35, cy-15), 5)
        else:
            # Ojos normales O O
            pygame.draw.circle(self.screen, COLOR_NEON, (cx-20, cy-15), 10)
            pygame.draw.circle(self.screen, COLOR_NEON, (cx+20, cy-15), 10)

    def cambiar_emocion(self, nueva_emocion, duracion=1.5):
        self.estado_bot = nueva_emocion
        self.timer_reaccion = time.time() + duracion

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            ahora = time.time()
            
            # Resetear a NORMAL cuando pase el tiempo
            if ahora > self.timer_reaccion:
                self.estado_bot = "NORMAL"

            self.screen.fill(COLOR_FONDO)

            if self.modo == "MENU":
                self.dibujar_bbot_emotivo(t)
                for i, opt in enumerate(self.opciones_menu):
                    es_sel = (self.seleccion == i)
                    col = (255, 200, 0) if es_sel else (100, 100, 150)
                    pygame.draw.rect(self.screen, col, (80 + i*170, 300, 150, 50), border_radius=15)
                    txt = pygame.font.SysFont("Arial", 18, bold=True).render(opt, True, (30,30,60) if es_sel else (255,255,255))
                    self.screen.blit(txt, (155+i*170 - txt.get_width()//2, 312))

            elif self.modo in ["CHISTES", "CUENTOS"]:
                self.dibujar_bbot_emotivo(t)
                # (Aquí iría la lógica de renderizar texto centrado que ya tenemos)
                f = pygame.font.SysFont("Arial", 20, bold=True)
                ts = f.render(self.texto_pantalla[:50], True, (255,255,255)) # Simplificado para el ejemplo
                self.screen.blit(ts, (400 - ts.get_width()//2, 260))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                input_act = None
                if event.type == pygame.JOYBUTTONDOWN: input_act = {"tipo": "btn", "val": event.button}
                elif event.type == pygame.JOYHATMOTION: input_act = {"tipo": "hat", "val": list(event.value)}

                if input_act:
                    if input_act == self.controles.get("BOTON 4"):
                        self.modo = "MENU"
                        continue

                    if self.modo == "MENU":
                        if input_act == self.controles.get("DERECHA"): self.seleccion = (self.seleccion + 1) % 4
                        elif input_act == self.controles.get("IZQUIERDA"): self.seleccion = (self.seleccion - -1) % 4
                        elif input_act == self.controles.get("BOTON 1"):
                            self.modo = self.opciones_menu[self.seleccion]
                            if self.modo == "CHISTES":
                                self.texto_pantalla = obtener_chiste()
                                self.cambiar_emocion("RISA", 2.0) # ¡Se ríe al contar el chiste!
                            elif self.modo == "CUENTOS":
                                self.historia_actual = random.choice(self.biblioteca_cuentos)
                                self.indice_cuento = 0
                                self.texto_pantalla = self.historia_actual[0]
                                self.cambiar_emocion("LEYENDO", 1.5)

                    elif self.modo == "CHISTES":
                        if input_act == self.controles.get("BOTON 1"):
                            self.texto_pantalla = obtener_chiste()
                            self.cambiar_emocion("RISA", 2.0)

                    elif self.modo == "CUENTOS":
                        if input_act == self.controles.get("BOTON 1"):
                            self.indice_cuento = (self.indice_cuento + 1) % len(self.historia_actual)
                            self.texto_pantalla = self.historia_actual[self.indice_cuento]
                            self.cambiar_emocion("LEYENDO", 1.0)

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConEmociones(); app.run()
