import pygame
import json
import os
import random
from utils import obtener_dato_curioso, obtener_chiste

# --- PALETA DE COLORES AMIGABLE ---
COLOR_CUERPO = (255, 255, 255)       # Blanco puro
COLOR_PANTALLA = (20, 20, 25)        # Negro azulado profundo
COLOR_VIVO = (0, 255, 200)           # Verde/Cyan neón (Energía)
COLOR_LOCO = (255, 50, 150)          # Rosa brillante
COLOR_FONDO = (60, 60, 90)           # Azul noche suave

CONFIG_FILE = "config.json"

class BBotApp:
    def __init__(self):
        pygame.init()
        # Pantalla completa 800x400
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("B-Bot de Pablo Ali")
        self.clock = pygame.time.Clock()
        
        # Cargar o crear datos
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.datos = json.load(f)
        else:
            self.datos = {"nombre": "Pablo Ali", "nivel": 1, "xp": 0}

        # Inicializar Joysticks (SNES30 / USB)
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks: j.init()

        self.mood = "feliz"
        self.texto = f"¡Hola Pablo Ali! ¿Jugamos hoy?"
        self.running = True

    def dibujar_escena(self):
        self.screen.fill(COLOR_FONDO)
        
        # 1. CUERPO DEL B-BOT (Más redondeado y tierno)
        # Sombra suave abajo
        pygame.draw.ellipse(self.screen, (40, 40, 70), (280, 310, 240, 40))
        # Chasis (Cuerpo tipo cápsula)
        pygame.draw.rect(self.screen, COLOR_CUERPO, (290, 30, 220, 280), border_radius=70)
        
        # 2. PANTALLA DE LA CARA
        pygame.draw.rect(self.screen, COLOR_PANTALLA, (315, 75, 170, 100), border_radius=20)

        # 3. OJOS MÁGICOS (Con pupilas para que se vea más vivo)
        tiempo = pygame.time.get_ticks()
        pestañeo = tiempo % 4000 < 150
        
        if not pestañeo:
            color = COLOR_VIVO if self.mood == "feliz" else COLOR_LOCO
            # Ojo Izquierdo
            pygame.draw.circle(self.screen, color, (355, 125), 18) # Brillo exterior
            pygame.draw.circle(self.screen, (255, 255, 255), (355, 125), 8) # Pupila blanca
            # Ojo Derecho
            pygame.draw.circle(self.screen, color, (445, 125), 18)
            pygame.draw.circle(self.screen, (255, 255, 255), (445, 125), 8)

        # 4. BOCA DIVERTIDA
        if self.mood == "feliz":
            # Una sonrisa curva (usando un arco o rect redondeado)
            pygame.draw.rect(self.screen, COLOR_VIVO, (370, 220, 60, 10), border_radius=5)
        elif self.mood == "loco":
            # Boca de sorpresa 'O'
            pygame.draw.circle(self.screen, COLOR_LOCO, (400, 230), 15, 3)

        # 5. BURBUJA DE DIÁLOGO (Estilo Comic)
        pygame.draw.rect(self.screen, (255, 255, 255), (60, 320, 680, 65), border_radius=20)
        # Triangulito de la burbuja
        pygame.draw.polygon(self.screen, (255, 255, 255), [(380, 320), (400, 320), (390, 305)])

        # Texto del B-Bot
        font = pygame.font.SysFont("Comic Sans MS", 18, bold=True)
        txt_limpio = self.texto[:85] + "..." if len(self.texto) > 85 else self.texto
        txt_surf = font.render(txt_limpio, True, (50, 50, 80))
        self.screen.blit(txt_surf, (90, 340))

        # BARRA DE NIVEL (Bonita en la esquina)
        pygame.draw.rect(self.screen, (30, 30, 50), (20, 20, 200, 25), border_radius=10)
        # Progreso de la barra
        ancho_xp = (self.datos["xp"] / 50) * 190
        pygame.draw.rect(self.screen, COLOR_VIVO, (25, 25, ancho_xp, 15), border_radius=8)
        
        lvl_font = pygame.font.SysFont("Arial", 14, bold=True)
        lvl_txt = lvl_font.render(f"PABLO ALI - NIVEL {self.datos['nivel']}", True, (255, 255, 255))
        self.screen.blit(lvl_txt, (30, 48))

    def run(self):
        while self.running:
            self.dibujar_escena()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # Botón A: ¡Dato!
                        self.mood = "feliz"
                        self.texto = obtener_dato_curioso(self.datos)
                        self.datos["xp"] += 10
                        if self.datos["xp"] >= 50:
                            self.datos["nivel"] += 1
                            self.datos["xp"] = 0
                            self.texto = "¡WOW! ¡SUBIMOS DE NIVEL!"
                        with open(CONFIG_FILE, 'w') as f: json.dump(self.datos, f)
                        
                    if event.button == 1: # Botón B: ¡Chiste!
                        self.mood = "loco"
                        self.texto = obtener_chiste()
            
            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotApp()
    app.run()
    pygame.quit()
