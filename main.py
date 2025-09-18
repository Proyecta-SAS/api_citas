import json
from datetime import datetime, timedelta, date, time
import holidays
import sys

# V.9.1 — Modo clásico (citas) + modo filtros (envio.json) + calendario Bitrix (calendar[].body.result)


def normalizar_dia_es(d: str) -> str:
    s = (d or "").strip().lower()
    # normalización básica de tildes y variantes
    s = s.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    return s


SPANISH_DAY_TO_WEEKDAY = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,  # por si llegara con tilde
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}


def parsear_citas(citas_json):
    citas = []
    if not isinstance(citas_json, dict):
        return citas
    # Estructura esperada: {"result": [{"DATE_FROM": "dd/mm/YYYY HH:MM:SS", "DATE_TO": "dd/mm/YYYY HH:MM:SS"}, ...]}
    for item in citas_json.get("result", []):
        try:
            citas.append({
                "DATE_FROM": item["DATE_FROM"],
                "DATE_TO": item["DATE_TO"]
            })
        except Exception:
            continue
    return citas


def extraer_citas_de_calendar(calendar_json):
    """Acepta el arreglo de calendario estilo Bitrix
    [ { "body": { "result": [ {"DATE_FROM":..., "DATE_TO":...}, ... ] }, ... } ]
    y retorna lista de dicts {DATE_FROM, DATE_TO}.
    """
    citas = []
    try:
        if isinstance(calendar_json, list) and calendar_json:
            body = calendar_json[0].get("body", {}) if isinstance(calendar_json[0], dict) else {}
            result = body.get("result", []) if isinstance(body, dict) else []
            for ev in result:
                if not isinstance(ev, dict):
                    continue
                df = ev.get("DATE_FROM")
                dt = ev.get("DATE_TO")
                if isinstance(df, str) and isinstance(dt, str):
                    citas.append({"DATE_FROM": df, "DATE_TO": dt})
    except Exception:
        pass
    return citas


def parsear_horario(horario_json):
    # Retorna tupla (time_desde, time_hasta) o valores por defecto 08:00-17:00
    por_defecto = (time(8, 0, 0), time(17, 0, 0))
    if not isinstance(horario_json, dict):
        return por_defecto
    desde_s = horario_json.get("desde")
    hasta_s = horario_json.get("hasta")
    try:
        if desde_s:
            h, m = [int(x) for x in desde_s.split(":", 1)]
            t_desde = time(h, m, 0)
        else:
            t_desde = por_defecto[0]
        if hasta_s:
            h2, m2 = [int(x) for x in hasta_s.split(":", 1)]
            t_hasta = time(h2, m2, 0)
        else:
            t_hasta = por_defecto[1]
        return (t_desde, t_hasta)
    except Exception:
        return por_defecto


def hay_interseccion(a_inicio: datetime, a_fin: datetime, b_inicio: datetime, b_fin: datetime) -> bool:
    # Intersección de intervalos: NOT (a_fin <= b_inicio OR a_inicio >= b_fin)
    return not (a_fin <= b_inicio or a_inicio >= b_fin)


