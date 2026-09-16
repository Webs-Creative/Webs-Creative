<?php
declare(strict_types=1);
session_start();
require __DIR__ . '/includes/db.php';
require __DIR__ . '/includes/helpers.php';

$campaign = wc_active_campaign();
$error = null;

if ($campaign && $_SERVER['REQUEST_METHOD'] === 'POST' && ($_POST['action'] ?? '') === 'signup') {
    if (!wc_csrf_check()) {
        $error = 'Tu sesión ha caducado. Recarga la página e inténtalo de nuevo.';
    } elseif (!empty($_POST['website'])) {
        // honeypot field filled in by a bot: pretend success, save nothing
        header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?') . '?ok=1');
        exit;
    } elseif (isset($_POST['form_ts']) && (time() - (int)$_POST['form_ts']) < 2) {
        $error = 'Por favor, inténtalo de nuevo.';
    } else {
        $name = trim((string)($_POST['name'] ?? ''));
        $email = trim((string)($_POST['email'] ?? ''));
        $phone = trim((string)($_POST['phone'] ?? ''));
        $company = trim((string)($_POST['company'] ?? ''));
        $accept = isset($_POST['accept']);
        $deadlineTs = strtotime($campaign['deadline'] . ' 23:59:00');

        if ($name === '' || $email === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || !$accept) {
            $error = 'Completa tu nombre, un correo válido y acepta las bases para participar.';
        } elseif ($deadlineTs !== false && $deadlineTs < time()) {
            $error = 'El plazo de inscripción ya ha terminado.';
        } else {
            $emailNorm = mb_strtolower($email);
            try {
                $stmt = wc_db()->prepare(
                    'INSERT INTO entries (campaign_id, name, email, email_norm, phone, company, created_at)
                     VALUES (:cid, :name, :email, :email_norm, :phone, :company, :created_at)'
                );
                $stmt->execute([
                    'cid' => $campaign['id'],
                    'name' => $name,
                    'email' => $email,
                    'email_norm' => $emailNorm,
                    'phone' => $phone !== '' ? $phone : null,
                    'company' => $company !== '' ? $company : null,
                    'created_at' => date('c'),
                ]);
                $_SESSION['wc_my_email'][$campaign['id']] = $email;
                header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?') . '?ok=1');
                exit;
            } catch (PDOException $e) {
                if (str_contains($e->getMessage(), 'UNIQUE')) {
                    $_SESSION['wc_my_email'][$campaign['id']] = $email;
                    header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?') . '?ok=1');
                    exit;
                }
                $error = 'No se pudo guardar tu inscripción. Inténtalo de nuevo en unos minutos.';
            }
        }
    }
}

$confirmedEmail = null;
if ($campaign && isset($_GET['ok'])) {
    $confirmedEmail = $_SESSION['wc_my_email'][$campaign['id']] ?? null;
}

$prizes = $campaign ? wc_campaign_prizes($campaign) : [];
$winnerNames = [];
if ($campaign && (int)$campaign['draw_done'] === 1) {
    $rows = wc_db()->prepare('SELECT name, winner_index FROM entries WHERE campaign_id = ? AND winner_index IS NOT NULL');
    $rows->execute([$campaign['id']]);
    foreach ($rows->fetchAll(PDO::FETCH_ASSOC) as $r) {
        $winnerNames[(int)$r['winner_index']] = $r['name'];
    }
}

