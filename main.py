import pygame
import time
import math
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES LCD VINTAGE ---
COLOR_FONDO = (155, 188, 15)  # Verde GameBoy
COLOR_PIXEL = (15, 56, 15)    # Verde oscuro

class BBot90s:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        # Estados: 0:Menu/Libre, 1:Laberinto, 2:Texto(Dato/Chiste)
        self.estado = 0
        self.seleccion = 0 # Icono seleccionado (0-3)
        self.iconos = ["JUGAR", "COMER", "CHISTE", "CUENTO"]
        
        self.texto = "¡HOLA PABLO ALI!"
        self.stats = {"hambre": 100, "energia": 100}
        self.running = True
        
        # Configuración de Joysticks
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

    def dibujar_interfaz(self):
        self.screen.fill(COLOR_FONDO)
        t = pygame.time.get_ticks()
        
        # 1. DIBUJAR ICONOS (ARRIBA)
        for i, nombre in enumerate(self.iconos):
            color = COLOR_PIXEL if self.seleccion == i else (139, 172, 15)
            pygame.draw.rect(self.screen, COLOR_PIXEL, (50 + i*190, 20, 160, 40), 2)
            if self.seleccion == i: # El icono seleccionado parpadea
                if (t // 500) % 2 == 0:
                    pygame.draw.rect(self.screen, COLOR_PIXEL, (55 + i*190, 25, 150, 30))
            
            font = pygame.font.SysFont("Courier New", 18, bold=True)
            txt_color = COLOR_FONDO if self.seleccion == i and (t // 500) % 2 == 0 else COLOR_PIXEL
            self.screen.blit(font.render(nombre, True, txt_color), (70 + i*190, 30))

        # 2. DIBUJAR AL B-BOT (SIEMPRE VISIBLE EN EL CENTRO)
        if self.estado != 1: # Si no está en el laberinto
            self.dibujar_bbot_animado(t)

        # 3. AREA DE TEXTO (ABAJO)
        pygame.draw.rect(self.screen, COLOR_PIXEL, (50, 320, 700, 60), 3)
        font_msg = pygame.font.SysFont("Courier New", 20, bold=True)
        self.screen.blit(font_msg.render(self.texto.upper()[:50], True, COLOR_PIXEL), (70, 340))

    def dibujar_bbot_animado(self, t):
        # Animación de respiración y balanceo
        bounce = math.sin(t * 0.005) * 10
        swing = math.sin(t * 0.002) * 5
        cx, cy = 400, 180
        
        # Cuerpo pixelado
        pygame.draw.rect(self.screen, COLOR_PIXEL, (cx-60 + swing, cy-60 + bounce, 120, 130), 4, border_radius=10)
        # Visor
        pygame.draw.rect(self.screen, COLOR_PIXEL, (cx-40 + swing, cy-40 + bounce, 80, 40), 2)
        # Ojos (parpadean)
        if (t % 4000 > 200):
            pygame.draw.rect(self.screen, COLOR_PIXEL, (cx-30+swing, cy-30+bounce, 15, 15))
            pygame.draw.rect(self.screen, COLOR_PIXEL, (cx+15+swing, cy-30+bounce, 15, 15))

    def run(self):
        while self.running:
            self.dibujar_interfaz()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    # Botón 1 (A) para Seleccionar lo que marque el icono
                    if event.button == 0:
                        if self.seleccion == 0: self.texto = "¡VAMOS AL LABERINTO!" # Aquí lanzarías el laberinto
                        if self.seleccion == 1: self.texto = "¡YUM! QUE RICO PABLO"
                        if self.seleccion == 2: self.texto = obtener_chiste()
                        if self.seleccion == 3: self.texto = "HABIA UNA VEZ UN ROBOT..."
                    
                    # Botón para volver al estado normal
                    if event.button in [6, 7]: self.estado = 0

                # MOVERSE ENTRE ICONOS CON LAS FLECHAS (D-PAD)
                if event.type == pygame.JOYHATMOTION:
                    hx, hy = event.value
                    if hx == 1: self.seleccion = (self.seleccion + 1) % 4
                    if hx == -1: self.seleccion = (self.seleccion - 1) % 4

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBot90s()
    app.run()
