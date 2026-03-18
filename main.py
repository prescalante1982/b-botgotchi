import pygame
import json
import os
import time
import math
from utils import obtener_chiste, obtener_cuento_dinamico, generar_laberinto

# Colores y Config
COLOR_FONDO = (20, 20, 40)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_pablo.json"

class BBotConsola:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 400))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Cargar Controles
        self.controles = {}
        self.pasos_config = ["IZQUIERDA", "DERECHA", "ARRIBA", "ABAJO", "BOTON 1", "BOTON 4"]
        self.indice_cfg = 0
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.controles = json.load(f)
            self.modo = "MENU"
        else:
            self.modo = "CONFIG"

        self.opciones = ["JUGAR", "CHISTES", "CUENTOS"]
        self.seleccion = 0
        self.texto_pantalla = "¡HOLA PABLO ALÍ!"
        self.estado_bot = "NORMAL"
        self.timer_emo = 0
        
        # Joystick
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0); self.joy.init()

    def mostrar_mensaje_carga(self):
        self.screen.fill(COLOR_FONDO)
        txt = pygame.font.SysFont("Arial", 30).render("CONECTANDO CON LA NUBE...", True, COLOR_NEON)
        self.screen.blit(txt, (400 - txt.get_width()//2, 180))
        pygame.display.flip()

    def run(self):
        while self.running:
            t = pygame.time.get_ticks()
            self.screen.fill(COLOR_FONDO)
            
            # --- DIBUJAR SEGÚN MODO ---
            if self.modo == "CONFIG":
                txt = f"PABLO, PRESIONA: {self.pasos_config[self.indice_cfg]}"
                s = pygame.font.SysFont("Arial", 30).render(txt, True, (255,255,255))
                self.screen.blit(s, (400 - s.get_width()//2, 180))
            
            elif self.modo == "MENU":
                # Dibujar Opciones
                for i, opt in enumerate(self.opciones):
                    sel = (self.seleccion == i)
                    color = COLOR_NEON if sel else (60, 60, 90)
                    pygame.draw.rect(self.screen, color, (100 + i*220, 300, 180, 60), border_radius=15)
                    txt = pygame.font.SysFont("Arial", 22, True).render(opt, True, (0,0,0) if sel else (200,200,200))
                    self.screen.blit(txt, (190 + i*220 - txt.get_width()//2, 315))

            # --- GESTIÓN DE EVENTOS ---
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
                        if self.indice_cfg >= len(self.pasos_config):
                            with open(CONFIG_FILE, 'w') as f: json.dump(self.controles, f)
                            self.modo = "MENU"
                        pygame.time.wait(200)
                    
                    else:
                        # Volver al menú (BOTON 4)
                        if entrada == self.controles.get("BOTON 4"):
                            self.modo = "MENU"
                        
                        elif self.modo == "MENU":
                            if entrada == self.controles.get("DERECHA"):
                                self.seleccion = (self.seleccion + 1) % len(self.opciones)
                            elif entrada == self.controles.get("IZQUIERDA"):
                                self.seleccion = (self.seleccion - 1) % len(self.opciones)
                            elif entrada == self.controles.get("BOTON 1"):
                                self.mostrar_mensaje_carga() # Feedback inmediato
                                nueva_opcion = self.opciones[self.seleccion]
                                if nueva_opcion == "CHISTES":
                                    self.texto_pantalla = obtener_chiste()
                                elif nueva_opcion == "CUENTOS":
                                    self.historia = obtener_cuento_dinamico()
                                    self.texto_pantalla = self.historia[0]
                                self.modo = nueva_opcion

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    BBotConsola().run()
