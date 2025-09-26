#!/usr/bin/env bash
set -euo pipefail

# Base URL del endpoint. Puedes sobreescribir con: BASE_URL=https://tu-api/ ./curl_examples.sh
BASE_URL="${BASE_URL:-http://127.0.0.1:8000/}"

echo "Usando BASE_URL=$BASE_URL"

echo "\n1) JSON crudo: Array Bitrix"
curl -sS -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '[{ "body": { "result": [ { "DATE_FROM": "27/09/2025 09:20:00", "DATE_TO": "27/09/2025 09:30:00" } ] }, "statusCode": 200 }]'

echo "\n2) JSON crudo: Objeto con calendar + filtros"
curl -sS -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "calendar": [{ "body": { "result": [ { "DATE_FROM": "29/09/2025 08:20:00", "DATE_TO": "29/09/2025 08:35:00" } ] } }],
    "minutos": 30,
    "Cantidad_dias": 5,
    "filtro": {
      "dias_habiles": ["Lunes", "Miercoles", "Viernes"],
      "jornada": 1
    }
  }'

echo "\n3) JSON crudo: Objeto con resultado"
curl -sS -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "resultado": { "DATE FROM": "09/09/2025 09:00:00", "DATE TO": "09/09/2025 17:00:00" },
    "minutos": 20,
    "Cantidad_dias": 7
  }'

echo "\n4) Form-urlencoded: payload con JSON"
curl -sS -X POST "$BASE_URL" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode 'payload={
    "resultado": { "DATE FROM": "09/09/2025 09:00:00", "DATE TO": "09/09/2025 17:00:00" },
    "minutos": 30,
    "Cantidad_dias": 5
  }'

echo "\nListo. Cambia BASE_URL si quieres apuntar a otra instancia."

