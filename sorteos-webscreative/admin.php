<?php
declare(strict_types=1);
session_start();
require __DIR__ . '/includes/db.php';
require __DIR__ . '/includes/helpers.php';

$passcodeHash = wc_setting('passcode_hash');
$isAdmin = !empty($_SESSION['wc_admin']);
$flash = null;
$error = null;

if (isset($_GET['logout'])) {
    unset($_SESSION['wc_admin']);
    header('Location: admin.php');
    exit;
}

// ---- first run: no passcode configured yet ----
if ($passcodeHash === null && $_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'setup') {
    if (!wc_csrf_check()) {
        $error = 'Tu sesión ha caducado. Recarga la página e inténtalo de nuevo.';
    } else {
        $p1 = (string)($_POST['passcode'] ?? '');
        $p2 = (string)($_POST['passcode2'] ?? '');
        if (strlen($p1) < 8) {
            $error = 'El código de acceso debe tener al menos 8 caracteres.';
        } elseif ($p1 !== $p2) {
            $error = 'Los dos códigos no coinciden.';
        } else {
            wc_set_setting('passcode_hash', password_hash($p1, PASSWORD_DEFAULT));
            $_SESSION['wc_admin'] = true;
            header('Location: admin.php');
            exit;
        }
    }
}

// ---- login ----
if ($passcodeHash !== null && !$isAdmin && $_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'login') {
    if (!wc_csrf_check()) {
        $error = 'Tu sesión ha caducado. Recarga la página e inténtalo de nuevo.';
    } elseif (password_verify((string)($_POST['passcode'] ?? ''), $passcodeHash)) {
        $_SESSION['wc_admin'] = true;
        header('Location: admin.php');
        exit;
    } else {
        $error = 'Código incorrecto.';
    }
}

$isAdmin = !empty($_SESSION['wc_admin']);

function wc_parse_prizes(string $text): array
{
    $prizes = [];
    foreach (preg_split('/\r?\n/', trim($text)) as $line) {
        $line = trim($line);
        if ($line === '') {
            continue;
        }
        $parts = preg_split('/\s*\|\s*/', $line, 2);
        $prizes[] = [
            'title' => $parts[0],
            'description' => $parts[1] ?? '',
        ];
    }
    return $prizes;
}

// ---- everything below requires an authenticated admin ----
$selectedCampaignId = isset($_GET['campaign']) ? (int)$_GET['campaign'] : null;

