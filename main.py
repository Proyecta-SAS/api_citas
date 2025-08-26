import json
from datetime import datetime, timedelta, date
import holidays
import sys
from collections import defaultdict

#V.6

def obtener_festivos_y_domingos():
    año = date.today().year
    festivos = holidays.CountryHoliday('CO', years=[año])

    inicio = date(año, 1, 1)
    fin = date(año, 12, 31)
    delta = timedelta(days=1)

    festivos_y_domingos = []

    while inicio <= fin:
        if inicio.weekday() == 6 or inicio in festivos:  # Domingo o festivo
            festivos_y_domingos.append(inicio.isoformat())
        inicio += delta

    return festivos_y_domingos

def parsear_citas(citas_json):
    citas = []
    for item in citas_json.get("result", []):
        citas.append({
            "DATE_FROM": item["DATE_FROM"],
            "DATE_TO": item["DATE_TO"]
        })
    return citas

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Se requiere al menos un argumento (citas_json)"}))
        return

    try:
        citas_json = json.loads(sys.argv[1])
    except Exception as e:
        print(json.dumps({"error": f"Error al interpretar JSON de citas: {str(e)}"}))
        return

    # Empezar desde mañana y contar 8 días
    hoy = datetime.now().date() + timedelta(days=1)
    fecha_fin = hoy + timedelta(days=7)
    festivos_y_domingos = obtener_festivos_y_domingos()

    horas_trabajo = [(hour, hour + 1) for hour in range(8, 17)]  # 8:00 a 17:00
    disponibilidad_por_dia = {}

    current_date = hoy
    while current_date <= fecha_fin:
        fecha_iso = current_date.isoformat()

        if fecha_iso in festivos_y_domingos:
            current_date += timedelta(days=1)
            continue

        citas_dia = []

        for start_hour, end_hour in horas_trabajo:
            inicio = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=start_hour)
            fin = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=end_hour)

            ocupado = False
            for cita in parsear_citas(citas_json):
                cita_inicio = datetime.strptime(cita["DATE_FROM"], "%d/%m/%Y %H:%M:%S")
                cita_fin = datetime.strptime(cita["DATE_TO"], "%d/%m/%Y %H:%M:%S")

                if not (fin <= cita_inicio or inicio >= cita_fin):
                    ocupado = True
                    break

            if not ocupado:
                citas_dia.append({
                    "hora_inicio": inicio.strftime("%H:%M"),
                    "hora_fin": fin.strftime("%H:%M")
                })

        disponibilidad_por_dia[fecha_iso] = citas_dia
        current_date += timedelta(days=1)

    resultado = []
    for dia in sorted(disponibilidad_por_dia):
        resultado.append({
            "dia": dia,
            "citas": disponibilidad_por_dia[dia]
        })

    print(json.dumps(resultado, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
