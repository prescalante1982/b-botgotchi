import pygame
import json
import os
import time
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- PALETA VINTAGE LCD ---
COLOR_LCD_FONDO = (155, 188, 15)   # Verde clásico GameBoy
COLOR_LCD_PIXEL = (15, 56, 15)     # Verde oscuro casi negro
COLOR_LCD_SHADOW = (139, 172, 15)

CONFIG_FILE = "config.json"

class BBot90s:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        # Stats estilo Tamagotchi
        self.stats = {"hambre": 100, "energia": 100, "diversion": 100, "vivo": True}
        self.datos = {"nombre": "Pablo Ali", "nivel": 1}
        
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

        self.mood = "neutral"
        self.texto = "¡HOLA PABLO ALI! PIPI-PU-PI!"
        self.last_tick = time.time()
        self.running = True

    def actualizar_logica(self):
        if not self.stats["vivo"]: return

        # El tiempo pasa... (Degradación rápida estilo 90s)
        ahora = time.time()
        if ahora - self.last_tick > 10: # Cada 10 segundos baja el hambre
            self.stats["hambre"] -= 10
            self.stats["energia"] -= 5
            self.stats["diversion"] -= 8
            self.last_tick = ahora

        # ¿Se murió? :(
        if self.stats["hambre"] <= 0 or self.stats["energia"] <= 0:
            self.stats["vivo"] = False
            self.texto = "OH NO... PRESIONA START PARA REINICIAR"

    def dibujar_interfaz_retro(self):
        self.screen.fill(COLOR_LCD_FONDO)
        
        # Dibujar Marco de la pantalla (Borde de plástico de juguete)
        pygame.draw.rect(self.screen, (50, 50, 50), (10, 10, 780, 380), 15, border_radius=30)

        if not self.stats["vivo"]:
            # Dibujar Fantasmita Píxel Art
            self.dibujar_fantasma()
        else:
            # 1. ICONOS DE ESTADO (Parpadean si están bajos)
            self.dibujar_iconos()
            # 2. EL B-BOT (Píxel Art puro)
            self.dibujar_bbot_pixel()

        # 3. TEXTO ESTILO LCD (Fuente Monospace)
        pygame.draw.rect(self.screen, COLOR_LCD_PIXEL, (50, 310, 700, 60), 2)
        font = pygame.font.SysFont("Courier New", 22, bold=True)
        txt = font.render(self.texto.upper(), True, COLOR_LCD_PIXEL)
        self.screen.blit(txt, (70, 330))

    def dibujar_iconos(self):
        # Hambre (Icono de comida) - Parpadea si < 30
        if self.stats["hambre"] > 30 or (time.time() * 2) % 2 > 1:
            pygame.draw.rect(self.screen, COLOR_LCD_PIXEL, (50, 30, 40, 30), 2) # "Hamburguesa"
        
        # Sueño (Icono Zzz)
        if self.stats["energia"] > 30 or (time.time() * 2) % 2 > 1:
            font = pygame.font.SysFont("Arial", 20, bold=True)
            self.screen.blit(font.render("Zz", True, COLOR_LCD_PIXEL), (120, 30))

    def dibujar_bbot_pixel(self):
        # Un diseño más cuadrado y "pixeleado"
        centro_x, centro_y = 400, 160
        # Cuerpo
        pygame.draw.rect(self.screen, COLOR_LCD_PIXEL, (centro_x-70, centro_y-80, 140, 180), 4, border_radius=10)
        # Visor
        pygame.draw.rect(self.screen, COLOR_LCD_PIXEL, (centro_x-50, centro_y-60, 100, 60), 2)
        
        # Ojos de píxel (Cuadrados)
        if (time.time() % 4 > 0.2): # Pestañeo
            pygame.draw.rect(self.screen, COLOR_LCD_PIXEL, (centro_x-35, centro_y-45, 20, 20))
            pygame.draw.rect(self.screen, COLOR_LCD_PIXEL, (centro_x+15, centro_y-45, 20, 20))

    def dibujar_fantasma(self):
        font = pygame.font.SysFont("Arial", 50, bold=True)
        self.screen.blit(font.render("X_X", True, COLOR_LCD_PIXEL), (350, 150))

    def run(self):
        while self.running:
            self.actualizar_logica()
            self.dibujar_interfaz_retro()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    # SI ESTÁ MUERTO: Resetear con cualquier botón largo
                    if not self.stats["vivo"]:
                        self.__init__()
                        continue

                    # BOTÓN A: Alimentar
                    if event.button == 0:
                        self.stats["hambre"] = min(100, self.stats["hambre"] + 25)
                        self.texto = "¡GLUP! DELICIOSO PABLO ALI"
                    
                    # BOTÓN B: Dormir
                    elif event.button == 1:
                        self.stats["energia"] = min(100, self.stats["energia"] + 40)
                        self.texto = "DURMIENDO... NO DESPIERTES"
                    
                    # BOTÓN X: Jugar (Laberinto)
                    elif event.button in [2, 3]:
                        self.texto = "¡VAMOS AL LABERINTO!"
                        # Aquí lanzas tu lógica de laberinto

            pygame.display.flip()
            self.clock.tick(20)

if __name__ == "__main__":
    app = BBot90s()
    app.run()