if ($isAdmin && $_SERVER['REQUEST_METHOD'] === 'POST' && wc_csrf_check()) {
    $action = $_POST['action'] ?? '';
    $cid = (int)($_POST['campaign_id'] ?? 0);

    if ($action === 'create_campaign') {
        $name = trim((string)($_POST['name'] ?? ''));
        $subtitle = trim((string)($_POST['subtitle'] ?? ''));
        $deadline = (string)($_POST['deadline'] ?? '');
        $drawDate = (string)($_POST['draw_date'] ?? '');
        $prizes = wc_parse_prizes((string)($_POST['prizes'] ?? ''));
        $activateNow = isset($_POST['activate_now']);

        if ($name === '' || $deadline === '' || $drawDate === '' || count($prizes) < 1) {
            $error = 'Rellena el nombre, las dos fechas y al menos un premio.';
        } else {
            $pdo = wc_db();
            if ($activateNow) {
                $pdo->exec('UPDATE campaigns SET active = 0');
            }
            $stmt = $pdo->prepare(
                'INSERT INTO campaigns (name, subtitle, prizes_json, deadline, draw_date, draw_done, active, created_at)
                 VALUES (:name, :subtitle, :prizes, :deadline, :draw_date, 0, :active, :created_at)'
            );
            $stmt->execute([
                'name' => $name,
                'subtitle' => $subtitle,
                'prizes' => json_encode($prizes, JSON_UNESCAPED_UNICODE),
                'deadline' => $deadline,
                'draw_date' => $drawDate,
                'active' => $activateNow ? 1 : 0,
                'created_at' => date('c'),
            ]);
            $selectedCampaignId = (int)$pdo->lastInsertId();
            $flash = 'Campaña creada' . ($activateNow ? ' y activada.' : '.');
        }
    } elseif ($action === 'activate_campaign' && $cid > 0) {
        $pdo = wc_db();
        $pdo->exec('UPDATE campaigns SET active = 0');
        $stmt = $pdo->prepare('UPDATE campaigns SET active = 1 WHERE id = ?');
        $stmt->execute([$cid]);
        $selectedCampaignId = $cid;
        $flash = 'Campaña activada. Ya es la que ven los clientes en la página pública.';
    } elseif ($action === 'delete_campaign' && $cid > 0) {
        $pdo = wc_db();
        $stmt = $pdo->prepare('DELETE FROM entries WHERE campaign_id = ?');
        $stmt->execute([$cid]);
        $stmt = $pdo->prepare('DELETE FROM campaigns WHERE id = ?');
        $stmt->execute([$cid]);
        $selectedCampaignId = null;
        $flash = 'Campaña eliminada.';
    } elseif ($action === 'save_settings' && $cid > 0) {
        $deadline = (string)($_POST['deadline'] ?? '');
        $drawDate = (string)($_POST['draw_date'] ?? '');
        $prizes = wc_parse_prizes((string)($_POST['prizes'] ?? ''));
        $stmt = wc_db()->prepare(
            'UPDATE campaigns SET deadline = ?, draw_date = ?, prizes_json = ? WHERE id = ?'
        );
        $stmt->execute([$deadline, $drawDate, json_encode($prizes, JSON_UNESCAPED_UNICODE), $cid]);
        $newPass = trim((string)($_POST['new_passcode'] ?? ''));
        if ($newPass !== '') {
            if (strlen($newPass) < 8) {
                $error = 'El nuevo código debe tener al menos 8 caracteres.';
            } else {
                wc_set_setting('passcode_hash', password_hash($newPass, PASSWORD_DEFAULT));
                $flash = 'Ajustes guardados. El código de acceso también se ha actualizado.';
            }
        } else {
            $flash = 'Ajustes guardados.';
        }
        $selectedCampaignId = $cid;
    } elseif ($action === 'toggle_contacted' || $action === 'toggle_redeemed') {
        $id = (int)($_POST['id'] ?? 0);
        $col = $action === 'toggle_contacted' ? 'contacted' : 'redeemed';
        $stmt = wc_db()->prepare("UPDATE entries SET $col = 1 - $col WHERE id = ?");
        $stmt->execute([$id]);
        $selectedCampaignId = $cid;
    } elseif ($action === 'delete_entry') {
        $id = (int)($_POST['id'] ?? 0);
        $stmt = wc_db()->prepare('DELETE FROM entries WHERE id = ?');
        $stmt->execute([$id]);
        $flash = 'Inscripción eliminada.';
        $selectedCampaignId = $cid;
    } elseif ($action === 'draw' && $cid > 0) {
        $stmt = wc_db()->prepare('SELECT id FROM entries WHERE campaign_id = ?');
        $stmt->execute([$cid]);
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $campaignForDraw = wc_campaign($cid);
        $prizeCount = $campaignForDraw ? count(wc_campaign_prizes($campaignForDraw)) : 0;
        if (count($rows) >= max($prizeCount, 1) && $prizeCount > 0) {
            $ids = array_column($rows, 'id');
            for ($i = count($ids) - 1; $i > 0; $i--) {
                $j = random_int(0, $i);
                [$ids[$i], $ids[$j]] = [$ids[$j], $ids[$i]];
            }
            $chosen = array_slice($ids, 0, $prizeCount);
            $pdo = wc_db();
            $reset = $pdo->prepare('UPDATE entries SET winner_index = NULL WHERE campaign_id = ?');
            $reset->execute([$cid]);
            $upd = $pdo->prepare('UPDATE entries SET winner_index = ? WHERE id = ?');
            foreach ($chosen as $i => $id) {
                $upd->execute([$i, $id]);
            }
            $markDone = $pdo->prepare('UPDATE campaigns SET draw_done = 1 WHERE id = ?');
            $markDone->execute([$cid]);
            $flash = 'Sorteo realizado.';
        }
        $selectedCampaignId = $cid;
    } elseif ($action === 'clear_all' && $cid > 0) {
        if (($_POST['confirm_text'] ?? '') === 'BORRAR') {
            $stmt = wc_db()->prepare('DELETE FROM entries WHERE campaign_id = ?');
            $stmt->execute([$cid]);
            $reset = wc_db()->prepare('UPDATE campaigns SET draw_done = 0 WHERE id = ?');
            $reset->execute([$cid]);
            $flash = 'Se han eliminado todas las inscripciones de esta campaña.';
        } else {
            $error = 'Escribe BORRAR (en mayúsculas) para confirmar el vaciado.';
        }
        $selectedCampaignId = $cid;
    }
}

