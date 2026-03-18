import pygame
import json
import time
import math
import random
from utils import obtener_dato_curioso, obtener_chiste, generar_laberinto

# --- COLORES ---
COLOR_MENU = (100, 100, 255)
COLOR_TEXTO = (255, 255, 255)
COLOR_FONDO = (60, 60, 90)
COLOR_VIVO = (0, 255, 200)

class BBotConsola:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.screen = pygame.display.set_mode((800, 400), pygame.FULLSCREEN | pygame.SCALED)
        self.clock = pygame.time.Clock()
        
        # Estado del Sistema: "MENU", "JUEGO", "MASCOTA", "CHISTES", "CUENTOS"
        self.modo = "MENU"
        self.texto = "¡HOLA PABLO ALI! ¿QUE HACEMOS?"
        
        self.controles = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.controles: j.init()

        self.ultima_accion = time.time()
        self.offset_y = 0
        self.running = True

    def dibujar_menu(self):
        self.screen.fill(COLOR_FONDO)
        font_titulo = pygame.font.SysFont("Arial", 30, bold=True)
        font_opcion = pygame.font.SysFont("Arial", 22, bold=True)

        # Título
        self.screen.blit(font_titulo.render("MENU DEL B-BOT", True, COLOR_VIVO), (280, 40))

        # Opciones con botones
        opciones = [
            "1. JUGAR LABERINTO",
            "2. CUIDAR MASCOTA",
            "3. ESCUCHAR CHISTES",
            "4. LEER UN CUENTO"
        ]
        for i, opt in enumerate(opciones):
            pygame.draw.rect(self.screen, (255, 255, 255), (200, 100 + i*60, 400, 45), border_radius=10)
            txt = font_opcion.render(opt, True, (50, 50, 80))
            self.screen.blit(txt, (250, 110 + i*60))

        self.screen.blit(font_opcion.render("PRESIONA START PARA SALIR", True, (200, 200, 200)), (250, 350))

    def dibujar_cuento(self):
        self.screen.fill((50, 20, 50))
        cuentos = [
            "HABIA UNA VEZ UN ROBOT QUE QUERIA SER GUITARRISTA...",
            "UN DRAGON VERDE QUE SOLO COMIA MANZANAS AZULES.",
            "EL ASTRONAUTA QUE ENCONTRO UN QUESO EN LA LUNA.",
            "UN PERRO QUE PODIA VOLAR USANDO SUS OREJAS."
        ]
        font = pygame.font.SysFont("Arial", 22, bold=True)
        # Mostramos el cuento centrado
        txt = font.render(self.texto, True, (255, 255, 255))
        self.screen.blit(txt, (50, 180))
        self.screen.blit(font.render("PULSA CUALQUIER BOTON PARA VOLVER", True, (150, 150, 150)), (220, 350))

    def dibujar_animacion_espera(self):
        # Si no hace nada, el B-Bot baila solo
        self.screen.fill(COLOR_FONDO)
        t = pygame.time.get_ticks()
        self.offset_y = math.sin(t * 0.01) * 15
        
        # Dibujo rápido del robot bailando
        pygame.draw.rect(self.screen, (255, 255, 255), (320, 100 + self.offset_y, 160, 200), border_radius=50)
        pygame.draw.circle(self.screen, COLOR_VIVO, (360, 160 + self.offset_y), 15)
        pygame.draw.circle(self.screen, COLOR_VIVO, (440, 160 + self.offset_y), 15)
        
        font = pygame.font.SysFont("Arial", 22, bold=True)
        txt = font.render(self.texto.upper(), True, (255, 255, 255))
        self.screen.blit(txt, (100, 330))

    def run(self):
        while self.running:
            ahora = time.time()
            
            # LÓGICA DE INACTIVIDAD (10 segundos)
            if ahora - self.ultima_accion > 10 and self.modo == "MENU":
                if ahora % 5 < 0.05: # Cambia de dato cada 5 segundos
                    self.texto = "SABIAS QUE: " + obtener_dato_curioso({"gustos":[]})
                self.dibujar_animacion_espera()
            else:
                if self.modo == "MENU": self.dibujar_menu()
                elif self.modo == "CUENTOS": self.dibujar_cuento()
                # Aquí irían los otros dibujos (laberinto, mascota, etc.)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    self.ultima_accion = time.time() # Reset de tiempo
                    
                    # BOTONES DEL MENU
                    if self.modo == "MENU":
                        if event.button == 0: # Botón 1: Laberinto
                            self.modo = "JUEGO"
                            self.texto = "¡CARGANDO LABERINTO!"
                        elif event.button == 1: # Botón 2: Mascota
                            self.modo = "MASCOTA"
                            self.texto = "¡HOLA! TENGO HAMBRE"
                        elif event.button == 2: # Botón 3: Chistes
                            self.modo = "CHISTES"
                            self.texto = obtener_chiste()
                        elif event.button == 3: # Botón 4: Cuentos
                            self.modo = "CUENTOS"
                            self.texto = "HABIA UNA VEZ UN ROBOT QUE JUGABA CON PABLO..."
                    
                    # VOLVER AL MENU (Botón Select/Start o un botón específico)
                    elif event.button in [6, 7, 8, 9]: 
                        self.modo = "MENU"
                        self.texto = "¿QUE HACEMOS AHORA?"

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotConsola()
    app.run()            self.offset_y = math.sin(t * 0.01) * 20 # Salta arriba y abajo
            self.angulo = math.sin(t * 0.01) * 10   # Se balancea
            if t % 3000 < 50: self.estado = "IDLE"  # Deja de bailar tras unos segundos
        
        # 2. LÓGICA DE SUEÑO
        elif self.stats["energia"] < 30:
            self.estado = "DURMIENDO"
            self.offset_y = math.sin(t * 0.002) * 5 # Respiración lenta
        
        else:
            self.estado = "IDLE"
            self.offset_y = 0
            self.angulo = 0

    def dibujar_ojos(self, cx, cy, color):
        t = pygame.time.get_ticks()
        
        if self.estado == "DURMIENDO":
            # Ojos cerrados: - -
            pygame.draw.rect(self.screen, COLOR_SUEÑO, (cx-55, cy+105+self.offset_y, 30, 5))
            pygame.draw.rect(self.screen, COLOR_SUEÑO, (cx+25, cy+105+self.offset_y, 30, 5))
            # Letras ZzZ
            font_z = pygame.font.SysFont("Arial", 25, bold=True)
            if t % 1000 < 500:
                self.screen.blit(font_z.render("ZzZ", True, (255, 255, 255)), (cx+80, cy+50+self.offset_y))
        
        elif self.estado == "BAILANDO":
            # Ojos de estrella o alegría: ^ ^
            pygame.draw.lines(self.screen, color, False, [(cx-50, cy+110+self.offset_y), (cx-35, cy+95+self.offset_y), (cx-20, cy+110+self.offset_y)], 4)
            pygame.draw.lines(self.screen, color, False, [(cx+20, cy+110+self.offset_y), (cx+35, cy+95+self.offset_y), (cx+50, cy+110+self.offset_y)], 4)
        
        else:
            # Ojos normales con parpadeo
            if not (t % 4000 < 150):
                pygame.draw.circle(self.screen, color, (cx-40, cy+110+self.offset_y), 20)
                pygame.draw.circle(self.screen, color, (cx+40, cy+110+self.offset_y), 20)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx-40, cy+110+self.offset_y), 8)
                pygame.draw.circle(self.screen, (255, 255, 255), (cx+40, cy+110+self.offset_y), 8)

    def dibujar_bbot(self):
        self.screen.fill(COLOR_FONDO)
        cx, cy = 400, 25
        
        # Sombra en el piso
        pygame.draw.ellipse(self.screen, (40, 40, 70), (300, 270, 200, 30))
        
        # Cuerpo (Cápsula blanca)
        pygame.draw.rect(self.screen, (255, 255, 255), (310, cy+self.offset_y, 180, 240), border_radius=60)
        
        # Pantalla de la cara
        pygame.draw.rect(self.screen, (20, 20, 25), (330, cy+50+self.offset_y, 140, 80), border_radius=15)
        
        # Dibujar Ojos dinámicos
        color_ojos = COLOR_VIVO if self.estado != "DURMIENDO" else COLOR_SUEÑO
        self.dibujar_ojos(cx, cy, color_ojos)

        # Burbuja de texto
        pygame.draw.rect(self.screen, (255, 255, 255), (50, 300, 700, 80), border_radius=20)
        font = pygame.font.SysFont("FreeSans", 22, bold=True)
        self.screen.blit(font.render(self.texto.upper(), True, (50, 50, 80)), (80, 330))

    def run(self):
        while self.running:
            self.actualizar_animacion()
            self.dibujar_bbot()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0: # A: COMER
                        self.estado = "BAILANDO"
                        self.stats["hambre"] = 100
                        self.texto = "¡QUE RICO! ¡GRACIAS PABLO ALI!"
                    
                    elif event.button == 1: # B: CHISTE
                        self.estado = "BAILANDO"
                        self.texto = obtener_chiste()
                    
                    elif event.button in [2, 3]: # X/Y: DORMIR O DESPERTAR
                        if self.stats["energia"] < 50:
                            self.stats["energia"] = 100
                            self.texto = "¡YA DESPERTE! ¡A JUGAR!"
                            self.estado = "BAILANDO"
                        else:
                            self.texto = "TENGO UN POQUITO DE SUEÑO..."

            pygame.display.flip()
            self.clock.tick(30)

if __name__ == "__main__":
    app = BBotVivo()
    app.run()
