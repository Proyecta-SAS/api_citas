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

    # Muestra mínima con el mismo shape, igual a lo solicitado
    return [
        {
            "body": {
            "result": [
                {
                    "ID": "914272",
                    "PARENT_ID": "914266",
                    "ACTIVE": "Y",
                    "DELETED": "N",
                    "CAL_TYPE": "user",
                    "OWNER_ID": "17890",
                    "NAME": "Excelencia Katterine Rincón",
                    "DATE_FROM": "22/09/2025 09:00:00",
                    "DATE_TO": "22/09/2025 09:15:00",
                    "ORIGINAL_DATE_FROM": None,
                    "TZ_FROM": "America/Bogota",
                    "TZ_TO": "America/Bogota",
                    "TZ_OFFSET_FROM": "-18000",
                    "TZ_OFFSET_TO": "-18000",
                    "DATE_FROM_TS_UTC": "1747652400",
                    "DATE_TO_TS_UTC": "1766385000",
                    "DT_SKIP_TIME": "N",
                    "DT_LENGTH": 900,
                    "EVENT_TYPE": None,
                    "CREATED_BY": "17890",
                    "DATE_CREATE": "20/05/2025 21:51:00",
                    "TIMESTAMP_X": "16/09/2025 04:48:24",
                    "DESCRIPTION": "",
                    "DT_FROM": None,
                    "DT_TO": None,
                    "PRIVATE_EVENT": "",
                    "ACCESSIBILITY": "busy",
                    "IMPORTANCE": "normal",
                    "IS_MEETING": True,
                    "MEETING_STATUS": "Y",
                    "MEETING_HOST": "1127",
                    "MEETING": {
                        "NOTIFY": True,
                        "MEETING_CREATOR": 1127,
                        "REINVITE": False,
                        "ALLOW_INVITE": False,
                        "HIDE_GUESTS": True,
                        "HOST_NAME": "Daimer Garcia",
                        "LANGUAGE_ID": "la",
                        "MAIL_FROM": "",
                        "CHAT_ID": 0
                    },
                    "LOCATION": "",
                    "REMIND": [
                        {
                            "type": "min",
                            "count": 0
                        },
                        {
                            "type": "min",
                            "count": 5
                        }
                    ],
                    "COLOR": "",
                    "TEXT_COLOR": "",
                    "RRULE": {
                        "FREQ": "WEEKLY",
                        "COUNT": 32,
                        "INTERVAL": 1,
                        "BYDAY": {
                            "MO": "MO"
                        },
                        "UNTIL": "01/01/2038",
                        "~UNTIL": "",
                        "UNTIL_TS": 2145916800
                    },
                    "EXDATE": "15/09/2025;09/06/2025;23/06/2025;07/07/2025",
                    "DAV_XML_ID": "20250519T140000Z-82a9304c457f248914dff05e6e974c94@avanzarsoluciones.bitrix24.es",
                    "G_EVENT_ID": "",
                    "DAV_EXCH_LABEL": "",
                    "CAL_DAV_LABEL": "",
                    "VERSION": "20",
                    "ATTENDEES_CODES": [
                        "U1127",
                        "U17890"
                    ],
                    "RECURRENCE_ID": None,
                    "RELATIONS": "",
                    "SECTION_ID": "6884",
                    "SYNC_STATUS": None,
                    "UF_CRM_CAL_EVENT": False,
                    "UF_WEBDAV_CAL_EVENT": False,
                    "SECTION_DAV_XML_ID": None,
                    "DATE_FROM_FORMATTED": "Mon Sep 22 2025 09:00:00",
                    "DATE_TO_FORMATTED": "Mon Sep 22 2025 09:15:00",
                    "IS_DAYLIGHT_SAVING_TZ": "N",
                    "SECT_ID": "6884",
                    "OPTIONS": None,
                    "ATTENDEE_LIST": [
                        {
                            "id": 1127,
                            "entryId": "914266",
                            "status": "H"
                        },
                        {
                            "id": 17890,
                            "entryId": "914272",
                            "status": "Y"
                        }
                    ],
                    "COLLAB_ID": None,
                    "~RRULE_DESCRIPTION": "semanalmente: Lun, desde 19/05/2025, 32 tiempo(s)",
                    "attendeesEntityList": [
                        {
                            "entityId": "user",
                            "id": 1127
                        },
                        {
                            "entityId": "user",
                            "id": 17890
                        }
                    ],
                    "~DATE_FROM": "19/05/2025 09:00:00",
                    "~DATE_TO": "19/05/2025 09:15:00",
                    "RINDEX": 1,
                    "~USER_OFFSET_FROM": 0,
                    "~USER_OFFSET_TO": 0
                }
            ],
            "time": {
                "start": 1758314944.790063,
                "finish": 1758314944.834991,
                "duration": 0.04492807388305664,
                "processing": 0.019826173782348633,
                "date_start": "2025-09-19T23:49:04+03:00",
                "date_finish": "2025-09-19T23:49:04+03:00",
                "operating_reset_at": 1758315544,
                "operating": 0
            }
        },
        "headers": {
            "server": "nginx",
            "date": "Fri, 19 Sep 2025 20:49:04 GMT",
            "content-type": "application/json; charset=utf-8",
            "transfer-encoding": "chunked",
            "connection": "close",
            "p3p": "policyref=\"/bitrix/p3p.xml\", CP=\"NON DSP COR CUR ADM DEV PSA PSD OUR UNR BUS UNI COM NAV INT DEM STA\"",
            "x-powered-cms": "Bitrix Site Manager (bc2cad9153cb418bb2dfd5602c3c3754)",
            "expires": "Thu, 19 Nov 1981 08:52:00 GMT",
            "cache-control": "no-store, no-cache, must-revalidate",
            "pragma": "no-cache",
            "set-cookie": [
                "qmb=0.; path=/"
            ],
            "x-bitrix24-date": "1584139988",
            "x-bitrix24-user": "0.",
            "access-control-allow-origin": "*",
            "access-control-allow-headers": "origin, content-type, accept",
            "x-content-type-options": "nosniff, nosniff",
            "x-bitrix-rest-application": "local.685d5063933614.00854686",
            "x-bitrix-rest-time": "0.0198261738",
            "x-bitrix-rest-user-time": "0.0092240000",
            "x-bitrix-rest-system-time": "0.0048570000",
            "x-frame-options": "SAMEORIGIN",
            "strict-transport-security": "max-age=31536000; includeSubdomains",
            "server-timing": "t1;dur=0.180, t2;dur=0.179, t3;dur=0.000, tc1;dur=117500, tc2;dur=18750, tc3;dur=20",
            "x-bitrix-ri": "b6be4e95e4acf11fea4078e3d6598581",
            "x-bitrix-lb": "lb-sa"
        },
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
            "dias_habiles" : ["Lunes", "Miercoles", "Viernes"],
            "horario" : {
                "desde": "09:00",
                "hasta": "17:00"
            },
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
