import json
from datetime import datetime, timedelta, date, time
import holidays
import sys

# V.9.5 — Soporta 'resultado' (DATE FROM/DATE TO) como ocupación, selección de días acorde a dias_habiles y sábados hasta 13:00.


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


def parsear_resultado(payload_dict):
    """Extrae un intervalo de ocupación desde payload['resultado'].
    Soporta claves con y sin espacio: 'DATE FROM'/'DATE TO' o 'DATE_FROM'/'DATE_TO'.
    Retorna lista con a lo sumo un dict {DATE_FROM, DATE_TO}.
    """
    citas = []
    if not isinstance(payload_dict, dict):
        return citas
    res = payload_dict.get("resultado")
    if not isinstance(res, dict):
        return citas
    # Prioridad a claves con espacio si existen
    df = res.get("DATE FROM") if "DATE FROM" in res else res.get("DATE_FROM")
    dt = res.get("DATE TO") if "DATE TO" in res else res.get("DATE_TO")
    if isinstance(df, str) and isinstance(dt, str):
        citas.append({"DATE_FROM": df, "DATE_TO": dt})
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


def parsear_horario(horario_json, por_defecto=(time(8, 0, 0), time(17, 0, 0))):
    # Retorna tupla (time_desde, time_hasta) usando por_defecto si faltan claves
    if not isinstance(horario_json, dict):
        return por_defecto
    desde_s = horario_json.get("desde")
    hasta_s = horario_json.get("hasta")
    try:
        t_desde = por_defecto[0]
        t_hasta = por_defecto[1]
        if desde_s:
            h, m = [int(x) for x in desde_s.split(":", 1)]
            t_desde = time(h, m, 0)
        if hasta_s:
            h2, m2 = [int(x) for x in hasta_s.split(":", 1)]
            t_hasta = time(h2, m2, 0)
        return (t_desde, t_hasta)
    except Exception:
        return por_defecto


def hay_interseccion(a_inicio: datetime, a_fin: datetime, b_inicio: datetime, b_fin: datetime) -> bool:
    # Intersección de intervalos: NOT (a_fin <= b_inicio OR a_inicio >= b_fin)
    return not (a_fin <= b_inicio or a_inicio >= b_fin)


def generar_slots_para_dia(d: date, t_desde: time, t_hasta: time, slot_minutes: int, citas_parsed):
    # Regla: sábados (weekday==5) solo hasta las 13:00, incluso si el horario/jornada define mayor rango
    cap_sabado = time(13, 0, 0)
    t_hasta_real = t_hasta
    if d.weekday() == 5 and (t_hasta > cap_sabado):
        t_hasta_real = cap_sabado

    inicio_dt = datetime.combine(d, t_desde)
    fin_dt = datetime.combine(d, t_hasta_real)
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

    # Citas existentes (opcional) y/o calendario Bitrix (opcional) y/o resultado (requerido según nueva especificación)
    citas_parsed = []
    citas_fuente = []
    if isinstance(payload, dict):
        # 'resultado' como ocupación base (un solo intervalo)
        citas_fuente.extend(parsear_resultado(payload))
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

    # Cantidad_dias global (puede aplicarse con o sin filtro)
    cantidad_dias_global = None
    if isinstance(payload, dict):
        try:
            raw_cd = payload.get("Cantidad_dias")
            cantidad_dias_global = int(raw_cd) if raw_cd is not None else None
        except Exception:
            cantidad_dias_global = None

    filtro = payload.get("filtro") if isinstance(payload, dict) else None

    # 1) Determinar horario base (jornada u horario explícito si viene filtro)
    t_desde, t_hasta = time(8, 0, 0), time(17, 0, 0)
    dias_wd_filtro = None
    if isinstance(filtro, dict):
        # Jornada: 1 => 08:00-12:00, 2 => 12:00-17:00, 3 => 08:00-17:00
        jornada = filtro.get("jornada")
        jornada_pair = (time(8, 0, 0), time(17, 0, 0))
        try:
            jn = int(jornada) if jornada is not None else None
            if jn == 1:
                jornada_pair = (time(8, 0, 0), time(12, 0, 0))
            elif jn == 2:
                jornada_pair = (time(12, 0, 0), time(17, 0, 0))
            elif jn == 3:
                jornada_pair = (time(8, 0, 0), time(17, 0, 0))
        except Exception:
            pass
        # Horario explícito (si viene) sobreescribe a jornada
        t_desde, t_hasta = parsear_horario(filtro.get("horario", {}), por_defecto=jornada_pair)

        # Días hábiles del filtro (opcional)
        dias_habiles_raw = filtro.get("dias_habiles", []) or []
        if dias_habiles_raw:
            dias_wd_filtro = set()
            for dname in dias_habiles_raw:
                key = normalizar_dia_es(str(dname))
                if key in SPANISH_DAY_TO_WEEKDAY:
                    dias_wd_filtro.add(SPANISH_DAY_TO_WEEKDAY[key])

    # 2) Construir lista de días válidos base según Cantidad_dias y dias_habiles
    #    - Siempre excluir domingos (weekday==6) y festivos
    #    - Si hay dias_habiles, seleccionar los próximos N días que cumplan con esos días de la semana
    #    - Si no hay dias_habiles, seleccionar los próximos N días válidos
    target_count = None
    try:
        target_count = int(cantidad_dias_global) if cantidad_dias_global is not None else 7
    except Exception:
        target_count = 7

    dias_validos = []
    d = hoy
    max_loop_days = 365 * 2
    loops = 0
    while len(dias_validos) < target_count and loops < max_loop_days:
        loops += 1
        if d.weekday() != 6 and d not in festivos_co:
            if isinstance(dias_wd_filtro, set) and dias_wd_filtro:
                if d.weekday() in dias_wd_filtro:
                    dias_validos.append(d)
            else:
                dias_validos.append(d)
        d += timedelta(days=1)

    # 3) Generar slots para cada día válido
    for di in dias_validos:
        slots = generar_slots_para_dia(di, t_desde, t_hasta, slot_minutes, citas_parsed)
        disponibilidad_por_dia[di.isoformat()] = slots

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
