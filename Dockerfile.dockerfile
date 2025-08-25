# Imagen base con PHP 8.2 (CLI incluye servidor embebido)
FROM php:8.2-cli

# Instala Python 3 y pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Crea carpeta de trabajo
WORKDIR /app

# Copia tu código dentro del contenedor
COPY . /app

# Si tienes dependencias Python
# RUN pip3 install --no-cache-dir -r requirements.txt

# Railway inyecta $PORT automáticamente
ENV PORT=8080

# Comando de arranque: servidor embebido de PHP
CMD php -S 0.0.0.0:$PORT -t public
