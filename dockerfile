# PHP + Nginx ya listos
FROM richarvey/nginx-php-fpm:3.1.6

# Paquetes del sistema: Python, pip y zona horaria
RUN apk add --no-cache python3 py3-pip tzdata

# Zona horaria
ENV TZ=America/Bogota
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo "$TZ" > /etc/timezone

# Logs de PHP a STDERR para verlos en Railway
ENV PHP_ERRORS_STDERR=1

# Código
WORKDIR /var/www/html
COPY . .

# Dependencias de Python
RUN python3 -m pip install --no-cache-dir -U pip \
 && python3 -m pip install --no-cache-dir -r requirements.txt
