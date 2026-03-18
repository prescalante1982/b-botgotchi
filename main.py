import pygame
import json
import os
from utils import obtener_dato_curioso, generar_laberinto

class BBotApp:
    def __init__(self):
        pygame.init()
        # Resolución estándar para pantallas de Raspberry Pi
        self.screen = pygame.display.set_mode((800, 480))
        self.clock = pygame.time.Clock()
        
        # Datos personalizados de Mateo
        self.datos = {"nombre": "Mateo", "edad": 7, "gustos": ["espacio", "dinosaurios"], "nivel": 1, "xp": 0}
        
        # Soporte para 8BitDo SNES30 y Joystick USB
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks: j.init()

        self.estado = "MENU"
        self.mood = "feliz"
        self.texto = f"¡Hola {self.datos['nombre']}! Presiona A para jugar."
        self.running = True

    def dibujar_rostro(self):
        self.screen.fill((20, 20, 20))
        color = (0, 255, 255) # Cyan Pixel Art
        # Dibujo básico de ojos cuadrados (Pixel Art)
        pygame.draw.rect(self.screen, color, (300, 150, 40, 40))
        pygame.draw.rect(self.screen, color, (460, 150, 40, 40))
        pygame.draw.rect(self.screen, color, (350, 280, 100, 10))

    def run(self):
        while self.running:
            self.dibujar_rostro()
            # Render de texto
            font = pygame.font.SysFont("monospace", 16)
            img = font.render(self.texto, True, (255, 255, 255))
            self.screen.blit(img, (50, 420))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # Botón A: Acción/Dato
                        self.texto = obtener_dato_curioso(self.datos)
                        self.mood = "feliz"
            
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotApp()
    app.run()
