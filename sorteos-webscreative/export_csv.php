<?php
declare(strict_types=1);
session_start();
require __DIR__ . '/includes/db.php';
require __DIR__ . '/includes/helpers.php';

if (empty($_SESSION['wc_admin'])) {
    http_response_code(403);
    echo 'Acceso no autorizado. Inicia sesión en el panel primero.';
    exit;
}

$campaignId = (int)($_GET['campaign'] ?? 0);
$campaign = $campaignId > 0 ? wc_campaign($campaignId) : null;
if (!$campaign) {
    http_response_code(404);
    echo 'Campaña no encontrada.';
    exit;
}

$prizes = wc_campaign_prizes($campaign);
$stmt = wc_db()->prepare('SELECT * FROM entries WHERE campaign_id = ? ORDER BY created_at ASC');
$stmt->execute([$campaignId]);
$entries = $stmt->fetchAll(PDO::FETCH_ASSOC);

$safeName = preg_replace('/[^a-z0-9]+/i', '-', $campaign['name']);
$filename = 'sorteo-' . trim(mb_strtolower($safeName), '-') . '.csv';

header('Content-Type: text/csv; charset=UTF-8');
header('Content-Disposition: attachment; filename="' . $filename . '"');

$out = fopen('php://output', 'w');
fwrite($out, "\xEF\xBB\xBF"); // UTF-8 BOM so Excel opens accents correctly
fputcsv($out, ['Nombre', 'Correo', 'Teléfono', 'Empresa', 'Fecha inscripción', 'Premio ganado', 'Contactado', 'Canjeado'], ';');

foreach ($entries as $e) {
    $prizeWon = '';
    if ($e['winner_index'] !== null) {
        $idx = (int)$e['winner_index'];
        $prizeWon = $prizes[$idx]['title'] ?? ('Premio ' . ($idx + 1));
    }
    fputcsv($out, [
        $e['name'],
        $e['email'],
        $e['phone'] ?? '',
        $e['company'] ?? '',
        wc_fmt_datetime_short($e['created_at']),
        $prizeWon,
        $e['contacted'] ? 'sí' : 'no',
        $e['redeemed'] ? 'sí' : 'no',
    ], ';');
}
fclose($out);
