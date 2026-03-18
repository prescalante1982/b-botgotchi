import pygame
import time
import math
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- PALETA DE COLORES MODERNOS ---
COLOR_FONDO = (30, 30, 60)
COLOR_BOT_CUERPO = (255, 255, 255)
COLOR_BOT_PANTALLA = (20, 20, 25)
COLOR_NEON = (0, 255, 200)
COLOR_TEXTO = (255, 255, 255)
COLOR_RESALTADO = (255, 200, 0) # Dorado para la selección

class BBotModerno:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        # Pantalla completa para la Raspberry
        try:
            self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        except:
            self.screen = pygame.display.set_mode((800, 400))
            
        self.clock = pygame.time.Clock()
        
        # Opciones del Menú
        self.opciones = ["JUGAR", "COMER", "CHISTE", "CUENTO"]
        self.seleccion = 0
        self.modo = "LIBRE" # LIBRE, JUGANDO
        
        self.texto = "¡HOLA PABLO ALI! USA LAS FLECHAS"
        self.running = True
        
        # Inicializar Mandos
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

    def dibujar_interfaz(self):
        self.screen.fill(COLOR_FONDO)
        t = pygame.time.get_ticks()
        
        # 1. DIBUJAR AL B-BOT (CENTRO) - Siempre moviéndose
        self.dibujar_bbot_animado(t)
        
        # 2. DIBUJAR MENÚ DE ICONOS (Debajo del Bot)
        for i, nombre in enumerate(self.opciones):
            x = 100 + i * 200
            y = 280
            es_seleccionado = (self.seleccion == i)
            
            # Efecto de elevación si está seleccionado
            offset_sel = math.sin(t * 0.01) * 5 if es_seleccionado else 0
            color_caja = COLOR_RESALTADO if es_seleccionado else (100, 100, 150)
            
            # Dibujar Caja de Opción
            pygame.draw.rect(self.screen, color_caja, (x-70, y+offset_sel, 140, 40), border_radius=10)
            if es_seleccionado:
                pygame.draw.rect(self.screen, COLOR_TEXTO, (x-74, y+offset_sel-4, 148, 48), 3, border_radius=12)
            
            # Texto
            font = pygame.font.SysFont("Arial", 18, bold=True)
            txt_color = (30, 30, 60) if es_seleccionado else COLOR_TEXTO
            txt_surf = font.render(nombre, True, txt_color)
            self.screen.blit(txt_surf, (x - txt_surf.get_width()//2, y + 10 + offset_sel))

        # 3. BURBUJA DE TEXTO (ARRIBA)
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 20, 700, 60), border_radius=15)
        font_msg = pygame.font.SysFont("Arial", 22, bold=True)
        msg_surf = font_msg.render(self.texto.upper(), True, (50, 50, 80))
        self.screen.blit(msg_surf, (400 - msg_surf.get_width()//2, 35))

    def dibujar_bbot_animado(self, t):
        # Animación: Flotar y parpadear
        flotar = math.sin(t * 0.004) * 15
        cx, cy = 400, 180 + flotar
        
        # Sombra en el suelo
        sombra_ancho = 100 + math.sin(t * 0.004) * 20
        pygame.draw.ellipse(self.screen, (20, 20, 40), (400 - sombra_ancho//2, 350, sombra_ancho, 20))

        # Cuerpo
        pygame.draw.rect(self.screen, COLOR_BOT_CUERPO, (cx-60, cy-70, 120, 140), border_radius=40)
        # Pantalla cara
        pygame.draw.rect(self.screen, COLOR_BOT_PANTALLA, (cx-45, cy-45, 90, 60), border_radius=10)
        
        # Ojos Neón (cambian de expresión según selección)
        color_ojos = COLOR_NEON
        if self.seleccion == 1: color_ojos = (255, 100, 100) # Rojo si es comida
        
        if (t % 5000 > 200): # Parpadeo
            pygame.draw.circle(self.screen, color_ojos, (cx-20, cy-15), 12)
            pygame.draw.circle(self.screen, color_ojos, (cx+20, cy-15), 12)

    def run(self):
        while self.running:
            self.dibujar_interfaz()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
                
                # NAVEGACIÓN CON FLECHAS (HAT)
                if event.type == pygame.JOYHATMOTION:
                    hx, hy = event.value
                    if hx == 1: # Derecha
                        self.seleccion = (self.seleccion + 1) % len(self.opciones)
                    if hx == -1: # Izquierda
                        self.seleccion = (self.seleccion - 1) % len(self.opciones)

                # SELECCIÓN CON BOTÓN (A / Botón 0)
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:
                        if self.seleccion == 0: # JUGAR
                            self.texto = "¡PREPARANDO EL LABERINTO!"
                            # Aquí puedes llamar a self.iniciar_juego()
                        elif self.seleccion == 1: # COMER
                            self.texto = "¡YUM! ME SIENTO GENIAL"
                        elif self.seleccion == 2: # CHISTE
                            self.texto = obtener_chiste()
                        elif self.seleccion == 3: # CUENTO
                            self.texto = "HABIA UNA VEZ UN ROBOT EN GUATEMALA..."

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotModerno()
    app.run()
