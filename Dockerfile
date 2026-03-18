# Usamos una imagen ligera de Python
FROM python:3.9-slim

# Instalamos dependencias del sistema para audio y gráficos
RUN apt-get update && apt-get install -y \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos e instalamos dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente
COPY . .
ENV PYGAME_DETECT_AVX2=1
ENV SDL_VIDEODRIVER=dummy
# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
