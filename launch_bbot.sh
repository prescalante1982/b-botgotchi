#!/bin/bash

# 1. ESPERA DE SEGURIDAD
# Damos 5 segundos para que el sistema gráfico (X11) cargue por completo
sleep 5

# 2. PERMISOS DE PERIFÉRICOS
# Liberamos el acceso a joysticks USB y Bluetooth para el usuario pi
echo "Configurando controles para Pablo Ali..."
sudo chmod 666 /dev/input/js* 2>/dev/input/null
sudo chmod 666 /dev/input/event* 2>/dev/input/null

# 3. ENTRAR AL DIRECTORIO DEL REPO
# Usamos la ruta absoluta para evitar errores de systemd
cd /home/pi/b-botgotchi

# 4. BUCLE DE AUTO-ARRANQUE (Keep-Alive)
# Si Pablo presiona por error una combinación que cierre el programa,
# este bucle lo volverá a abrir infinitamente.
while true; do
    echo "Iniciando B-Bot en modo Consola..."
    
    # Ejecutamos con python3. 
    # Usamos stdbuf para que los logs se vean en tiempo real si debugueas.
    python3 main.py
    
    echo "El programa se cerró. Reiniciando en 3 segundos..."
    sleep 3
done
