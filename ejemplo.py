#!/usr/bin/env python3
import json
from urllib import request, error

# Cambia esta URL si tu endpoint es diferente
BASE_URL = "https://citas.proyectasolutions.co/"

def ensure_trailing_slash(url: str) -> str:
    return url if url.endswith("/") else url + "/"

result = [{},{}]
def main():
  url = ensure_trailing_slash(BASE_URL)
  
  payload = {
    "citas": {
      "result": [
        { "DATE_FROM": "26/08/2025 09:00:00", "DATE_TO": "26/08/2025 10:00:00" },
        { "DATE_FROM": "27/08/2025 14:30:00", "DATE_TO": "27/08/2025 16:00:00" }
      ]
    }
  }
  
  # payload = {
  #   "citas": "holas"
  # }
  
  data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
  headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
  }
  
  req = request.Request(url, data=data, headers=headers, method="POST")
  
  try:
      with request.urlopen(req, timeout=30) as resp:
          body = resp.read().decode("utf-8", errors="replace")
          print(f"[POST] {url} -> {resp.status}")
          print(body)
  except error.HTTPError as e:
      print(f"[POST] {url} -> HTTP {e.code}")
      print(e.read().decode("utf-8", errors="replace"))
  except Exception as e:
      print(f"[POST] {url} -> ERROR: {e}")

if __name__ == "__main__":
    main()