$csrf = wc_csrf_token();
$daysLeft = $campaign ? wc_days_left($campaign['deadline']) : 0;
?>
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= $campaign ? h($campaign['name']) : 'Sorteos Webs Creative' ?></title>
<meta name="description" content="<?= $campaign ? h($campaign['subtitle']) : 'Sorteos y promociones para clientes de Webs Creative.' ?>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Work+Sans:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<div class="wrap">

  <div class="topbar">
    <a class="brand" href="https://webscreative.es/"><span class="brand-mark">WC</span>Webs Creative</a>
  </div>

  <?php if (!$campaign): ?>

    <div class="section">
      <div class="card" style="text-align:center">
        <div class="kicker">Sorteos Webs Creative</div>
        <h2 class="title">Ahora mismo no hay ningún sorteo activo</h2>
        <p style="margin-top:10px;font-size:14px;color:var(--ink-2)">Vuelve a mirar pronto o sigue nuestras redes para no perderte la próxima campaña.</p>
      </div>
    </div>

  <?php else: ?>

  <div class="section" style="padding-bottom:0">
    <div class="hero">
      <span class="eyebrow eyebrow-pulse"><span class="dot"></span>Sorteo exclusivo &middot; solo clientes de Webs Creative</span>
      <h1><?= h($campaign['name']) ?></h1>
      <p><?= h($campaign['subtitle']) ?></p>
      <div class="hero-actions">
        <a href="#inscripcion" class="btn btn-primary btn-shine">Quiero participar &darr;</a>
        <div class="deadline-chip">
          <?php if ($daysLeft > 0): ?>
            Quedan <strong style="color:#fff"><?= $daysLeft ?> día<?= $daysLeft === 1 ? '' : 's' ?></strong> para inscribirte &middot; hasta el <?= h(wc_fmt_date_long($campaign['deadline'])) ?>
          <?php else: ?>
            <?= (int)$campaign['draw_done'] === 1 ? 'Sorteo ya celebrado' : 'Inscripciones cerradas, sorteo en marcha' ?>
          <?php endif; ?>
        </div>
      </div>
    </div>
  </div>

  <?php if ($prizes): ?>
  <div class="tickets tickets-cols-<?= min(count($prizes), 3) ?>">
    <?php foreach ($prizes as $i => $prize): ?>
    <div class="ticket">
      <div class="pct"><?= h($prize['title'] ?? '') ?></div>
      <div class="label">Premio <?= $i + 1 ?></div>
      <div class="uses"><?= h($prize['description'] ?? '') ?></div>
      <?php if (isset($winnerNames[$i])): ?><div class="winner-badge">Ganador: <?= h(wc_first_name_last_initial($winnerNames[$i])) ?></div><?php endif; ?>
    </div>
    <?php endforeach; ?>
  </div>
  <?php endif; ?>

  <div class="section" id="inscripcion">
    <div class="card">
      <?php if ($confirmedEmail): ?>
        <div class="confirm-box">
          <div class="confirm-icon">&#10003;</div>
          <h2 class="title" style="margin-top:0">¡Ya estás dentro del sorteo!</h2>
          <p style="margin-top:8px;color:var(--ink-2);font-size:14px;line-height:1.6">
            Te inscribiste con <strong><?= h($confirmedEmail) ?></strong>. Si ganas, te avisaremos por correo y por
            teléfono antes del <?= h(wc_fmt_date_long($campaign['draw_date'])) ?>.
          </p>
        </div>
      <?php else: ?>
        <div class="kicker">Inscripción</div>
        <h2 class="title">Apunta tus datos</h2>
        <p style="margin-top:8px;font-size:14px;color:var(--ink-2)">Una inscripción por cliente o empresa. Tardas menos de un minuto.</p>
        <?php if ($error): ?><div class="error-text"><?= h($error) ?></div><?php endif; ?>
        <?php if ($daysLeft <= 0): ?>
          <p style="margin-top:16px;font-size:14px;color:var(--ink-2)">El plazo de inscripción ha terminado. Gracias por vuestro interés.</p>
        <?php else: ?>
        <form method="post" action="index.php#inscripcion">
          <input type="hidden" name="action" value="signup">
          <input type="hidden" name="csrf" value="<?= h($csrf) ?>">
          <input type="hidden" name="form_ts" value="<?= time() ?>">
          <input class="hp-field" type="text" name="website" tabindex="-1" autocomplete="off">
          <div class="form-grid">
            <div class="field full"><label for="f-name">Nombre y apellidos *</label>
              <input id="f-name" name="name" type="text" required autocomplete="name" placeholder="Ej. Laura Pérez" value="<?= h($_POST['name'] ?? '') ?>"></div>
            <div class="field"><label for="f-email">Correo electrónico *</label>
              <input id="f-email" name="email" type="email" required autocomplete="email" placeholder="tucorreo@empresa.com" value="<?= h($_POST['email'] ?? '') ?>"></div>
            <div class="field"><label for="f-phone">Teléfono (opcional)</label>
              <input id="f-phone" name="phone" type="tel" autocomplete="tel" placeholder="600 000 000" value="<?= h($_POST['phone'] ?? '') ?>"></div>
            <div class="field full"><label for="f-company">Empresa (opcional)</label>
              <input id="f-company" name="company" type="text" autocomplete="organization" placeholder="Nombre de tu negocio" value="<?= h($_POST['company'] ?? '') ?>"></div>
          </div>
          <div class="checkline">
            <input id="f-accept" type="checkbox" name="accept" required>
            <label for="f-accept">He leído y acepto las bases del sorteo y la <a href="https://webscreative.es/politica-de-privacidad/" target="_blank" rel="noopener noreferrer">política de privacidad</a> de Webs Creative. *</label>
          </div>
          <div class="form-actions"><button type="submit" class="btn btn-primary" style="width:100%">Inscribirme en el sorteo &rarr;</button></div>
        </form>
        <?php endif; ?>
        <div class="small-print">Solo para clientes de Webs Creative. Una inscripción por cliente o empresa. El premio no es acumulable con otras ofertas. Puedes pedir las bases completas escribiendo a <a href="mailto:info@webscreative.es" style="color:var(--accent-ink)">info@webscreative.es</a>.</div>
      <?php endif; ?>
    </div>
  </div>

  <div class="section" style="padding-top:0">
    <div class="card">
      <div class="kicker">Cómo funciona</div>
      <h2 class="title">Cuatro pasos, sin complicaciones</h2>
      <div class="steps">
        <div class="step"><div class="step-num">01</div><p><strong>Inscríbete</strong> con tu nombre y correo antes del <?= h(wc_fmt_date_long($campaign['deadline'])) ?>.</p></div>
        <div class="step"><div class="step-num">02</div><p>El <strong><?= h(wc_fmt_date_long($campaign['draw_date'])) ?></strong> hacemos el sorteo entre todos los clientes inscritos.</p></div>
        <div class="step"><div class="step-num">03</div><p>Avisamos a los ganadores por correo y teléfono.</p></div>
        <div class="step"><div class="step-num">04</div><p>Canjeas tu premio en tu próximo proyecto con nosotros, sin acumular con otras ofertas.</p></div>
      </div>
    </div>
  </div>

  <?php endif; ?>

  <?php require __DIR__ . '/includes/footer.php'; ?>
</div>
</body>
</html>
