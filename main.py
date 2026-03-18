import pygame
import json
import os
import time
import math
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
COLOR_TEXTO = (255, 255, 255)
FILE_CONFIG = "config_pablo.json"

class BBotConfig:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        try:
            self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        except:
            self.screen = pygame.display.set_mode((800, 400))
            
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 1. CARGAR O INICIAR CONFIGURACIÓN
        self.controles = {}
        self.paso_config = 0
        self.botones_a_mapear = ["IZQUIERDA", "DERECHA", "SELECCIONAR"]
        
        if os.path.exists(FILE_CONFIG):
            with open(FILE_CONFIG, 'r') as f:
                self.controles = json.load(f)
            self.modo = "MENU"
        else:
            self.modo = "CONFIGURANDO"

        self.opciones = ["JUGAR", "COMER", "CHISTE", "CUENTO"]
        self.seleccion = 0
        self.texto = "¡HOLA PABLO ALI!"
        
        # Iniciar Mando
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()

    def dibujar_pantalla_config(self):
        self.screen.fill((20, 20, 40))
        font = pygame.font.SysFont("Arial", 35, bold=True)
        # Instrucción clara
        msg = f"PRESIONA TU BOTON O FLECHA: {self.botones_a_mapear[self.paso_config]}"
        txt = font.render(msg, True, COLOR_NEON)
        self.screen.blit(txt, (400 - txt.get_width()//2, 180))
        
        aviso = pygame.font.SysFont("Arial", 18).render("CONFIGURANDO MANDO PARA PABLO ALI...", True, (150, 150, 150))
        self.screen.blit(aviso, (250, 350))

    def dibujar_menu_pro(self):
        self.screen.fill(COLOR_FONDO)
        t = pygame.time.get_ticks()
        
        # B-Bot Animado
        flotar = math.sin(t * 0.005) * 15
        cx, cy = 400, 150 + flotar
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 140), border_radius=40)
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx-20, cy-15), 10)
        pygame.draw.circle(self.screen, COLOR_NEON, (cx+20, cy-15), 10)

        # Iconos de Menú
        for i, nombre in enumerate(self.opciones):
            es_sel = (self.seleccion == i)
            color = (255, 200, 0) if es_sel else (100, 100, 150)
            y_btn = 280 - (10 if es_sel else 0)
            pygame.draw.rect(self.screen, color, (80 + i*170, y_btn, 150, 50), border_radius=15)
            
            f = pygame.font.SysFont("Arial", 18, bold=True)
            txt = f.render(nombre, True, (30,30,60) if es_sel else (255,255,255))
            self.screen.blit(txt, (155 + i*170 - txt.get_width()//2, y_btn + 15))

    def capturar_boton(self, event):
        # Captura si es un botón o si es una flecha (Hat)
        val = None
        if event.type == pygame.JOYBUTTONDOWN:
            val = {"tipo": "btn", "id": event.button}
        elif event.type == pygame.JOYHATMOTION:
            if event.value != (0, 0):
                val = {"tipo": "hat", "id": event.value}
        
        if val:
            tecla_actual = self.botones_a_mapear[self.paso_config]
            self.controles[tecla_actual] = val
            self.paso_config += 1
            time.sleep(0.4) # Pausa para no capturar doble
            
            if self.paso_config >= len(self.botones_a_mapear):
                with open(FILE_CONFIG, 'w') as f:
                    json.dump(self.controles, f)
                self.modo = "MENU"

    def run(self):
        while self.running:
            if self.modo == "CONFIGURANDO":
                self.dibujar_pantalla_config()
            else:
                self.dibujar_menu_pro()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if self.modo == "CONFIGURANDO":
                    self.capturar_boton(event)
                else:
                    # LÓGICA DE JUEGO CON BOTONES MAPEADOS
                    if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYHATMOTION:
                        # Revisar qué se presionó
                        input_actual = None
                        if event.type == pygame.JOYBUTTONDOWN: input_actual = {"tipo": "btn", "id": event.button}
                        if event.type == pygame.JOYHATMOTION: input_actual = {"tipo": "hat", "id": list(event.value)}
                        
                        # Comparar con lo guardado
                        if input_actual == self.controles.get("DERECHA"):
                            self.seleccion = (self.seleccion + 1) % 4
                        elif input_actual == self.controles.get("IZQUIERDA"):
                            self.seleccion = (self.seleccion - 1) % 4
                        elif input_actual == self.controles.get("SELECCIONAR"):
                            # Acción según el botón
                            opc = self.opciones[self.seleccion]
                            if opc == "CHISTE": print(obtener_chiste())
                            # Agrega aquí las demás llamadas

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConfig()
    app.run()
