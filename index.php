<?php
// CORS
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");
header("Content-Type: application/json");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// v.9.4 — Acepta payload general (citas, filtro y calendar Bitrix). Cantidad_dias es global y se aplica antes de dias_habiles.

$body = file_get_contents("php://input");
if (!$body) {
    http_response_code(400); // sigue siendo error del cliente
    echo json_encode(["error" => "No se recibió ningún cuerpo en la solicitud"]);
    exit;
}

// Intento 1: JSON crudo
$data = json_decode($body, true);

// Intento 2: si no es JSON, probar como form-urlencoded (payload=..., data=..., json=...)
if ($data === null && json_last_error() !== JSON_ERROR_NONE) {
    $form = [];
    parse_str($body, $form);
    $candidate = null;
    foreach (["payload", "data", "json"] as $k) {
        if (isset($form[$k]) && is_string($form[$k])) {
            $candidate = $form[$k];
            break;
        }
    }
    if ($candidate !== null) {
        $data2 = json_decode($candidate, true);
        if ($data2 !== null || json_last_error() === JSON_ERROR_NONE) {
            $data = $data2;
        }
    }
}

if ($data === null && json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(400);
    echo json_encode([
        "error" => "Cuerpo no válido: se espera JSON crudo o form-urlencoded con 'payload'|'data'|'json'",
    ]);
    exit;
}

// Puede venir 'citas', 'filtro', 'calendar', 'resultado',
// o incluso un arreglo de eventos (result) o arreglo Bitrix.
// Pasamos el payload completo a Python para normalizar.
$payload_json = json_encode($data);
$escaped_payload = escapeshellarg($payload_json);

// Ejecutar el script de Python
$cmd = "python3 main.py $escaped_payload 2>&1";
exec($cmd, $output, $status);

if ($status !== 0) {
    http_response_code(500);
    echo json_encode([
        "error" => "Error al ejecutar el script Python",
        "detail" => implode("\n", $output),
        "code" => 500
    ]);
    exit;
}

echo implode("\n", $output);
