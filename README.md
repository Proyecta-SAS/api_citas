#Disponibilidad de citas (PHP + Python) – README v9.3

Sistema sencillo para calcular disponibilidad horaria en los próximos 8 días (desde mañana), excluyendo domingos y festivos de Colombia, a partir de un listado de citas existentes.
El endpoint está en PHP y delega el cálculo a un script Python que usa la librería holidays. Soporta:
- Modo clásico (con citas existentes)
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


#Cuerpo de la solicitud (modo clásico)

El JSON debe incluir el campo citas.
Dentro de citas se espera un objeto con el arreglo result, donde cada elemento contiene DATE_FROM y DATE_TO en formato DD/MM/YYYY HH:MM:SS.

{
  "citas": {
    "result": [
      {
        "DATE_FROM": "26/08/2025 09:00:00",
        "DATE_TO":   "26/08/2025 10:00:00"
      },
      {
        "DATE_FROM": "27/08/2025 14:30:00",
        "DATE_TO":   "27/08/2025 16:00:00"
      }
    ]
  }
}



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


## Modo por filtros (nuevo)

Permite definir días hábiles específicos, horario y tamaño de slot, y limitar cuántas ocurrencias por día de la semana devolver.

Payload de ejemplo (similar a envio.json):

{
  "minutos": 30,
  "Cantidad_dias": 3,
  "filtro": {
    "dias_habiles": ["Lunes"],
    "jornada": 1
  },
  "citas": {  // opcional: bloquea solapes si se incluye
    "result": [
      { "DATE_FROM": "23/09/2025 09:00:00", "DATE_TO": "23/09/2025 10:00:00" }
    ]
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
- Si se especifican varios días en "dias_habiles", se devuelven hasta "Cantidad_dias" ocurrencias por cada día de la semana seleccionado.
- Si no se especifica "dias_habiles", se consideran días laborales (lunes a sábado), excluyendo domingos y festivos.


## Cantidad_dias sin filtro (nuevo)

Si envías `Cantidad_dias` sin el bloque `filtro`, el sistema devuelve los próximos N días válidos consecutivos a partir de mañana, excluyendo domingos y festivos de Colombia, en lugar de la ventana fija de 8 días.

Ejemplo:

{
  "Cantidad_dias": 3,
  "minutos": 20,
  "citas": {
    "result": [
      { "DATE_FROM": "26/09/2025 09:00:00", "DATE_TO": "26/09/2025 10:00:00" }
    ]
  }
}

Si hoy es lunes, retornará disponibilidad para martes, miércoles y jueves.


## Calendario estilo Bitrix (nuevo)

Además del bloque "citas", puedes enviar el calendario crudo obtenido de Bitrix en este shape, y el backend lo transformará internamente para bloquear solapes:

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

- v9.3
  - Nuevo: `Cantidad_dias` sin `filtro` devuelve los próximos N días válidos consecutivos desde mañana (excluye domingos y festivos de Colombia).
  - `minutos` actúa globalmente para el tamaño de slot (si no se especifica, por defecto 20).
  - Documentación actualizada (ejemplos Postman y calendario Bitrix).

- v9.2
  - Agregado modo por filtros (`filtro.dias_habiles`, `filtro.jornada`/`filtro.horario`).
  - Soporte de calendario estilo Bitrix (`calendar[].body.result`).
  - Combinación de `citas` + `calendar` para bloquear solapes.

hoy = datetime.now().date() + timedelta(days=1)
fecha_fin = hoy + timedelta(days=7)

festivos = holidays.CountryHoliday('CO', years=[año])


#Seguridad y notas

index.php usa escapeshellarg para pasar de forma segura el JSON a Python.

Asegúrate de que el binario de Python esté disponible como python3 en tu PATH del entorno donde corre PHP-FPM/Apache.

Considera limitar tamaño de payload y rate limiting si el endpoint se expone públicamente.

Zonas horarias: el código usa la hora del sistema (datetime.now()); alinéala con tu operación (ej. America/Bogota).

Cambio de año: actualmente se cargan festivos solo del año actual. Si el rango cruzara fin de año, extiende years=[año, año+1].


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
