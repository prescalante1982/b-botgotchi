import pygame
import json
import os
import random
from utils import obtener_dato_curioso, obtener_chiste

# --- CONFIGURACIÓN VISUAL ---
COLOR_CUERPO = (245, 245, 245)
COLOR_PANTALLA = (25, 25, 30)
COLOR_LED = (0, 255, 255)
COLOR_LED_GLOW = (180, 255, 255)
COLOR_FONDO = (35, 35, 45)

CONFIG_FILE = "config.json"
# Datos actualizados para Pablo Alí
DATA_INICIAL = {
    "nombre": "Pablo Ali",
    "edad": 7,
    "gustos": ["espacio", "robots", "dinosaurios", "minecraft"],
    "nivel": 1,
    "xp": 0
}

class BBotApp:
    def __init__(self):
        pygame.init()
        # Pantalla completa para 800x400
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("B-Botgotchi OS")
        self.clock = pygame.time.Clock()
        
        # Cargar o Inicializar datos de Pablo Alí
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: 
                self.datos = json.load(f)
                # Forzamos actualización de nombre si era el anterior
                if self.datos["nombre"] != "Pablo Ali":
                    self.datos["nombre"] = "Pablo Ali"
        else:
            self.datos = DATA_INICIAL

        # Joysticks (8BitDo SNES30 + USB)
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks: j.init()

        self.mood = "feliz"
        self.texto = f"¡Hola {self.datos['nombre']}! Soy tu B-Bot."
        self.running = True

    def dibujar_bbot(self):
        self.screen.fill(COLOR_FONDO)
        
        # Cuerpo Cilíndrico
        pygame.draw.rect(self.screen, (210, 210, 215), (285, 30, 230, 270), border_radius=55)
        pygame.draw.rect(self.screen, COLOR_CUERPO, (290, 25, 220, 260), border_radius=55)
        
        # Pantalla Digital
        pygame.draw.rect(self.screen, COLOR_PANTALLA, (315, 65, 170, 100), border_radius=15)

        # Animación de Ojos
        tiempo = pygame.time.get_ticks()
        pestañeo = tiempo % 4500 < 150
        
        if not pestañeo:
            color = COLOR_LED if self.mood != "loco" else (255, 80, 255)
            pygame.draw.rect(self.screen, COLOR_LED_GLOW, (345, 95, 25, 25)) 
            pygame.draw.rect(self.screen, color, (345, 95, 25, 25), 3)
            pygame.draw.rect(self.screen, COLOR_LED_GLOW, (430, 95, 25, 25))
            pygame.draw.rect(self.screen, color, (430, 95, 25, 25), 3)

        # Boca
        if self.mood == "feliz":
            pygame.draw.rect(self.screen, COLOR_LED, (370, 210, 60, 6), border_radius=3)
        elif self.mood == "loco":
            pygame.draw.rect(self.screen, (255, 80, 255), (375, 200, 50, 25), 2)

        # Burbuja de Texto
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 310, 700, 70), border_radius=15)
        font = pygame.font.SysFont("monospace", 16, bold=True)
        txt_display = self.texto[:85] + "..." if len(self.texto) > 85 else self.texto
        txt_surf = font.render(txt_display, True, (40, 40, 45))
        self.screen.blit(txt_surf, (75, 335))

        # UI de Nivel
        lvl_font = pygame.font.SysFont("monospace", 14, bold=True)
        lvl_txt = lvl_font.render(f"PABLO ALI - LVL {self.datos['nivel']} | XP {self.datos['xp']}/50", True, (200, 255, 200))
        self.screen.blit(lvl_txt, (20, 20))

    def guardar_progreso(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.datos, f)

    def run(self):
        while self.running:
            self.dibujar_bbot()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # Botón A
                        self.texto = obtener_dato_curioso(self.datos)
                        self.mood = "feliz"
                        self.datos["xp"] += 10
                        if self.datos["xp"] >= 50:
                            self.datos["nivel"] += 1
                            self.datos["xp"] = 0
                        self.guardar_progreso()
                    if event.button == 1: # Botón B
                        self.texto = obtener_chiste()
                        self.mood = "loco"
                    if event.button == 7: # Start para salir
                        self.running = False

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotApp()
    app.run()
    pygame.quit()
