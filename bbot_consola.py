import pygame
import json
import sys

# Definir la estructura del B-Bot Atlas
class BBotAtlas:
    def __init__(self, json_path):
        # 1. Cargar datos del JSON
        with open(json_path, 'r') as f:
            self.data = json.load(f)
        
        # 2. Cargar la imagen del Atlas
        image_name = self.data['meta']['image']
        try:
            self.atlas_image = pygame.image.load(image_name).convert_alpha()
        except pygame.error as e:
            print(f"Error cargando imagen: {e}")
            sys.exit()

        # 3. Pre-recortar todas las expresiones para mayor velocidad
        self.sprites = {}
        for name, rect in self.data['expressions'].items():
            # Crear un sub-surface (recorte) de la imagen principal
            sprite_rect = pygame.Rect(rect['x'], rect['y'], rect['w'], rect['h'])
            self.sprites[name] = self.atlas_image.subsurface(sprite_rect)
            
    def get_expression(self, expression_name):
        """Devuelve el sprite recortado para la expresión dada."""
        # Si no existe, devuelve la neutral por defecto
        return self.sprites.get(expression_name, self.sprites['neutral'])

    def get_all_names(self):
        """Devuelve una lista de los nombres de expresiones disponibles."""
        return list(self.sprites.keys())

# --- Configuración de la Mascota ---
def ejecutar_b_bot():
    pygame.init()
    
    # Configuración de pantalla
    ANCHO, ALTO = 800, 600
    screen = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("B-Bot Mascota Virtual")
    clock = pygame.time.Clock()
    
    # Colores
    BLANCO = (255, 255, 255)
    GRIS_CLARO = (220, 220, 220)

    # Cargar el Atlas de B-Bot
    # Asegúrate de que bbot_atlas.png y bbot_mascota.json estén en la misma carpeta
    mi_bot_atlas = BBotAtlas('bbot_mascota.json')
    
    # Estado inicial
    lista_expresiones = mi_bot_atlas.get_all_names()
    indice_actual = 0
    expresion_actual = lista_expresiones[indice_actual]
    
    # Fuente para mostrar el estado
    try:
        fuente = pygame.font.SysFont("Arial", 24)
    except:
        fuente = pygame.font.Font(None, 24)

    running = True
    while running:
        # 1. Gestión de Eventos (Controles)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Cambiar expresión con flechas (simulando lógica de la mascota)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    indice_actual = (indice_actual + 1) % len(lista_expresiones)
                elif event.key == pygame.K_LEFT:
                    indice_actual = (indice_actual - 1) % len(lista_expresiones)
                
                expresion_actual = lista_expresiones[indice_actual]
                print(f"B-Bot está ahora: {expresion_actual}")

        # 2. Actualización de Lógica (Aquí iría tu código de Mascota)
        # Ejemplo: Si hambre > 80, forzar expresion_actual = "triste"

        # 3. Dibujado
        screen.fill(GRIS_CLARO) # Fondo

        # Obtener el sprite actual del Atlas
        sprite_a_dibujar = mi_bot_atlas.get_expression(expresion_actual)
        
        # Centrar el B-Bot en la pantalla
        sprite_rect = sprite_a_dibujar.get_rect()
        sprite_rect.center = (ANCHO // 2, ALTO // 2)
        
        # Dibujar el B-Bot
        screen.blit(sprite_a_dibujar, sprite_rect)
        
        # Mostrar el texto del estado actual
        texto_estado = fuente.render(f"Estado Actual: {expresion_actual.upper()}", True, (0, 0, 0))
        screen.blit(texto_estado, (20, 20))
        
        texto_ayuda = fuente.render("Usa FLECHAS Izq/Der para cambiar expresión", True, (100, 100, 100))
        screen.blit(texto_ayuda, (20, ALTO - 40))

        pygame.display.flip() # Actualizar pantalla
        clock.tick(60) # Limitar a 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    ejecutar_b_bot()
