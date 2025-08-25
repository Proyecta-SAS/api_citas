<?php
header("Content-Type: application/json");

// V.2

$body = file_get_contents("php://input");

if (!$body) {
    echo json_encode(["error" => "No se recibió ningún cuerpo en la solicitud" . $body]);
    exit;
}

$data = json_decode($body, true);
if (!$data || !isset($data['citas'])) {
    echo json_encode(["error" => "Se requiere el campo 'citas'" . $body]);
    exit;
}

$citas_json = json_encode($data['citas']);
$escaped_citas = escapeshellarg($citas_json);

// Ejecutar el script de Python
$cmd = "python3 main.py $escaped_citas";
exec($cmd, $output, $status);

if ($status !== 0) {
    echo json_encode(["error" => "Error al ejecutar el script Python"]);
    exit;
}

echo implode("\n", $output);
