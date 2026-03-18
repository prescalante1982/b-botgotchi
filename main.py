import pygame
import time
import math
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES VIBRANTES ---
COLOR_FONDO = (30, 30, 60)
COLOR_NEON = (0, 255, 200)
COLOR_RESALTADO = (255, 200, 0) # Amarillo para la selección

class BBotFinal:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        
        # Ajuste de pantalla para Raspberry
        try:
            self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        except:
            self.screen = pygame.display.set_mode((800, 400))
            
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Estado del Menú
        self.opciones = ["JUGAR", "COMER", "CHISTE", "CUENTO"]
        self.seleccion = 0
        self.texto = "¡HOLA PABLO ALI! MUEVETE CON LAS FLECHAS"
        
        # Inicializar TODOS los joysticks conectados
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.joysticks.append(joy)

    def dibujar_interfaz(self):
        self.screen.fill(COLOR_FONDO)
        t = pygame.time.get_ticks()
        
        # 1. EL B-BOT (Animado y en el centro)
        flotar = math.sin(t * 0.005) * 15
        cx, cy = 400, 160 + flotar
        
        # Cuerpo y Cara
        pygame.draw.rect(self.screen, (255, 255, 255), (cx-60, cy-70, 120, 140), border_radius=40)
        pygame.draw.rect(self.screen, (20, 20, 25), (cx-45, cy-45, 90, 60), border_radius=10)
        
        # Ojos Neón con parpadeo
        if (t % 4000 > 200):
            pygame.draw.circle(self.screen, COLOR_NEON, (cx-20, cy-15), 12)
            pygame.draw.circle(self.screen, COLOR_NEON, (cx+20, cy-15), 12)

        # 2. BOTONES DEL MENÚ (Estilo moderno)
        for i, nombre in enumerate(self.opciones):
            x = 100 + i * 200
            y = 300
            es_sel = (self.seleccion == i)
            
            # Si está seleccionado, brilla y se mueve un poco
            offset_y = math.sin(t * 0.01) * 4 if es_sel else 0
            color = COLOR_RESALTADO if es_sel else (100, 100, 150)
            
            pygame.draw.rect(self.screen, color, (x-75, y + offset_y, 150, 50), border_radius=15)
            font = pygame.font.SysFont("Arial", 20, bold=True)
            txt_color = (30, 30, 60) if es_sel else (255, 255, 255)
            txt_surf = font.render(nombre, True, txt_color)
            self.screen.blit(txt_surf, (x - txt_surf.get_width()//2, y + 12 + offset_y))

        # 3. BURBUJA DE TEXTO SUPERIOR
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 20, 700, 60), border_radius=15)
        font_msg = pygame.font.SysFont("Arial", 22, bold=True)
        msg_surf = font_msg.render(self.texto.upper(), True, (50, 50, 80))
        self.screen.blit(msg_surf, (400 - msg_surf.get_width()//2, 35))

    def run(self):
        while self.running:
            self.dibujar_interfaz()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # --- CONTROL POR TECLADO (Para tus pruebas rápidas) ---
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: self.running = False
                    if event.key == pygame.K_RIGHT: self.seleccion = (self.seleccion + 1) % 4
                    if event.key == pygame.K_LEFT: self.seleccion = (self.seleccion - 1) % 4
                    if event.key == pygame.K_RETURN: self.texto = f"ELEGISTE {self.opciones[self.seleccion]}"

                # --- CONTROL POR JOYSTICK (Flechas y Ejes) ---
                # 1. D-PAD (Hats)
                if event.type == pygame.JOYHATMOTION:
                    hx, hy = event.value
                    if hx == 1: self.seleccion = (self.seleccion + 1) % 4
                    if hx == -1: self.seleccion = (self.seleccion - 1) % 4

                # 2. BOTONES (A, B, X, Y)
                if event.type == pygame.JOYBUTTONDOWN:
                    # Cualquier botón del 0 al 3 servirá para elegir (A, B, X, Y)
                    if event.button in [0, 1, 2, 3]:
                        opc = self.opciones[self.seleccion]
                        if opc == "JUGAR": self.texto = "¡CARGANDO EL LABERINTO!"
                        elif opc == "COMER": self.texto = "¡YUM! ¡QUE RICO!"
                        elif opc == "CHISTE": self.texto = obtener_chiste()
                        elif opc == "CUENTO": self.texto = "HABIA UNA VEZ UN ROBOT..."
                    
                    # Botones de Sistema (Salir)
                    if event.button in [6, 7, 8, 9]:
                        self.texto = "¡HOLA PABLO ALI!"

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotFinal()
    app.run()
