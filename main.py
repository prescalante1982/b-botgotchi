import pygame
import json
import os
import time
import math
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "controles_pablo.json"

class BBotConfigurable:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        # Mapeo de controles (se llenará en el inicio)
        self.mapa = {} 
        self.paso_config = 0
        self.teclas_a_pedir = ["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA", "BOTON 1", "BOTON 2", "BOTON 3", "BOTON 4"]
        
        self.modo = "CONFIG" if not os.path.exists(CONFIG_FILE) else "MENU"
        if self.modo == "MENU":
            with open(CONFIG_FILE, 'r') as f: self.mapa = json.load(f)

        self.seleccion = 0
        self.opciones = ["JUGAR", "COMER", "CHISTE", "CUENTO"]
        self.texto = ""
        self.running = True
        
        # Joystick
        self.joy = None
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

    def dibujar_config(self):
        self.screen.fill((20, 20, 40))
        font = pygame.font.SysFont("Arial", 30, bold=True)
        
        # Instrucción para Pablo Alí
        msg = f"HOLA PABLO! PRESIONA: {self.teclas_a_pedir[self.paso_config]}"
        txt_surf = font.render(msg, True, COLOR_NEON)
        self.screen.blit(txt_surf, (400 - txt_surf.get_width()//2, 180))
        
        # Dibujar progreso
        pygame.draw.rect(self.screen, (100, 100, 100), (200, 250, 400, 20), border_radius=10)
        progreso = (self.paso_config / len(self.teclas_a_pedir)) * 400
        pygame.draw.rect(self.screen, COLOR_NEON, (200, 250, progreso, 20), border_radius=10)

    def capturar_input(self, event):
        # Capturamos tanto botones como flechas (Hats)
        val = None
        if event.type == pygame.JOYBUTTONDOWN:
            val = ("btn", event.button)
        elif event.type == pygame.JOYHATMOTION:
            if event.value != (0, 0):
                val = ("hat", event.value)
        
        if val:
            tecla_actual = self.teclas_a_pedir[self.paso_config]
            self.mapa[tecla_actual] = val
            self.paso_config += 1
            time.sleep(0.3) # Evitar rebote
            
            if self.paso_config >= len(self.teclas_a_pedir):
                with open(CONFIG_FILE, 'w') as f: json.dump(self.mapa, f)
                self.modo = "MENU"
                self.texto = "¡LISTO PABLO! YA TE CONOZCO"

    def dibujar_menu(self):
        self.screen.fill(COLOR_FONDO)
        t = pygame.time.get_ticks()
        
        # Dibujar B-Bot flotando
        flotar = math.sin(t * 0.005) * 15
        pygame.draw.rect(self.screen, (255, 255, 255), (340, 120 + flotar, 120, 140), border_radius=40)
        pygame.draw.circle(self.screen, COLOR_NEON, (380, 170 + flotar), 10)
        pygame.draw.circle(self.screen, COLOR_NEON, (420, 170 + flotar), 10)

        # Iconos
        for i, opt in enumerate(self.opciones):
            color = COLOR_NEON if self.seleccion == i else (100, 100, 150)
            pygame.draw.rect(self.screen, color, (50 + i*180, 300, 160, 50), border_radius=15)
            font = pygame.font.SysFont("Arial", 20, bold=True)
            self.screen.blit(font.render(opt, True, (255,255,255)), (80 + i*180, 312))

    def run(self):
        while self.running:
            if self.modo == "CONFIG":
                self.dibujar_config()
            else:
                self.dibujar_menu()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if self.modo == "CONFIG":
                    self.capturar_input(event)
                else:
                    # Lógica de navegación usando el MAPA guardado
                    if event.type == pygame.JOYHATMOTION or event.type == pygame.JOYBUTTONDOWN:
                        # Revisar si lo presionado coincide con el mapa
                        btn_presionado = None
                        if event.type == pygame.JOYBUTTONDOWN: btn_presionado = ["btn", event.button]
                        if event.type == pygame.JOYHATMOTION: btn_presionado = ["hat", list(event.value)]
                        
                        if btn_presionado:
                            if btn_presionado == self.mapa.get("DERECHA"):
                                self.seleccion = (self.seleccion + 1) % 4
                            elif btn_presionado == self.mapa.get("IZQUIERDA"):
                                self.seleccion = (self.seleccion - 1) % 4
                            elif btn_presionado == self.mapa.get("BOTON 1"):
                                self.texto = f"ELEGISTE {self.opciones[self.seleccion]}"

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConfigurable()
    app.run()
