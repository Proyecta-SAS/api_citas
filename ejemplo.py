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
                    "ID": "1026440",
                    "PARENT_ID": "1026440",
                    "ACTIVE": "Y",
                    "DELETED": "N",
                    "CAL_TYPE": "user",
                    "OWNER_ID": "17890",
                    "NAME": "llamada a Juan Aldana (Prueba)",
                    "DATE_FROM": "27/09/2025 09:20:00",
                    "DATE_TO": "27/09/2025 09:30:00",
                    "ORIGINAL_DATE_FROM": "null",
                    "TZ_FROM": "America/Atikokan",
                    "TZ_TO": "America/Atikokan",
                    "TZ_OFFSET_FROM": "-18000",
                    "TZ_OFFSET_TO": "-18000",
                    "DATE_FROM_TS_UTC": "1758972000",
                    "DATE_TO_TS_UTC": "1758972600",
                    "DT_SKIP_TIME": "N",
                    "DT_LENGTH": 600,
                    "EVENT_TYPE": "null",
                    "CREATED_BY": "16448",
                    "DATE_CREATE": "25/09/2025 00:55:25",
                    "TIMESTAMP_X": "25/09/2025 00:55:25",
                    "DESCRIPTION": "El cliente Juan Aldana (Prueba) agendó esta llamada para obtener la información necesaria sobre nuestro proceso.",
                    "DT_FROM": "null",
                    "DT_TO": "null",
                    "PRIVATE_EVENT": "",
                    "ACCESSIBILITY": "busy",
                    "IMPORTANCE": "normal",
                    "IS_MEETING": False,
                    "MEETING_STATUS": "H",
                    "MEETING_HOST": "17890",
                    "MEETING": {
                        "NOTIFY": False,
                        "MEETING_CREATOR": 17890,
                        "REINVITE": False,
                        "ALLOW_INVITE": False,
                        "HIDE_GUESTS": False,
                        "HOST_NAME": "Alba Katterine Rincon Rodriguez",
                        "LANGUAGE_ID": "la",
                        "MAIL_FROM": "servicioalcliente1@impulsepbs.com"
                    },
                    "LOCATION": "",
                    "REMIND": [],
                    "COLOR": "",
                    "TEXT_COLOR": "",
                    "RRULE": "",
                    "EXDATE": "",
                    "DAV_XML_ID": "20250927T142000Z-ee8c7859dba8d05fd40369e9a7f3c0cf@avanzarsoluciones.bitrix24.es",
                    "G_EVENT_ID": "",
                    "DAV_EXCH_LABEL": "",
                    "CAL_DAV_LABEL": "",
                    "VERSION": "1",
                    "ATTENDEES_CODES": [
                        "U17890"
                    ],
                    "RECURRENCE_ID": "null",
                    "RELATIONS": "",
                    "SECTION_ID": "6884",
                    "SYNC_STATUS": "null",
                    "UF_CRM_CAL_EVENT": [
                        "D_840950"
                    ],
                    "UF_WEBDAV_CAL_EVENT": False,
                    "SECTION_DAV_XML_ID": "null",
                    "DATE_FROM_FORMATTED": "Sat Sep 27 2025 09:20:00",
                    "DATE_TO_FORMATTED": "Sat Sep 27 2025 09:30:00",
                    "IS_DAYLIGHT_SAVING_TZ": "N",
                    "SECT_ID": "6884",
                    "OPTIONS": "null",
                    "ATTENDEE_LIST": [
                        {
                            "id": 17890,
                            "entryId": "1026440",
                            "status": "H"
                        }
                    ],
                    "COLLAB_ID": "null",
                    "attendeesEntityList": [
                        {
                            "entityId": "user",
                            "id": 17890
                        }
                    ],
                    "~USER_OFFSET_FROM": 0,
                    "~USER_OFFSET_TO": 0
                },
                {
                    "ID": "1028396",
                    "PARENT_ID": "1028394",
                    "ACTIVE": "Y",
                    "DELETED": "N",
                    "CAL_TYPE": "user",
                    "OWNER_ID": "17890",
                    "NAME": "Excelencia Katterine Rincón",
                    "DATE_FROM": "29/09/2025 08:20:00",
                    "DATE_TO": "29/09/2025 08:35:00",
                    "ORIGINAL_DATE_FROM": "29/09/2025 09:00:00",
                    "TZ_FROM": "America/Bogota",
                    "TZ_TO": "America/Bogota",
                    "TZ_OFFSET_FROM": "-18000",
                    "TZ_OFFSET_TO": "-18000",
                    "DATE_FROM_TS_UTC": "1759141200",
                    "DATE_TO_TS_UTC": "1759142100",
                    "DT_SKIP_TIME": "N",
                    "DT_LENGTH": 900,
                    "EVENT_TYPE": "null",
                    "CREATED_BY": "17890",
                    "DATE_CREATE": "20/05/2025 21:51:00",
                    "TIMESTAMP_X": "26/09/2025 19:47:52",
                    "DESCRIPTION": "",
                    "DT_FROM": "null",
                    "DT_TO": "null",
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
                    "RRULE": "",
                    "EXDATE": "",
                    "DAV_XML_ID": "20250519T140000Z-82a9304c457f248914dff05e6e974c94@avanzarsoluciones.bitrix24.es",
                    "G_EVENT_ID": "",
                    "DAV_EXCH_LABEL": "",
                    "CAL_DAV_LABEL": "",
                    "VERSION": "23",
                    "ATTENDEES_CODES": [
                        "U1127",
                        "U17890"
                    ],
                    "RECURRENCE_ID": 914266,
                    "RELATIONS": {
                        "COMMENT_XML_ID": "EVENT_914266_29/09/2025"
                    },
                    "SECTION_ID": "6884",
                    "SYNC_STATUS": "null",
                    "UF_CRM_CAL_EVENT": False,
                    "UF_WEBDAV_CAL_EVENT": False,
                    "SECTION_DAV_XML_ID": "null",
                    "DATE_FROM_FORMATTED": "Mon Sep 29 2025 08:20:00",
                    "DATE_TO_FORMATTED": "Mon Sep 29 2025 08:35:00",
                    "IS_DAYLIGHT_SAVING_TZ": "N",
                    "SECT_ID": "6884",
                    "OPTIONS": "null",
                    "ATTENDEE_LIST": [
                        {
                            "id": 1127,
                            "entryId": "1028394",
                            "status": "H"
                        },
                        {
                            "id": 17890,
                            "entryId": "1028396",
                            "status": "Y"
                        }
                    ],
                    "COLLAB_ID": "null",
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
                    "~USER_OFFSET_FROM": 0,
                    "~USER_OFFSET_TO": 0
                },
                {
                    "ID": "1022964",
                    "PARENT_ID": "1022960",
                    "ACTIVE": "Y",
                    "DELETED": "N",
                    "CAL_TYPE": "user",
                    "OWNER_ID": "17890",
                    "NAME": "LECCIONES APRENDIDAS AL JUAN PABLO DIAZ",
                    "DATE_FROM": "02/10/2025 15:00:00",
                    "DATE_TO": "02/10/2025 16:00:00",
                    "ORIGINAL_DATE_FROM": "null",
                    "TZ_FROM": "America/Bogota",
                    "TZ_TO": "America/Bogota",
                    "TZ_OFFSET_FROM": "-18000",
                    "TZ_OFFSET_TO": "-18000",
                    "DATE_FROM_TS_UTC": "1759424400",
                    "DATE_TO_TS_UTC": "1759428000",
                    "DT_SKIP_TIME": "N",
                    "DT_LENGTH": 3600,
                    "EVENT_TYPE": "null",
                    "CREATED_BY": "17890",
                    "DATE_CREATE": "22/09/2025 20:44:20",
                    "TIMESTAMP_X": "22/09/2025 20:44:20",
                    "DESCRIPTION": "",
                    "DT_FROM": "null",
                    "DT_TO": "null",
                    "PRIVATE_EVENT": "",
                    "ACCESSIBILITY": "busy",
                    "IMPORTANCE": "normal",
                    "IS_MEETING": True,
                    "MEETING_STATUS": "Y",
                    "MEETING_HOST": "16004",
                    "MEETING": {
                        "NOTIFY": True,
                        "MEETING_CREATOR": 16004,
                        "REINVITE": False,
                        "ALLOW_INVITE": False,
                        "HIDE_GUESTS": True,
                        "HOST_NAME": "Ingrid Paola Julio Lascarro",
                        "LANGUAGE_ID": "null",
                        "MAIL_FROM": False,
                        "CHAT_ID": 0
                    },
                    "LOCATION": "",
                    "REMIND": [
                        {
                            "type": "min",
                            "count": 15
                        }
                    ],
                    "COLOR": "#00afc7",
                    "TEXT_COLOR": "",
                    "RRULE": "",
                    "EXDATE": "",
                    "DAV_XML_ID": "20251002T200000Z-3e0685ecfef9674e60cc0c84b5355631@avanzarsoluciones.bitrix24.es",
                    "G_EVENT_ID": "",
                    "DAV_EXCH_LABEL": "",
                    "CAL_DAV_LABEL": "",
                    "VERSION": "1",
                    "ATTENDEES_CODES": [
                        "U16004",
                        "U1127",
                        "U17890"
                    ],
                    "RECURRENCE_ID": "null",
                    "RELATIONS": "",
                    "SECTION_ID": "6884",
                    "SYNC_STATUS": "null",
                    "UF_CRM_CAL_EVENT": False,
                    "UF_WEBDAV_CAL_EVENT": False,
                    "SECTION_DAV_XML_ID": "null",
                    "DATE_FROM_FORMATTED": "Thu Oct 02 2025 15:00:00",
                    "DATE_TO_FORMATTED": "Thu Oct 02 2025 16:00:00",
                    "IS_DAYLIGHT_SAVING_TZ": "N",
                    "SECT_ID": "6884",
                    "OPTIONS": "null",
                    "ATTENDEE_LIST": [
                        {
                            "id": 16004,
                            "entryId": "1022960",
                            "status": "H"
                        },
                        {
                            "id": 1127,
                            "entryId": "1022962",
                            "status": "Y"
                        },
                        {
                            "id": 17890,
                            "entryId": "1022964",
                            "status": "Y"
                        }
                    ],
                    "COLLAB_ID": "null",
                    "attendeesEntityList": [
                        {
                            "entityId": "user",
                            "id": 16004
                        },
                        {
                            "entityId": "user",
                            "id": 1127
                        },
                        {
                            "entityId": "user",
                            "id": 17890
                        }
                    ],
                    "~USER_OFFSET_FROM": 0,
                    "~USER_OFFSET_TO": 0
                }
            ],
            "time": {
                "start": 1758920424,
                "finish": 1758920424.193102,
                "duration": 0.1931018829345703,
                "processing": 0,
                "date_start": "2025-09-27T00:00:24+03:00",
                "date_finish": "2025-09-27T00:00:24+03:00",
                "operating_reset_at": 1758921024,
                "operating": 0
            }
        },
        "headers": {
            "server": "nginx",
            "date": "Fri, 26 Sep 2025 21:00:24 GMT",
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
            "x-bitrix-rest-time": "0.0000000000",
            "x-bitrix-rest-user-time": "0.0126380000",
            "x-bitrix-rest-system-time": "0.0041390000",
            "x-frame-options": "SAMEORIGIN",
            "strict-transport-security": "max-age=31536000; includeSubdomains",
            "server-timing": "t1;dur=0.264, t2;dur=0.264, t3;dur=0.000, tc1;dur=112000, tc2;dur=17723, tc3;dur=20",
            "x-bitrix-ri": "ecd91e03dedd97b763a0f87ce6b51af7",
            "x-bitrix-lb": "lb-sa-2"
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
        "minutos": 10,
        "Cantidad_dias": 3,
        "filtro": {
            "horario" : {
                "desde": "09:00",
                "hasta": "17:00"
            },
            "jornada": 1
        },
        # Se envía el calendario crudo como lo recibiste
        "calendar": calendar,

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
