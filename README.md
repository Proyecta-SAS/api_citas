#Disponibilidad de citas (PHP + Python) – README v9.5

Sistema sencillo para calcular disponibilidad horaria desde mañana, excluyendo domingos y festivos de Colombia. Soporta:
- Modo "resultado" (ocupación mínima obligatoria con un rango)
- Modo clásico (citas existentes)
- Modo por filtros (similar a envio.json)
- Calendario estilo Bitrix (calendar[].body.result)

Nota rápida: el archivo que recibiste como index.py es código PHP. Renómbralo a index.php para evitar confusiones.


#Estructura
.
├─ index.php       # Endpoint HTTP (antes llamado index.py)
└─ main.py         # Motor de cálculo de disponibilidad (modos: clásico y filtros)



#Requisitos

 - PHP 7.4+ (o 8.x) con exec habilitado.

 - Python 3.8+

 - Paquete Python:

    - holidays (para festivos de Colombia)


#Endpoint

URL: POST /
Content-Type: application/json


#Cuerpo de la solicitud (modo "resultado" obligatorio)

El JSON debe incluir el campo "resultado" con las llaves "DATE FROM" y "DATE TO" (también se aceptan variantes con guion bajo). Este rango indica ocupación base sobre la cual se calculará la disponibilidad:

{
  "resultado": {
    "DATE FROM": "09/09/2025 09:00:00",
    "DATE TO":   "09/09/2025 17:00:00"
  },
  "minutos": 30,
  "Cantidad_dias": 5
}

Además, opcionalmente puedes enviar:
- "citas.result": lista adicional de ocupaciones
- "calendar": calendario Bitrix (se transforma internamente a ocupaciones)



El cálculo revisa bloques de 20 minutos entre 08:00 y 17:00
(08:00–08:20, 08:20–08:40, …, 16:40–17:00).
Cualquier solapamiento con una cita existente bloquea ese intervalo.



#Respuesta (200 OK)

Arreglo de días (desde mañana durante 8 días), cada uno con sus intervalos disponibles:

[
  {
    "dia": "2025-08-26",
    "citas": [
      { "hora_inicio": "08:00", "hora_fin": "09:00" },
      { "hora_inicio": "10:00", "hora_fin": "11:00" }
    ]
  },
  {
    "dia": "2025-08-27",
    "citas": []
  }
]


## Modo por filtros

Permite definir días hábiles específicos, horario y tamaño de slot.

Payload de ejemplo (similar a envio.json):

{
  "resultado": { "DATE FROM": "22/09/2025 09:00:00", "DATE TO": "22/09/2025 17:00:00" },
  "minutos": 30,
  "Cantidad_dias": 3,
  "filtro": {
    "dias_habiles": ["Lunes"],
    "jornada": 1
  }
}

Comportamiento:
- Devuelve sólo los próximos 3 lunes (desde mañana), excluyendo domingos y festivos de Colombia.
- Genera slots de 30 minutos según la jornada:
  - jornada 1: 08:00–12:00
  - jornada 2: 12:00–17:00
  - jornada 3: 08:00–17:00
- Si también envías "horario.desde/hasta", ese horario sobreescribe a la jornada.
- Si se incluyen "citas", no se listan los slots que se solapen.
- Si envías "Cantidad_dias" y también "dias_habiles", se seleccionan los próximos N días que cumplan con esos días de la semana (desde mañana), excluyendo domingos y festivos.
- Si envías "Cantidad_dias" pero no "dias_habiles", se seleccionan los próximos N días válidos (lunes a sábado), excluyendo domingos y festivos.
- Regla especial de sábado: la disponibilidad se limita hasta las 13:00, incluso si el horario/jornada indique una franja mayor.

### Prioridad: horario vs jornada
- Prioridad: `horario` tiene prioridad sobre `jornada` (si viene `horario`, se usa ese rango exacto).
- Si `horario` viene incompleto, se completa con la `jornada` definida; si no hay `jornada`, se usa 08:00–17:00 como complemento.
- Ejemplos:
  - `horario.desde = 09:00`, sin `horario.hasta` y `jornada = 1` → rango final 09:00–12:00.
  - `horario.hasta = 16:00`, sin `horario.desde` y sin `jornada` → rango final 08:00–16:00.
  - En sábado, el rango final nunca excede 13:00.


## Cantidad_dias (global)

`Cantidad_dias` controla cuántos días devolver a partir de mañana (excluye domingos y festivos):

- Con `dias_habiles`: se seleccionan los próximos N días que coincidan con esos días de la semana.
- Sin `dias_habiles`: se seleccionan los próximos N días válidos (lunes a sábado).
- Si no envías `Cantidad_dias`, el predeterminado es 7 días.

