#!/usr/bin/env python3
import json
import os
import sys
from urllib import request, error

# Cambia esta URL si tu endpoint es diferente
DEFAULT_URL = "https://citas.proyectasolutions.co/"


def ensure_trailing_slash(url: str) -> str:
    return url if url.endswith("/") else url + "/"


def get_base_url(argv) -> str:
    # 1er argumento que parezca URL
    if len(argv) > 1 and argv[1].startswith("http"):
        return ensure_trailing_slash(argv[1])
    env_url = os.environ.get("BASE_URL")
    if env_url:
        return ensure_trailing_slash(env_url)
    return ensure_trailing_slash(DEFAULT_URL)


def load_calendar(argv):
    """Carga el calendario en el formato:
    [ { "body": { "result": [ {"DATE_FROM":..., "DATE_TO":...}, ... ] }, "headers": {...}, "statusCode": 200 } ]
    Se puede pasar ruta por 1er o 2do argumento, o por env CALENDAR_FILE.
    Si no se encuentra, retorna un ejemplo mínimo con ese shape.
    """
    # Detectar ruta en argumentos
    candidate = None
    if len(argv) > 1 and not argv[1].startswith("http"):
        candidate = argv[1]
    if len(argv) > 2:
        candidate = argv[2]
    candidate = os.environ.get("CALENDAR_FILE", candidate)

    if candidate and os.path.isfile(candidate):
        try:
            with open(candidate, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"No se pudo leer {candidate}: {e}. Usando muestra mínima.")

    # Muestra mínima con el mismo shape
    return [
        {
            "body": {
                "result": [
                    {
                        "ID": "sample-1",
                        "DATE_FROM": "26/09/2025 09:00:00",
                        "DATE_TO": "26/09/2025 09:30:00",
                        "TZ_FROM": "America/Bogota",
                        "TZ_TO": "America/Bogota"
                    },
                    {
                        "ID": "sample-2",
                        "DATE_FROM": "29/09/2025 10:00:00",
                        "DATE_TO": "29/09/2025 11:00:00",
                        "TZ_FROM": "America/Bogota",
                        "TZ_TO": "America/Bogota"
                    }
                ],
                "time": {
                    "start": 0, "finish": 0, "duration": 0, "processing": 0,
                    "date_start": "", "date_finish": "", "operating": 0
                }
            },
            "headers": {"content-type": "application/json"},
            "statusCode": 200
        }
    ]


def calendar_to_citas(calendar):
    """Extrae citas.result con DATE_FROM y DATE_TO desde calendar[0].body.result"""
    try:
        body = calendar[0]["body"]
        result = body.get("result", [])
        citas = []
        for ev in result:
            df = ev.get("DATE_FROM")
            dt = ev.get("DATE_TO")
            if isinstance(df, str) and isinstance(dt, str):
                citas.append({"DATE_FROM": df, "DATE_TO": dt})
        return {"result": citas}
    except Exception:
        return {"result": []}


def main(argv):
    url = get_base_url(argv)
    calendar = load_calendar(argv)

    # Construir payload con filtros y el calendario en el formato requerido + citas derivadas
    payload = {
        "minutos": 30,
        "Cantidad_dias": 3,
        "filtro": {
            "dias_habiles": ["Lunes"],
            "jornada": 1
        },
        # Se envía el calendario crudo como lo recibiste
        "calendar": calendar,
        # Y además, para que el backend bloquee solapes, se transforma a citas.result
        "citas": calendar_to_citas(calendar)
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    req = request.Request(url, data=data, headers=headers, method="POST")

    print("Payload enviado (resumido):")
    preview = payload.copy()
    # evitar imprimir todo el calendario si es muy grande
    preview["calendar"] = "<calendar omitido: %d elementos>" % len(calendar)
    print(json.dumps(preview, ensure_ascii=False, indent=2))

    try:
        with request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            print(f"\n[POST] {url} -> {resp.status}")
            print(body)
    except error.HTTPError as e:
        print(f"\n[POST] {url} -> HTTP {e.code}")
        print(e.read().decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"\n[POST] {url} -> ERROR: {e}")


if __name__ == "__main__":
    main(sys.argv)
