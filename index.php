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

// v.7

$body = file_get_contents("php://input");
if (!$body) {
    http_response_code(400); // sigue siendo error del cliente
    echo json_encode(["error" => "No se recibió ningún cuerpo en la solicitud"]);
    exit;
}

$data = json_decode($body, true);

// Validar estructura de "citas"
if (
    !$data || 
    !isset($data['citas']) || 
    !is_array($data['citas']) ||   // 👈 fuerza a que sea array/obj
    !isset($data['citas']['result']) || 
    !is_array($data['citas']['result'])
) {
    http_response_code(500); // lo tratamos como error del servidor
    echo json_encode(["error" => "Estructura de JSON invalida"]);
    exit;
}

$citas_json = json_encode($data['citas']);
$escaped_citas = escapeshellarg($citas_json);

// Ejecutar el script de Python
$cmd = "python3 main.py $escaped_citas 2>&1";
exec($cmd, $output, $status);

if ($status !== 0) {
    http_response_code(500);
    echo json_encode([
        "error" => "Error al ejecutar el script Python",
        "detail" => implode("\n", $output),
        "code" => 502
    ]);
    exit;
}

echo implode("\n", $output);
