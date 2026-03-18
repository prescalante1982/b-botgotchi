#!/bin/bash
# Dar permisos a los controles USB y Bluetooth
sudo chmod 666 /dev/input/js*
sudo chmod 666 /dev/input/event*

# Entrar a la carpeta y ejecutar el B-Bot
cd /home/pi/b-botgotchi
# Si usas entorno virtual, usa la ruta al python del venv:
/usr/bin/python3 main.py
