import json
from datetime import datetime, timedelta, date, time
import holidays
import sys

# V.6.3 — Limpieza de variables y manejo de errores

def obtener_festivos_y_domingos(año: int):
    festivos = holidays.CountryHoliday('CO', years=[año])
    inicio = date(año, 1, 1)
    fin = date(año, 12, 31)
    delta = timedelta(days=1)

    festivos_y_domingos = set()
    d = inicio
    while d <= fin:
        if d.weekday() == 6 or d in festivos:  # Domingo (6) o festivo
            festivos_y_domingos.add(d.isoformat())
        d += delta
    return festivos_y_domingos

def parsear_citas(citas_json):
    citas = []
    # Estructura esperada: {"result": [{"DATE_FROM": "dd/mm/YYYY HH:MM:SS", "DATE_TO": "dd/mm/YYYY HH:MM:SS"}, ...]}
    for item in citas_json.get("result", []):
        try:
            citas.append({
                "DATE_FROM": item["DATE_FROM"],
                "DATE_TO": item["DATE_TO"]
            })
        except KeyError as e:
            # Si algún item no trae las claves correctas, lo saltamos con seguridad
            continue
    return citas

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Se requiere al menos un argumento (citas_json)"}))
        return

    # Parseo del JSON de citas
    try:
        citas_json = json.loads(sys.argv[1])
    except Exception as e:
        print(json.dumps({"error": f"Error al interpretar JSON de citas: {str(e)}"}))
        return

    # Ventana de análisis: desde mañana (inclusive) por 8 días calendario
    hoy = date.today() + timedelta(days=1)
    fecha_fin = hoy + timedelta(days=7)

    festivos_y_domingos = obtener_festivos_y_domingos(hoy.year)

    # Configuración de slots: cada 20 minutos entre 08:00 y 17:00 (tope exclusivo)
    slot_minutes = 20
    hora_inicio_jornada = time(8, 0, 0)
    hora_fin_jornada = time(17, 0, 0)  # exclusivo

    # Preparseo de citas a objetos datetime para evitar reprocesar en cada slot
    citas_parsed = []
    for c in parsear_citas(citas_json):
        try:
            ci = datetime.strptime(c["DATE_FROM"], "%d/%m/%Y %H:%M:%S")
            cf = datetime.strptime(c["DATE_TO"], "%d/%m/%Y %H:%M:%S")
            if cf <= ci:
                # Ignoramos rangos inválidos
                continue
            citas_parsed.append((ci, cf))
        except Exception:
            # Si alguna cita viene con formato inválido, la omitimos
            continue

    disponibilidad_por_dia = {}

    d = hoy
    while d <= fecha_fin:
        fecha_iso = d.isoformat()

        # Saltar domingos/festivos
        if fecha_iso in festivos_y_domingos:
            d += timedelta(days=1)
            continue

        # Construir la franja del día
        inicio_jornada_dt = datetime.combine(d, hora_inicio_jornada)
        fin_jornada_dt = datetime.combine(d, hora_fin_jornada)

        # Generar slots
        slots = []
        cursor = inicio_jornada_dt
        while cursor < fin_jornada_dt:
            fin_slot = cursor + timedelta(minutes=slot_minutes)

            # Verificar choque con alguna cita existente
            ocupado = False
            for ci, cf in citas_parsed:
                # Sólo consideramos citas que intersecten este mismo día
                if ci.date() != d and cf.date() != d and not (ci.date() < d < cf.date()):
                    continue
                # Intersección de intervalos: NOT (fin_slot <= ci OR cursor >= cf)
                if not (fin_slot <= ci or cursor >= cf):
                    ocupado = True
                    break

            if not ocupado:
                slots.append({
                    "hora_inicio": cursor.strftime("%H:%M"),
                    "hora_fin": fin_slot.strftime("%H:%M")
                })

            cursor = fin_slot

        disponibilidad_por_dia[fecha_iso] = slots
        d += timedelta(days=1)

    # Resultado ordenado
    resultado = [{"dia": k, "citas": disponibilidad_por_dia[k]} for k in sorted(disponibilidad_por_dia)]
    print(json.dumps(resultado, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Captura de cualquier error no manejado para evitar 500 genéricos sin contexto
        print(json.dumps({
            "error": "Error inesperado en la ejecución",
            "detail": str(e)
        }))
