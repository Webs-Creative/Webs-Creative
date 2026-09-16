<?php
declare(strict_types=1);

function wc_db(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        $dataDir = __DIR__ . '/../data';
        if (!is_dir($dataDir)) {
            mkdir($dataDir, 0775, true);
        }
        $isNew = !file_exists($dataDir . '/sorteo.sqlite');
        $pdo = new PDO('sqlite:' . $dataDir . '/sorteo.sqlite');
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->exec('PRAGMA journal_mode = WAL');
        $pdo->exec('CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subtitle TEXT NOT NULL,
            prizes_json TEXT NOT NULL,
            deadline TEXT NOT NULL,
            draw_date TEXT NOT NULL,
            draw_done INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )');
        $pdo->exec('CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            email_norm TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            created_at TEXT NOT NULL,
            contacted INTEGER NOT NULL DEFAULT 0,
            redeemed INTEGER NOT NULL DEFAULT 0,
            winner_index INTEGER,
            UNIQUE (campaign_id, email_norm)
        )');
        $pdo->exec('CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )');

        if ($isNew) {
            wc_seed_default_campaign($pdo);
        }
    }
    return $pdo;
}

function wc_seed_default_campaign(PDO $pdo): void
{
    $prizes = json_encode([
        ['title' => '30%', 'description' => 'De descuento para tu web, tu software de facturación o tu app móvil'],
        ['title' => '50%', 'description' => 'De descuento para tu web, tu software de facturación o tu app móvil'],
        ['title' => '70%', 'description' => 'De descuento para tu web, tu software de facturación o tu app móvil'],
    ], JSON_UNESCAPED_UNICODE);

    $stmt = $pdo->prepare(
        'INSERT INTO campaigns (name, subtitle, prizes_json, deadline, draw_date, draw_done, active, created_at)
         VALUES (:name, :subtitle, :prizes, :deadline, :draw_date, 0, 1, :created_at)'
    );
    $stmt->execute([
        'name' => 'Sorteamos hasta un 70% de descuento entre nuestros clientes',
        'subtitle' => 'Como agradecimiento por confiar en nosotros, sorteamos 3 cupones de descuento entre todos nuestros clientes: 30%, 50% y 70% para tu próxima web, tu software de facturación a medida o tu app móvil. Inscribirte lleva menos de un minuto.',
        'prizes' => $prizes,
        'deadline' => '2026-10-15',
        'draw_date' => '2026-10-20',
        'created_at' => date('c'),
    ]);
}

function wc_setting(string $key, ?string $default = null): ?string
{
    $stmt = wc_db()->prepare('SELECT value FROM settings WHERE key = ?');
    $stmt->execute([$key]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    return $row ? $row['value'] : $default;
}

function wc_set_setting(string $key, string $value): void
{
    $stmt = wc_db()->prepare(
        'INSERT INTO settings (key, value) VALUES (:k, :v)
         ON CONFLICT(key) DO UPDATE SET value = excluded.value'
    );
    $stmt->execute(['k' => $key, 'v' => $value]);
}

function wc_active_campaign(): ?array
{
    $row = wc_db()->query('SELECT * FROM campaigns WHERE active = 1 ORDER BY id DESC LIMIT 1')->fetch(PDO::FETCH_ASSOC);
    return $row ?: null;
}

function wc_campaign(int $id): ?array
{
    $stmt = wc_db()->prepare('SELECT * FROM campaigns WHERE id = ?');
    $stmt->execute([$id]);
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    return $row ?: null;
}

function wc_all_campaigns(): array
{
    return wc_db()->query('SELECT * FROM campaigns ORDER BY id DESC')->fetchAll(PDO::FETCH_ASSOC);
}

function wc_campaign_prizes(array $campaign): array
{
    $prizes = json_decode($campaign['prizes_json'], true);
    return is_array($prizes) ? $prizes : [];
}