Ejemplo:

{
  "resultado": { "DATE FROM": "26/09/2025 09:00:00", "DATE TO": "26/09/2025 17:00:00" },
  "Cantidad_dias": 3,
  "minutos": 20
}

Si hoy es lunes, retornará disponibilidad para martes, miércoles y jueves.


## Calendario estilo Bitrix (nuevo)

Además del bloque "resultado", puedes enviar el calendario crudo obtenido de Bitrix en este shape; el backend lo transformará a ocupaciones y las combinará con "resultado":

"calendar": [
  {
    "body": {
      "result": [
        { "DATE_FROM": "19/09/2025 19:00:00", "DATE_TO": "19/09/2025 19:20:00", ... },
        ...
      ],
      "time": { ... }
    },
    "headers": { ... },
    "statusCode": 200
  }
]

Notas:
- Si envías ambos, "citas" y "calendar", se combinan para marcar ocupación.
- El parser usa los campos "DATE_FROM" y "DATE_TO" de cada evento.



#Errores posibles

Sin cuerpo en la solicitud:

{ "error": "No se recibió ningún cuerpo en la solicitud" }

{ "error": "Se requiere 'citas' o 'filtro' en el payload" }

{ "error": "Error al interpretar JSON de citas: <detalle>" }

{ "error": "Error al ejecutar el script Python" }


#Ejemplo con curl

curl -X POST http://127.0.0.1:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "citas": {
      "result": [
        { "DATE_FROM": "26/08/2025 09:00:00", "DATE_TO": "26/08/2025 10:00:00" },
        { "DATE_FROM": "27/08/2025 14:30:00", "DATE_TO": "27/08/2025 16:00:00" }
      ]
    }
  }'



#Cómo funciona

index.php:

Lee el cuerpo JSON.

Extrae citas, lo pasa a main.py por línea de comandos de forma segura (escapeshellarg).

Devuelve el stdout del script Python.

main.py:

Por defecto, calcula desde mañana hasta 7 días después (8 días en total).
Si envías `Cantidad_dias` sin `filtro`, entonces calcula los próximos N días válidos consecutivos (desde mañana), excluyendo domingos y festivos.

Omite domingos y festivos de Colombia (holidays.CountryHoliday('CO')).

Genera bloques de 20 minutos entre 08:00–17:00 (o el tamaño indicado en `minutos`).

Marca un bloque como ocupado si se solapa con cualquier cita dada.

Devuelve la lista de días con sus bloques disponibles.




#Personalización

Horario laboral y tamaño de bloque: edita en main.py

slot_minutes = 20            # tamaño del bloque en minutos
start_minutes = 8 * 60       # 08:00
end_minutes = 17 * 60        # 17:00 (exclusivo)


#Changelog

- v9.5
  - Nuevo: soporte de ocupación en `resultado` con llaves "DATE FROM" / "DATE TO".
  - Cambio: si hay `dias_habiles` y `Cantidad_dias`, se seleccionan los próximos N días que cumplan con esos días.
  - Regla de sábado: disponibilidad hasta las 13:00, aunque el horario/jornada exceda.
  - Predeterminado: 7 días y 20 minutos de slot cuando no se especifica.

- v9.4
  - Ajustes de `Cantidad_dias` y flujo de filtros.

Ejemplo de rango base:

hoy = datetime.now().date() + timedelta(days=1)


#Seguridad y notas

index.php usa escapeshellarg para pasar de forma segura el JSON a Python.

Asegúrate de que el binario de Python esté disponible como python3 en tu PATH del entorno donde corre PHP-FPM/Apache.

Considera limitar tamaño de payload y rate limiting si el endpoint se expone públicamente.

Zonas horarias: el código usa la hora del sistema (datetime.now()); alinéala con tu operación (ej. America/Bogota).

Festivos: se usan de Colombia sin limitar por año, para cubrir rangos amplios.


#Solución de problemas

“Error al ejecutar el script Python”
Verifica:

Ruta de python3 en el entorno de PHP (which python3).

Permisos de exec en php.ini y que disable_functions no bloquee exec.

Logs de PHP/servidor para detalles.

Desfase horario
Ajusta TZ del sistema y/o date.timezone en php.ini a America/Bogota.






Licencia

Este proyecto puede distribuirse bajo licencia MIT (ajústalo según tu necesidad).




🙌 Créditos

Festivos: paquete Python holidays.

Autoría: Proyecta Soluciones y tu yo del futuro que no quiere rehacer esto desde cero.


Desarrollado por Proyecta Soluciones / Davius
