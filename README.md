#Disponibilidad de citas (PHP + Python) – README v3.0

Sistema sencillo para calcular disponibilidad horaria en los próximos 8 días (desde mañana), excluyendo domingos y festivos de Colombia, a partir de un listado de citas existentes.
El endpoint está en PHP y delega el cálculo a un script Python que usa la librería holidays.

Nota rápida: el archivo que recibiste como index.py es código PHP. Renómbralo a index.php para evitar confusiones.


#Estructura
.
├─ index.php       # Endpoint HTTP (antes llamado index.py)
└─ main.py         # Motor de cálculo de disponibilidad



#Requisitos

 - PHP 7.4+ (o 8.x) con exec habilitado.

 - Python 3.8+

 - Paquete Python:

    - holidays (para festivos de Colombia)


#Endpoint

URL: POST /
Content-Type: application/json


#Cuerpo de la solicitud

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



El cálculo revisa bloques de 1 hora entre 08:00 y 17:00 (8–9, 9–10, …, 16–17).
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



#Errores posibles

Sin cuerpo en la solicitud:

{ "error": "No se recibió ningún cuerpo en la solicitud" }

{ "error": "Se requiere el campo 'citas'" }

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

Calcula desde mañana hasta 7 días después (8 días en total).

Omite domingos y festivos de Colombia (holidays.CountryHoliday('CO')).

Genera bloques horarios de 1 hora entre 08:00–17:00.

Marca un bloque como ocupado si se solapa con cualquier cita dada.

Devuelve la lista de días con sus bloques disponibles.




#Personalización

Horario laboral: edita en main.py

horas_trabajo = [(hour, hour + 1) for hour in range(8, 17)]


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