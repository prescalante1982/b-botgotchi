import pygame
import json
import os
import random
from utils import obtener_dato_curioso, obtener_chiste

# --- CONFIGURACIÓN VISUAL ---
COLOR_CUERPO = (255, 255, 255)
COLOR_PANTALLA = (20, 20, 25)
COLOR_VIVO = (0, 255, 200)
COLOR_LOCO = (255, 50, 150)
COLOR_FONDO = (60, 60, 90)

CONFIG_FILE = "config.json"

class BBotApp:
    def __init__(self):
        pygame.init()
        # Forzar Pantalla Completa a 800x400
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("B-Bot de Pablo Ali")
        self.clock = pygame.time.Clock()
        
        # Datos persistentes
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f: self.datos = json.load(f)
        else:
            self.datos = {"nombre": "Pablo Ali", "nivel": 1, "xp": 0}

        # --- INICIALIZACIÓN DE TODOS LOS JOYSTICKS ---
        pygame.joystick.init()
        self.controles = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.controles.append(joy)
            print(f"Control {i} detectado: {joy.get_name()}")

        self.mood = "feliz"
        self.texto = f"¡HOLA PABLO ALI! PRESIONA CUALQUIER BOTON"
        self.running = True

    def dibujar_interfaz(self):
        self.screen.fill(COLOR_FONDO)
        
        # 1. CUERPO (Ajustado para dejar espacio a la letra grande)
        pygame.draw.ellipse(self.screen, (40, 40, 70), (280, 270, 240, 30))
        pygame.draw.rect(self.screen, COLOR_CUERPO, (300, 20, 200, 250), border_radius=60)
        
        # 2. CARA DIGITAL
        pygame.draw.rect(self.screen, COLOR_PANTALLA, (320, 60, 160, 90), border_radius=15)

        # 3. OJOS (Pestañeo aleatorio)
        tiempo = pygame.time.get_ticks()
        if not (tiempo % 4000 < 150):
            color = COLOR_VIVO if self.mood == "feliz" else COLOR_LOCO
            # Ojo Izquierdo
            pygame.draw.circle(self.screen, color, (355, 105), 22) 
            pygame.draw.circle(self.screen, (255, 255, 255), (355, 105), 10)
            # Ojo Derecho
            pygame.draw.circle(self.screen, color, (445, 105), 22)
            pygame.draw.circle(self.screen, (255, 255, 255), (445, 105), 10)

        # 4. BOCA
        if self.mood == "feliz":
            pygame.draw.rect(self.screen, COLOR_VIVO, (370, 190, 60, 10), border_radius=5)
        else:
            pygame.draw.circle(self.screen, COLOR_LOCO, (400, 200), 15, 3)

        # 5. BURBUJA DE TEXTO (Letra muy grande para Pablo Alí)
        pygame.draw.rect(self.screen, (255, 255, 255), (30, 285, 740, 95), border_radius=20)
        
        # Usamos Arial Bold (Fuente estándar en la mayoría de sistemas)
        font = pygame.font.SysFont("Arial", 28, bold=True)
        
        # Dividir texto en 2 líneas
        palabras = self.texto.split(' ')
        l1, l2 = "", ""
        for p in palabras:
            if len(l1 + p) < 28: l1 += p + " "
            else: l2 += p + " "

        s1 = font.render(l1.upper(), True, (30, 30, 60))
        s2 = font.render(l2.upper(), True, (30, 30, 60))
        self.screen.blit(s1, (60, 295))
        self.screen.blit(s2, (60, 335))

        # 6. BARRA DE NIVEL
        pygame.draw.rect(self.screen, (30, 30, 50), (20, 20, 180, 20), border_radius=10)
        ancho_xp = (self.datos["xp"] / 50) * 170
        pygame.draw.rect(self.screen, COLOR_VIVO, (25, 25, ancho_xp, 10), border_radius=5)

    def guardar(self):
        with open(CONFIG_FILE, 'w') as f: json.dump(self.datos, f)

    def run(self):
        while self.running:
            self.dibujar_interfaz()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                
                # --- DETECCIÓN DINÁMICA DE BOTONES ---
                if event.type == pygame.JOYBUTTONDOWN:
                    print(f"Control {event.joy} - Botón {event.button}") # Debug
                    
                    # Acción A (Dato Curioso): Acepta botones 0, 1 o 2 (Mapeos comunes)
                    if event.button in [0, 1, 2]:
                        self.mood = "feliz"
                        self.texto = obtener_dato_curioso(self.datos)
                        self.datos["xp"] += 10
                        if self.datos["xp"] >= 50:
                            self.datos["nivel"] += 1
                            self.datos["xp"] = 0
                            self.texto = "¡SUBIMOS DE NIVEL! GENIAL PABLO ALI"
                        self.guardar()
                    
                    # Acción B (Chiste): Acepta botones 1, 3 o 4
                    elif event.button in [1, 3, 4]:
                        self.mood = "loco"
                        self.texto = obtener_chiste()
                    
                    # Botón Salir (Start/Select o botón 7/8/9)
                    elif event.button in [7, 8, 9]:
                        self.running = False

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotApp()
    app.run()
    pygame.quit()
