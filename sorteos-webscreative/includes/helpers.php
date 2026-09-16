<?php
declare(strict_types=1);

function h(?string $s): string
{
    return htmlspecialchars($s ?? '', ENT_QUOTES, 'UTF-8');
}

function wc_csrf_token(): string
{
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
    return $_SESSION['csrf'];
}

function wc_csrf_check(): bool
{
    return isset($_POST['csrf'], $_SESSION['csrf'])
        && is_string($_POST['csrf'])
        && hash_equals($_SESSION['csrf'], $_POST['csrf']);
}

function wc_fmt_date_long(string $ymd): string
{
    static $months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
    $ts = strtotime($ymd);
    if ($ts === false) {
        return $ymd;
    }
    return (int)date('j', $ts) . ' de ' . $months[(int)date('n', $ts) - 1] . ' de ' . date('Y', $ts);
}

function wc_fmt_datetime_short(string $iso): string
{
    $ts = strtotime($iso);
    return $ts === false ? $iso : date('d/m/Y H:i', $ts);
}

function wc_days_left(string $ymd): int
{
    $target = strtotime($ymd . ' 23:59:00');
    if ($target === false) {
        return 0;
    }
    return (int)ceil(($target - time()) / 86400);
}

function wc_first_name_last_initial(string $name): string
{
    $parts = preg_split('/\s+/', trim($name)) ?: [];
    if (empty($parts) || $parts[0] === '') {
        return 'Participante';
    }
    $first = $parts[0];
    $last = count($parts) > 1 ? mb_strtoupper(mb_substr(end($parts), 0, 1)) . '.' : '';
    return trim($first . ' ' . $last);
}
