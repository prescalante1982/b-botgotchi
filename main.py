import pygame
import json
import os
import time
import math
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- CONFIGURACIÓN VISUAL ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
CONFIG_FILE = "config_controles.json"

class BBotConfigurador:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        try:
            self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        except:
            self.screen = pygame.display.set_mode((800, 400))
            
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Lista de lo que necesitamos capturar
        self.controles = {}
        self.pasos = ["IZQUIERDA", "DERECHA", "BOTON 1", "BOTON 2", "BOTON 3", "BOTON 4"]
        self.indice_paso = 0
        
        # Si ya existe el archivo, saltamos al menú
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.controles = json.load(f)
            self.modo = "MENU"
        else:
            self.modo = "CONFIG"

        self.opciones = ["JUGAR", "COMER", "CHISTE", "CUENTO"]
        self.seleccion = 0
        self.texto = "¡HOLA PABLO ALI!"
        
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

    def dibujar_config(self):
        self.screen.fill((20, 20, 40))
        font = pygame.font.SysFont("Arial", 32, bold=True)
        
        # Instrucción dinámica
        txt = f"PABLO, PRESIONA TU: {self.pasos[self.indice_paso]}"
        surf = font.render(txt, True, COLOR_NEON)
        self.screen.blit(surf, (400 - surf.get_width()//2, 180))
        
        # Barra de progreso
        pygame.draw.rect(self.screen, (60, 60, 80), (200, 250, 400, 10))
        ancho = (self.indice_paso / len(self.pasos)) * 400
        pygame.draw.rect(self.screen, COLOR_NEON, (200, 250, ancho, 10))

    def capturar_input(self, event):
        id_detectado = None
        
        # Detectar si es un botón físico
        if event.type == pygame.JOYBUTTONDOWN:
            id_detectado = {"tipo": "btn", "val": event.button}
        
        # Detectar si son las flechas (Hats)
        elif event.type == pygame.JOYHATMOTION:
            if event.value != (0, 0):
                id_detectado = {"tipo": "hat", "val": event.value}

        if id_detectado:
            # Guardamos el ID que envió el mando para ese nombre
            nombre_tecla = self.pasos[self.indice_paso]
            self.controles[nombre_tecla] = id_detectado
            self.indice_paso += 1
            time.sleep(0.3) # Evitar que un clic cuente por dos
            
            if self.indice_paso >= len(self.pasos):
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(self.controles, f)
                self.modo = "MENU"

    def dibujar_menu(self):
        self.screen.fill(COLOR_FONDO)
        t = pygame.time.get_ticks()
        
        # B-Bot bailando
        flotar = math.sin(t * 0.005) * 15
        cx, cy = 400, 150 + flotar
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 140), border_radius=40)
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx-20, cy-15), 10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx+20, cy-15), 10)

        # Botones de opciones
        for i, opt in enumerate(self.opciones):
            es_sel = (self.seleccion == i)
            color = (255, 200, 0) if es_sel else (100, 100, 150)
            pygame.draw.rect(self.screen, color, (80 + i*170, 300, 150, 50), border_radius=15)
            f = pygame.font.SysFont("Arial", 18, bold=True)
            txt = f.render(opt, True, (30,30,60) if es_sel else (255,255,255))
            self.screen.blit(txt, (155+i*170 - txt.get_width()//2, 315))

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
                    # LÓGICA DE JUEGO USANDO EL MAPA GUARDADO
                    input_actual = None
                    if event.type == pygame.JOYBUTTONDOWN:
                        input_actual = {"tipo": "btn", "val": event.button}
                    elif event.type == pygame.JOYHATMOTION:
                        input_actual = {"tipo": "hat", "val": list(event.value)}

                    if input_actual:
                        # Navegar
                        if input_actual == self.controles.get("DERECHA"):
                            self.seleccion = (self.seleccion + 1) % 4
                        elif input_actual == self.controles.get("IZQUIERDA"):
                            self.seleccion = (self.seleccion - 1) % 4
                        
                        # Acciones (Botones 1 al 4)
                        elif input_actual == self.controles.get("BOTON 1"):
                            self.texto = "¡ELEGISTE JUGAR!"
                            # Lanzar laberinto aquí
                        elif input_actual == self.controles.get("BOTON 2"):
                            self.texto = "¡YUM! COMIDA RICA"
                        elif input_actual == self.controles.get("BOTON 3"):
                            self.texto = obtener_chiste()
                        elif input_actual == self.controles.get("BOTON 4"):
                            self.texto = "HABIA UNA VEZ UN ROBOT..."

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConfigurador()
    app.run()