def generar_slots_para_dia(d: date, t_desde: time, t_hasta: time, slot_minutes: int, citas_parsed):
    inicio_dt = datetime.combine(d, t_desde)
    fin_dt = datetime.combine(d, t_hasta)
    if fin_dt <= inicio_dt:
        return []

    slots = []
    cursor = inicio_dt
    delta = timedelta(minutes=max(1, int(slot_minutes)))
    while cursor < fin_dt:
        fin_slot = cursor + delta
        ocupado = False
        for ci, cf in citas_parsed:
            # Considerar citas que puedan cruzar días
            if not (ci.date() == d or cf.date() == d or (ci.date() < d < cf.date())):
                continue
            if hay_interseccion(cursor, fin_slot, ci, cf):
                ocupado = True
                break
        if not ocupado:
            slots.append({
                "hora_inicio": cursor.strftime("%H:%M"),
                "hora_fin": fin_slot.strftime("%H:%M"),
            })
        cursor = fin_slot
    return slots


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Se requiere al menos un argumento (payload JSON)"}))
        return

    # Parseo del JSON de entrada (puede traer 'citas' y/o 'filtro')
    try:
        payload = json.loads(sys.argv[1])
    except Exception as e:
        print(json.dumps({"error": f"Error al interpretar JSON: {str(e)}"}))
        return

    # Normalización: si viene un arreglo directamente, asuma que es
    # - calendario Bitrix: [ { body: { result: [...] } } ]
    # - o lista de eventos [{DATE_FROM, DATE_TO}, ...]
    if isinstance(payload, list):
        citas_list = []
        if payload and isinstance(payload[0], dict) and "body" in payload[0]:
            citas_list.extend(extraer_citas_de_calendar(payload))
        else:
            for ev in payload:
                if isinstance(ev, dict) and "DATE_FROM" in ev and "DATE_TO" in ev:
                    citas_list.append({
                        "DATE_FROM": ev["DATE_FROM"],
                        "DATE_TO": ev["DATE_TO"],
                    })
        payload = {"citas": {"result": citas_list}}

    hoy = date.today() + timedelta(days=1)  # empezamos desde mañana
    # Festivos de Colombia, sin limitar por año para soportar rangos largos
    festivos_co = holidays.CountryHoliday('CO')

    # Configuración común
    slot_minutes = 20
    if isinstance(payload, dict) and isinstance(payload.get("minutos"), int) and payload["minutos"] > 0:
        slot_minutes = int(payload["minutos"])

    # Citas existentes (opcional) y/o calendario Bitrix (opcional)
    citas_parsed = []
    citas_fuente = []
    if isinstance(payload, dict):
        if "citas" in payload:
            citas_fuente.extend(parsear_citas(payload.get("citas", {})))
        if "calendar" in payload:
            citas_fuente.extend(extraer_citas_de_calendar(payload.get("calendar")))

    for c in citas_fuente:
        try:
            ci = datetime.strptime(c["DATE_FROM"], "%d/%m/%Y %H:%M:%S")
            cf = datetime.strptime(c["DATE_TO"], "%d/%m/%Y %H:%M:%S")
            if cf > ci:
                citas_parsed.append((ci, cf))
        except Exception:
            continue

    disponibilidad_por_dia = {}

    filtro = payload.get("filtro") if isinstance(payload, dict) else None

    if isinstance(filtro, dict):
        # Modo nuevo por filtros (como envio.json)
        dias_habiles_raw = filtro.get("dias_habiles", []) or []
        dias_wd = set()
        for dname in dias_habiles_raw:
            key = normalizar_dia_es(str(dname))
            if key in SPANISH_DAY_TO_WEEKDAY:
                dias_wd.add(SPANISH_DAY_TO_WEEKDAY[key])

        t_desde, t_hasta = parsear_horario(filtro.get("horario", {}))
        cantidad_dias = payload.get("Cantidad_dias")
        try:
            cantidad_dias = int(cantidad_dias) if cantidad_dias is not None else None
        except Exception:
            cantidad_dias = None

        # Si no se especifican días hábiles, consideramos todos los días laborales (lun-sab) excepto domingos
        if not dias_wd:
            dias_wd = {0, 1, 2, 3, 4, 5}

        # Contadores por día de semana si se dio Cantidad_dias
        counts = {wd: 0 for wd in dias_wd}

        d = hoy
        max_loop_days = 365 * 2  # límite de seguridad
        loops = 0
        while True:
            loops += 1
            if loops > max_loop_days:
                break

            # Saltar domingos y festivos
            if d.weekday() == 6 or d in festivos_co:
                d += timedelta(days=1)
                continue

            wd = d.weekday()
            if wd in dias_wd:
                # Si se configuró cantidad_dias, verificar por día de semana
                if cantidad_dias is None or counts.get(wd, 0) < cantidad_dias:
                    slots = generar_slots_para_dia(d, t_desde, t_hasta, slot_minutes, citas_parsed)
                    disponibilidad_por_dia[d.isoformat()] = slots
                    if cantidad_dias is not None:
                        counts[wd] = counts.get(wd, 0) + 1

            # Condición de término cuando todos alcanzan cantidad_dias
            if cantidad_dias is not None and dias_wd and all(counts[wd] >= cantidad_dias for wd in dias_wd):
                break

            d += timedelta(days=1)

    else:
        # Modo clásico: próximos 8 días (excluyendo domingos y festivos), 08:00-17:00
        t_desde, t_hasta = time(8, 0, 0), time(17, 0, 0)
        fecha_fin = hoy + timedelta(days=7)

        d = hoy
        while d <= fecha_fin:
            if d.weekday() == 6 or d in festivos_co:
                d += timedelta(days=1)
                continue
            slots = generar_slots_para_dia(d, t_desde, t_hasta, slot_minutes, citas_parsed)
            disponibilidad_por_dia[d.isoformat()] = slots
            d += timedelta(days=1)

    resultado = [{"dia": k, "citas": disponibilidad_por_dia[k]} for k in sorted(disponibilidad_por_dia)]
    print(json.dumps(resultado, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({
            "error": "Error inesperado en la ejecución",
            "detail": str(e)
        }))