$csrf = wc_csrf_token();
$campaigns = $isAdmin ? wc_all_campaigns() : [];

if ($selectedCampaignId === null) {
    $active = wc_active_campaign();
    $selectedCampaignId = $active ? (int)$active['id'] : (isset($campaigns[0]) ? (int)$campaigns[0]['id'] : null);
}
$selected = $selectedCampaignId ? wc_campaign($selectedCampaignId) : null;

$entries = [];
if ($isAdmin && $selected) {
    $stmt = wc_db()->prepare('SELECT * FROM entries WHERE campaign_id = ? ORDER BY created_at ASC');
    $stmt->execute([$selected['id']]);
    $entries = $stmt->fetchAll(PDO::FETCH_ASSOC);
}
$prizes = $selected ? wc_campaign_prizes($selected) : [];
$winnersByIndex = [];
foreach ($entries as $e) {
    if ($e['winner_index'] !== null) {
        $winnersByIndex[(int)$e['winner_index']] = $e;
    }
}
$daysLeft = $selected ? wc_days_left($selected['deadline']) : 0;
$prizesTextDefault = $selected ? implode("\n", array_map(
    fn($p) => ($p['title'] ?? '') . ' | ' . ($p['description'] ?? ''),
    $prizes
)) : "30% | De descuento para tu web, tu software de facturación o tu app móvil\n50% | De descuento para tu web, tu software de facturación o tu app móvil\n70% | De descuento para tu web, tu software de facturación o tu app móvil";
?>
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Panel de gestión &middot; Sorteos Webs Creative</title>
<meta name="robots" content="noindex, nofollow">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Work+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <a class="brand" href="index.php"><span class="brand-mark">WC</span>Webs Creative</a>
  </div>

  <div class="section">
  <?php if ($passcodeHash === null): ?>

    <div class="card gate-card">
      <div class="kicker">Primer acceso</div>
      <h2 class="title">Configura el panel</h2>
      <p style="margin-top:8px;font-size:13.5px;color:var(--ink-2)">Elige el código de acceso que usará el equipo para gestionar los sorteos.</p>
      <?php if ($error): ?><div class="error-text"><?= h($error) ?></div><?php endif; ?>
      <form method="post" style="margin-top:18px;text-align:left">
        <input type="hidden" name="action" value="setup">
        <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
        <div class="field"><label for="p1">Código de acceso (mínimo 8 caracteres)</label><input id="p1" type="password" name="passcode" required minlength="8"></div>
        <div class="field" style="margin-top:12px"><label for="p2">Repite el código</label><input id="p2" type="password" name="passcode2" required minlength="8"></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary" style="width:100%">Crear acceso</button></div>
      </form>
    </div>

  <?php elseif (!$isAdmin): ?>

    <div class="card gate-card">
      <div class="kicker">Panel de gestión</div>
      <h2 class="title">Acceso del equipo</h2>
      <p style="margin-top:8px;font-size:13.5px;color:var(--ink-2)">Introduce el código de acceso para ver y gestionar los sorteos.</p>
      <?php if ($error): ?><div class="error-text"><?= h($error) ?></div><?php endif; ?>
      <form method="post" style="margin-top:18px;text-align:left">
        <input type="hidden" name="action" value="login">
        <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
        <div class="field"><label for="pass">Código de acceso</label><input id="pass" type="password" name="passcode" autocomplete="off" autofocus></div>
        <div class="form-actions"><button type="submit" class="btn btn-primary" style="width:100%">Entrar</button></div>
      </form>
    </div>

  <?php else: ?>

    <div class="admin-top">
      <div><div class="kicker">Panel de gestión</div><h2 class="title">Sorteos y campañas</h2></div>
      <a href="?logout=1" class="btn btn-ghost">Cerrar sesión de equipo</a>
    </div>

    <?php if ($flash): ?><div class="flash-ok"><?= h($flash) ?></div><?php endif; ?>
    <?php if ($error): ?><div class="error-text"><?= h($error) ?></div><?php endif; ?>

    <div class="card" style="margin-top:16px">
      <div class="kicker">Campañas</div>
      <?php if ($campaigns): ?>
        <div class="table-scroll">
          <table class="entries">
            <thead><tr><th>Nombre</th><th>Inscripción</th><th>Sorteo</th><th>Inscritos</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>
            <?php foreach ($campaigns as $c):
                $countStmt = wc_db()->prepare('SELECT COUNT(*) FROM entries WHERE campaign_id = ?');
                $countStmt->execute([$c['id']]);
                $n = (int)$countStmt->fetchColumn();
            ?>
              <tr<?= $selected && (int)$selected['id'] === (int)$c['id'] ? ' style="background:var(--surface-2)"' : '' ?>>
                <td class="name"><?= h($c['name']) ?></td>
                <td><?= h(wc_fmt_date_long($c['deadline'])) ?></td>
                <td><?= h(wc_fmt_date_long($c['draw_date'])) ?></td>
                <td><?= $n ?></td>
                <td>
                  <?php if ((int)$c['active'] === 1): ?><span class="badge badge-win">Activa</span><?php endif; ?>
                  <?php if ((int)$c['draw_done'] === 1): ?><span class="badge badge-redeemed">Sorteada</span><?php endif; ?>
                </td>
                <td>
                  <div class="row-actions">
                    <a href="?campaign=<?= (int)$c['id'] ?>"><button type="button">Gestionar</button></a>
                    <?php if ((int)$c['active'] !== 1): ?>
                      <form method="post"><input type="hidden" name="action" value="activate_campaign"><input type="hidden" name="csrf" value="<?= h($csrf) ?>"><input type="hidden" name="campaign_id" value="<?= (int)$c['id'] ?>"><button type="submit">Activar</button></form>
                    <?php endif; ?>
                    <form method="post" onsubmit="return confirm('¿Eliminar esta campaña y todas sus inscripciones?');"><input type="hidden" name="action" value="delete_campaign"><input type="hidden" name="csrf" value="<?= h($csrf) ?>"><input type="hidden" name="campaign_id" value="<?= (int)$c['id'] ?>"><button type="submit" style="color:var(--danger)">Eliminar</button></form>
                  </div>
                </td>
              </tr>
            <?php endforeach; ?>
            </tbody>
          </table>
        </div>
      <?php endif; ?>

      <div class="admin-divider"></div>
      <div class="kicker">Nueva campaña</div>
      <form method="post" style="margin-top:10px">
        <input type="hidden" name="action" value="create_campaign">
        <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
        <div class="form-grid">
          <div class="field full"><label for="nc-name">Nombre / titular</label><input id="nc-name" type="text" name="name" required placeholder="Ej. Sorteo de Navidad: 3 meses de mantenimiento gratis"></div>
          <div class="field full"><label for="nc-subtitle">Subtítulo (una o dos frases)</label><input id="nc-subtitle" type="text" name="subtitle" placeholder="Explica en una frase qué se sortea y entre quién"></div>
          <div class="field"><label for="nc-deadline">Fecha límite de inscripción</label><input id="nc-deadline" type="date" name="deadline" required></div>
          <div class="field"><label for="nc-draw">Fecha del sorteo</label><input id="nc-draw" type="date" name="draw_date" required></div>
          <div class="field full"><label for="nc-prizes">Premios (uno por línea, formato "Título | Descripción")</label>
            <textarea id="nc-prizes" name="prizes" rows="4" required style="border:1px solid var(--border);background:var(--bg);color:var(--ink);border-radius:12px;padding:12px 13px;font-size:14.5px;font-family:inherit;width:100%" placeholder="30% | De descuento en tu próxima web&#10;50% | De descuento en tu próxima web&#10;70% | De descuento en tu próxima web"></textarea>
          </div>
        </div>
        <div class="checkline"><input id="nc-activate" type="checkbox" name="activate_now"><label for="nc-activate">Activarla ya (sustituye a la campaña activa actual en la página pública)</label></div>
        <div class="form-actions"><button type="submit" class="btn btn-secondary">Crear campaña</button></div>
      </form>
    </div>

    <?php if ($selected): ?>
    <div class="card" style="margin-top:16px">
      <div class="admin-top">
        <div><div class="kicker">Gestionando</div><h2 class="title"><?= h($selected['name']) ?></h2></div>
      </div>

      <div class="stat-grid">
        <div class="stat"><div class="n"><?= count($entries) ?></div><div class="l">Inscritos</div></div>
        <div class="stat"><div class="n"><?= max($daysLeft, 0) ?></div><div class="l">Días restantes</div></div>
        <div class="stat"><div class="n"><?= (int)$selected['draw_done'] === 1 ? 'Sí' : 'No' ?></div><div class="l">Sorteo realizado</div></div>
      </div>

      <?php if ($winnersByIndex): ?>
        <div class="winners-callout">
          <h3>Ganadores del sorteo</h3>
          <ul>
            <?php foreach ($winnersByIndex as $idx => $e): ?>
              <li><strong><?= h($prizes[$idx]['title'] ?? ('Premio ' . ($idx + 1))) ?></strong> &mdash; <?= h($e['name']) ?> &middot; <?= h($e['email']) ?><?= $e['phone'] ? ' &middot; ' . h($e['phone']) : '' ?></li>
            <?php endforeach; ?>
          </ul>
        </div>
      <?php endif; ?>

      <div class="admin-divider"></div>
      <div class="kicker">Ajustes de esta campaña</div>
      <form method="post">
        <input type="hidden" name="action" value="save_settings">
        <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
        <input type="hidden" name="campaign_id" value="<?= (int)$selected['id'] ?>">
        <div class="settings-grid">
          <label class="field-inline">Fecha límite de inscripción<input type="date" name="deadline" value="<?= h($selected['deadline']) ?>"></label>
          <label class="field-inline">Fecha del sorteo<input type="date" name="draw_date" value="<?= h($selected['draw_date']) ?>"></label>
          <label class="field-inline">Nuevo código de acceso del equipo (opcional)<input type="password" name="new_passcode" minlength="8" placeholder="Dejar en blanco para no cambiarlo"></label>
        </div>
        <div class="field full" style="margin-top:14px"><label for="ec-prizes">Premios (uno por línea, formato "Título | Descripción")</label>
          <textarea id="ec-prizes" name="prizes" rows="4" style="border:1px solid var(--border);background:var(--bg);color:var(--ink);border-radius:12px;padding:12px 13px;font-size:14.5px;font-family:inherit;width:100%"><?= h($prizesTextDefault) ?></textarea>
        </div>
        <div class="admin-actions"><button type="submit" class="btn btn-secondary">Guardar ajustes</button></div>
      </form>

      <div class="admin-divider"></div>
      <div class="kicker">Inscritos (<?= count($entries) ?>)</div>
      <?php if ($entries): ?>
        <div class="table-scroll">
          <table class="entries">
            <thead><tr><th>#</th><th>Nombre</th><th>Correo</th><th>Teléfono</th><th>Empresa</th><th>Fecha</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>
            <?php foreach ($entries as $i => $e): $idx = $e['winner_index'] !== null ? (int)$e['winner_index'] : null; ?>
              <tr>
                <td><?= $i + 1 ?></td>
                <td class="name"><?= h($e['name']) ?></td>
                <td><?= h($e['email']) ?></td>
                <td><?= h($e['phone'] ?: '—') ?></td>
                <td><?= h($e['company'] ?: '—') ?></td>
                <td><?= h(wc_fmt_datetime_short($e['created_at'])) ?></td>
                <td>
                  <?php if ($idx !== null): ?><span class="badge badge-win">Ganador &middot; <?= h($prizes[$idx]['title'] ?? ('Premio ' . ($idx + 1))) ?></span><?php endif; ?>
                  <?php if ($e['contacted']): ?><span class="badge badge-contacted">Contactado</span><?php endif; ?>
                  <?php if ($e['redeemed']): ?><span class="badge badge-redeemed">Canjeado</span><?php endif; ?>
                  <?php if ($idx === null && !$e['contacted'] && !$e['redeemed']): ?><span style="color:var(--muted)">—</span><?php endif; ?>
                </td>
                <td>
                  <div class="row-actions">
                    <form method="post"><input type="hidden" name="action" value="toggle_contacted"><input type="hidden" name="csrf" value="<?= h($csrf) ?>"><input type="hidden" name="id" value="<?= (int)$e['id'] ?>"><input type="hidden" name="campaign_id" value="<?= (int)$selected['id'] ?>"><button type="submit"><?= $e['contacted'] ? 'Quitar contactado' : 'Marcar contactado' ?></button></form>
                    <form method="post"><input type="hidden" name="action" value="toggle_redeemed"><input type="hidden" name="csrf" value="<?= h($csrf) ?>"><input type="hidden" name="id" value="<?= (int)$e['id'] ?>"><input type="hidden" name="campaign_id" value="<?= (int)$selected['id'] ?>"><button type="submit"><?= $e['redeemed'] ? 'Quitar canjeado' : 'Marcar canjeado' ?></button></form>
                    <form method="post" onsubmit="return confirm('¿Eliminar esta inscripción?');"><input type="hidden" name="action" value="delete_entry"><input type="hidden" name="csrf" value="<?= h($csrf) ?>"><input type="hidden" name="id" value="<?= (int)$e['id'] ?>"><input type="hidden" name="campaign_id" value="<?= (int)$selected['id'] ?>"><button type="submit" style="color:var(--danger)">Eliminar</button></form>
                  </div>
                </td>
              </tr>
            <?php endforeach; ?>
            </tbody>
          </table>
        </div>
      <?php else: ?>
        <div class="empty-note">Aún no hay inscripciones en esta campaña.</div>
      <?php endif; ?>

      <div class="admin-actions">
        <form method="post" onsubmit="return confirm('<?= (int)$selected['draw_done'] === 1 ? 'Ya había un sorteo realizado en esta campaña. ¿Sustituirlo por uno nuevo?' : '¿Sortear los premios ahora?' ?>');">
          <input type="hidden" name="action" value="draw">
          <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
          <input type="hidden" name="campaign_id" value="<?= (int)$selected['id'] ?>">
          <button type="submit" class="btn btn-primary" <?= count($entries) < max(count($prizes), 1) ? 'disabled' : '' ?>>&#127922; <?= (int)$selected['draw_done'] === 1 ? 'Repetir sorteo' : 'Sortear ganadores' ?></button>
        </form>
        <a class="btn btn-secondary" href="export_csv.php?campaign=<?= (int)$selected['id'] ?>">Exportar CSV</a>
      </div>

      <?php if ($entries): ?>
      <div class="admin-divider"></div>
      <div class="kicker">Vaciar esta campaña</div>
      <p style="margin-top:6px;font-size:12.5px;color:var(--muted)">Borra todas las inscripciones y ganadores de "<?= h($selected['name']) ?>". Escribe <strong>BORRAR</strong> para confirmar.</p>
      <form method="post" style="margin-top:10px;display:flex;gap:10px;flex-wrap:wrap;align-items:center">
        <input type="hidden" name="action" value="clear_all">
        <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
        <input type="hidden" name="campaign_id" value="<?= (int)$selected['id'] ?>">
        <input type="text" name="confirm_text" placeholder="Escribe BORRAR" style="border:1px solid var(--danger-border);background:var(--danger-bg);color:var(--danger);border-radius:12px;padding:10px 13px;font-size:13.5px;font-family:inherit">
        <button type="submit" class="btn btn-danger">Vaciar inscripciones</button>
      </form>
      <?php endif; ?>
    </div>
    <?php endif; ?>

  <?php endif; ?>
  </div>

  <?php require __DIR__ . '/includes/footer.php'; ?>
</div>
</body>
</html>
