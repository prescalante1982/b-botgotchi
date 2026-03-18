import random

def obtener_dato_curioso(datos):
    # Frases cortas y fáciles de leer para un niño
    datos_peques = [
        "¡LOS GATOS TIENEN 18 DEDOS EN TOTAL!",
        "¡EL ESPACIO ES MUY SILENCIOSO!",
        "¡LAS VACAS TIENEN MEJORES AMIGAS!",
        "¡EL SOL ES UNA ESTRELLA GIGANTE!",
        "¡LOS PULPOS TIENEN TRES CORAZONES!",
        "¡LOS DINOSAURIOS VIVIERON HACE MUCHO!",
        "¡EL AGUA DEL MAR ES SALADA!",
        "¡LAS HORMIGAS NUNCA DUERMEN!",
        "¡LOS CONEJOS COMEN MUCHAS ZANAHORIAS!"
    ]
    return random.choice(datos_peques)

def obtener_chiste():
    chistes = [
        "¿QUE HACE UNA ABEJA EN EL GYM? ¡ZUMBA!",
        "¿COMO SE DICE PAÑUELO EN JAPONES? ¡SAKAMOKO!",
        "¿QUE LE DICE UN JAGUAR A OTRO? ¡JAGUAR YOU!",
        "¿CUAL ES EL BAILE FAVORITO DEL TOMATE? ¡LA SALSA!",
        "¿POR QUE EL LIBRO DE MATES ESTA TRISTE? ¡PORQUE TIENE PROBLEMAS!"
    ]
    return random.choice(chistes)

def generar_laberinto(dim):
    # Generamos un laberinto más abierto para que sea fácil
    lab = [[0 for _ in range(dim)] for _ in range(dim)]
    for f in range(dim):
        for c in range(dim):
            if random.random() < 0.25: # Menos paredes (25%)
                lab[f][c] = 1
    lab[0][0] = 0 # Inicio libre
    lab[dim-1][dim-1] = 0 # Meta libre
    return lab
