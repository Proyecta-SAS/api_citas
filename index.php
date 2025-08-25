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

// v.5

$body = file_get_contents("php://input");



if ($body === false || $body === '') {
    echo json_encode(["error" => "No se recibió ningún cuerpo en la solicitud"]);
    exit;
}

$data = json_decode($body, true);
if (!$data || !isset($data['citas'])) {
    echo json_encode(["error" => "Se requiere el campo 'citas'"]);
    exit;
}

$citas_json = json_encode($data['citas'], JSON_UNESCAPED_UNICODE);
$escaped_citas = escapeshellarg($citas_json);


$cmd = "python3 main.py $escaped_citas";
exec($cmd, $output, $status);

if ($status !== 0) {
    echo json_encode(["error" => "Error al ejecutar el script Python"]);
    exit;
}

echo implode("\n", $output);
