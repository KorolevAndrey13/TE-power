<?php
// Общее для страниц админки: настройки, вход, защита форм, оформление.
declare(strict_types=1);
require __DIR__ . '/store.php';

// ---- настройки: файл лежит ВНЕ папки сайта, в репозиторий не попадает ----
function config_path(): string {
    $env = getenv('TE_ADMIN_CONFIG');
    foreach ([$env ?: '', dirname((string)($_SERVER['DOCUMENT_ROOT'] ?? '')) . '/te-admin/config.php', dirname(__DIR__, 3) . '/te-admin/config.php'] as $p) {
        if ($p !== '' && is_file($p)) { return $p; }
    }
    return '';
}
$CONFIG_FILE = config_path();
if ($CONFIG_FILE === '') {
    http_response_code(503);
    exit('Админка не настроена: нет файла te-admin/config.php рядом с папкой сайта.');
}
$CONFIG = require $CONFIG_FILE;
$DATA_DIR = $CONFIG['data_dir'] ?? dirname($CONFIG_FILE) . '/data';
if (!is_dir($DATA_DIR)) { @mkdir($DATA_DIR, 0700, true); }
if (!is_dir($DATA_DIR) || !is_writable($DATA_DIR)) { $DATA_DIR = sys_get_temp_dir(); }

function store(): Store {
    global $CONFIG;
    static $s = null;
    if ($s === null) {
        $s = ($CONFIG['storage'] ?? 'github') === 'local'
            ? new LocalStore($CONFIG['local_root'])
            : new GitHubStore($CONFIG['github_token'], $CONFIG['repo'], $CONFIG['branch'] ?? 'main');
    }
    return $s;
}

// ---- заголовки и сессия ----
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: same-origin');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex, nofollow');
$https = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
session_name('te_admin');
session_set_cookie_params(['lifetime' => 0, 'path' => '/admin/', 'secure' => $https, 'httponly' => true, 'samesite' => 'Strict']);
session_start();
const SESSION_TTL = 7200;  // выход после 2 часов бездействия
if (isset($_SESSION['user']) && time() - ($_SESSION['seen'] ?? 0) > SESSION_TTL) { $_SESSION = []; session_regenerate_id(true); }
if (isset($_SESSION['user'])) { $_SESSION['seen'] = time(); }
if (empty($_SESSION['csrf'])) { $_SESSION['csrf'] = bin2hex(random_bytes(32)); }

function h($s): string { return htmlspecialchars((string)$s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function csrf_field(): string { return '<input type="hidden" name="csrf" value="' . h($_SESSION['csrf']) . '">'; }
function check_csrf(): void {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST' || !hash_equals($_SESSION['csrf'], (string)($_POST['csrf'] ?? ''))) {
        http_response_code(400);
        exit('Форма устарела. Вернитесь назад и обновите страницу.');
    }
}
function flash(string $msg, string $kind = 'ok'): void { $_SESSION['flash'][] = [$kind, $msg]; }
function redirect(string $to): void { header('Location: ' . $to); exit; }
function user(): ?array {
    global $CONFIG;
    $u = $_SESSION['user'] ?? null;
    return $u !== null && isset($CONFIG['users'][$u]) ? ['login' => $u, 'name' => $CONFIG['users'][$u]['name'] ?? $u] : null;
}

// ---- вход: не больше 5 неудачных попыток за 15 минут с одного адреса ----
const LOGIN_MAX = 5, LOGIN_WINDOW = 900;
function login_attempts_file(): string {
    global $DATA_DIR;
    return $DATA_DIR . '/te-admin-login-' . hash('sha256', (string)($_SERVER['REMOTE_ADDR'] ?? '')) . '.json';
}
function login_blocked(): bool {
    $f = login_attempts_file();
    $a = is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: []) : [];
    $a = array_filter($a, function ($t) { return $t > time() - LOGIN_WINDOW; });
    return count($a) >= LOGIN_MAX;
}
function login_failed(): void {
    $f = login_attempts_file();
    $a = is_file($f) ? (json_decode((string)file_get_contents($f), true) ?: []) : [];
    $a = array_values(array_filter($a, function ($t) { return $t > time() - LOGIN_WINDOW; }));
    $a[] = time();
    file_put_contents($f, json_encode($a), LOCK_EX);
}
/** Хэш пароля: pbkdf2_sha256$<итерации>$<соль>$<хэш> (делает tools/admin_user.py) или bcrypt ($2y$…). */
function password_ok(string $password, string $hash): bool {
    if (preg_match('/^pbkdf2_sha256\$(\d+)\$([0-9a-f]+)\$([0-9a-f]{64})$/', $hash, $m)) {
        return hash_equals($m[3], hash_pbkdf2('sha256', $password, (string)hex2bin($m[2]), (int)$m[1], 64));
    }
    return password_verify($password, $hash);
}
function try_login(string $login, string $password): bool {
    global $CONFIG;
    // для неизвестного логина — проверка того же веса, чтобы по времени ответа нельзя было подобрать логины
    $hash = $CONFIG['users'][$login]['hash'] ?? 'pbkdf2_sha256$600000$00$' . str_repeat('0', 64);
    if (!password_ok($password, $hash) || !isset($CONFIG['users'][$login])) { login_failed(); return false; }
    @unlink(login_attempts_file());
    session_regenerate_id(true);
    $_SESSION['user'] = $login;
    $_SESSION['seen'] = time();
    $_SESSION['csrf'] = bin2hex(random_bytes(32));
    return true;
}

// ---- данные сайта ----
function series_list(): array {
    $raw = store()->read('content/series.json');
    return $raw ? (json_decode($raw, true) ?: []) : [];
}
function slugify(string $s): string {
    $map = ['а'=>'a','б'=>'b','в'=>'v','г'=>'g','д'=>'d','е'=>'e','ё'=>'e','ж'=>'zh','з'=>'z','и'=>'i','й'=>'y','к'=>'k','л'=>'l','м'=>'m',
            'н'=>'n','о'=>'o','п'=>'p','р'=>'r','с'=>'s','т'=>'t','у'=>'u','ф'=>'f','х'=>'h','ц'=>'ts','ч'=>'ch','ш'=>'sh','щ'=>'sch',
            'ъ'=>'','ы'=>'y','ь'=>'','э'=>'e','ю'=>'yu','я'=>'ya'];
    $s = strtr(mb_strtolower($s, 'UTF-8'), $map);
    $s = trim((string)preg_replace('/[^a-z0-9]+/', '-', $s), '-');
    $s = implode('-', array_slice(explode('-', $s), 0, 8));
    return $s !== '' ? $s : 'novost';
}
function doc_label(string $path): array {
    // content/docs/tpd/ДШ-ТПД.pdf -> ['ДШ', 'Даташит ТПД']
    $name = pathinfo($path, PATHINFO_FILENAME);
    if (preg_match('/^(ДШ|ТУ|РП|3D)-(.+)$/u', $name, $m)) {
        $kind = ['ДШ' => 'Даташит', 'ТУ' => 'Технические условия', 'РП' => 'Руководство', '3D' => '3D-модели'][$m[1]];
        return [$m[1], $kind . ' ' . $m[2]];
    }
    return ['ДШ', 'Даташит ' . $name];
}
function max_upload_mb(): int {
    $v = function ($k) { $s = trim((string)ini_get($k)); $n = (int)$s; $u = strtolower(substr($s, -1));
                         return $u === 'g' ? $n * 1024 : ($u === 'k' ? (int)ceil($n / 1024) : ($u === 'm' ? $n : (int)ceil($n / 1048576))); };
    return max(1, min($v('upload_max_filesize'), $v('post_max_size')));
}

// ---- загрузки ----
function uploaded(string $field): ?array {
    if (!isset($_FILES[$field]) || $_FILES[$field]['error'] === UPLOAD_ERR_NO_FILE) { return null; }
    if ($_FILES[$field]['error'] !== UPLOAD_ERR_OK) {
        throw new RuntimeException('Файл не загрузился (слишком большой? предел — ' . max_upload_mb() . ' МБ).');
    }
    return $_FILES[$field];
}
function read_pdf(array $f): string {
    $data = (string)file_get_contents($f['tmp_name']);
    if (substr($data, 0, 5) !== '%PDF-') { throw new RuntimeException('Это не PDF-файл.'); }
    if (strlen($data) > 40 * 1048576) { throw new RuntimeException('PDF больше 40 МБ.'); }
    return $data;
}
/** Картинка новости: уменьшается до 1600 px по ширине и пересохраняется (метаданные фото — GPS и т.п. — при этом удаляются). */
function read_image(array $f): array {
    $info = @getimagesize($f['tmp_name']);
    $types = [IMAGETYPE_JPEG => 'jpg', IMAGETYPE_PNG => 'png', IMAGETYPE_WEBP => 'webp'];
    if (!$info || !isset($types[$info[2]])) { throw new RuntimeException('Картинка должна быть JPG, PNG или WebP.'); }
    $data = (string)file_get_contents($f['tmp_name']);
    if (!function_exists('imagecreatefromstring')) {
        if (strlen($data) > 5 * 1048576) { throw new RuntimeException('Картинка больше 5 МБ — уменьшите её перед загрузкой.'); }
        return [$data, $types[$info[2]]];
    }
    $src = imagecreatefromstring($data);
    if (!$src) { throw new RuntimeException('Не удалось прочитать картинку.'); }
    $w = imagesx($src); $hgt = imagesy($src);
    if ($w > 1600) {
        $dst = imagecreatetruecolor(1600, (int)round($hgt * 1600 / $w));
        imagealphablending($dst, false); imagesavealpha($dst, true);
        imagecopyresampled($dst, $src, 0, 0, 0, 0, 1600, (int)round($hgt * 1600 / $w), $w, $hgt);
        imagedestroy($src); $src = $dst;
    }
    imagealphablending($src, false); imagesavealpha($src, true);
    ob_start();
    if (function_exists('imagewebp')) { imagewebp($src, null, 85); $ext = 'webp'; }
    elseif ($info[2] === IMAGETYPE_PNG) { imagepng($src, null, 8); $ext = 'png'; }
    else { imagejpeg($src, null, 85); $ext = 'jpg'; }
    imagedestroy($src);
    return [(string)ob_get_clean(), $ext];
}

// ---- оформление ----
function page_start(string $title): void {
    $u = user();
    echo '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
       . '<meta name="robots" content="noindex, nofollow"><title>' . h($title) . ' — админка TE-POWER</title><style>' . ADMIN_CSS . '</style></head><body>';
    echo '<header class="top"><a class="top__brand" href="./">TE-POWER · админка</a>';
    if ($u) {
        echo '<nav class="top__nav"><a href="./?p=news">Новости</a><a href="./?p=docs">Документы</a><a href="../" target="_blank" rel="noreferrer">Сайт ↗</a></nav>'
           . '<form method="post" action="./?p=logout" class="top__out">' . csrf_field() . '<span>' . h($u['name']) . '</span><button>Выйти</button></form>';
    }
    echo '</header><main class="main"><h1>' . h($title) . '</h1>';
    foreach ($_SESSION['flash'] ?? [] as [$kind, $msg]) { echo '<div class="msg msg--' . h($kind) . '">' . h($msg) . '</div>'; }
    unset($_SESSION['flash']);
}
function page_end(): void {
    // повторное нажатие «Сохранить», пока идёт отправка, не создаёт вторую копию: кнопка блокируется после первого
    echo '<script>document.addEventListener("submit",function(e){if(e.defaultPrevented)return;var f=e.target;'
       . 'if(f.dataset.sent){e.preventDefault();return;}f.dataset.sent="1";'
       . 'f.querySelectorAll("button").forEach(function(b){b.disabled=true;if(b.classList.contains("btn"))b.textContent="Сохраняем…";});});</script>';
    echo '</main></body></html>';
}

const ADMIN_CSS = <<<'CSS'
:root{--bg:#F1F2F0;--panel:#fff;--line:#D9DCDD;--text:#1C2124;--muted:#5D6870;--accent:#215FA6;--accent-dark:#174A85;--red:#B3261E;--green:#1E7B45;}
*{box-sizing:border-box;}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;}
a{color:var(--accent);}h1{font-size:24px;margin:0 0 20px;}h2{font-size:18px;margin:28px 0 12px;}
.top{display:flex;flex-wrap:wrap;align-items:center;gap:12px 24px;padding:12px 24px;background:#1C2124;color:#fff;}
.top a{color:#fff;text-decoration:none;}.top__brand{font-weight:800;}.top__nav{display:flex;gap:18px;flex:1;}
.top__out{display:flex;align-items:center;gap:10px;margin:0;color:#B9C6D6;font-size:14px;}
.top__out button{background:none;border:1px solid #5D6870;color:#fff;border-radius:4px;padding:4px 10px;cursor:pointer;}
.main{max-width:980px;margin:0 auto;padding:28px 20px 80px;}
.card{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:20px;margin-bottom:16px;}
.msg{padding:12px 16px;border-radius:6px;margin-bottom:16px;}.msg--ok{background:#E3F2E8;color:var(--green);}.msg--err{background:#FBE7E6;color:var(--red);}
label{display:block;font-weight:600;margin:14px 0 6px;}.hint{color:var(--muted);font-size:13px;font-weight:400;margin-top:4px;}
input[type=text],input[type=password],input[type=date],select,textarea{width:100%;padding:9px 11px;border:1px solid var(--line);border-radius:4px;font:inherit;background:#fff;color:var(--text);}
textarea{min-height:110px;resize:vertical;}textarea.big{min-height:340px;}
.row{display:grid;grid-template-columns:1fr 1fr;gap:16px;}@media (max-width:640px){.row{grid-template-columns:1fr;}}
.btn{display:inline-block;background:var(--accent);color:#fff;border:none;border-radius:4px;padding:10px 18px;font:inherit;font-weight:700;cursor:pointer;text-decoration:none;}
.btn:hover{background:var(--accent-dark);}.btn--line{background:#fff;color:var(--accent);border:1px solid var(--accent);}.btn--line:hover{background:#EEF3FA;}
.btn--danger{background:#fff;color:var(--red);border:1px solid var(--red);}.btn--small{padding:5px 12px;font-size:13px;}
.actions{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:22px;}
.list{list-style:none;margin:0;padding:0;}.list li{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;padding:10px 0;border-top:1px solid var(--line);}
.list li:first-child{border-top:none;}.list__main{flex:1;min-width:220px;}.list__date{color:var(--muted);font-size:13px;font-family:ui-monospace,Consolas,monospace;}
.badge{display:inline-block;font-size:12px;padding:1px 8px;border-radius:10px;background:#E8EEF6;color:var(--accent);margin-left:6px;}
.thumb{max-width:220px;max-height:140px;border:1px solid var(--line);border-radius:4px;display:block;margin-top:6px;background:#2a2f33;}
.check{display:flex;gap:8px;align-items:center;font-weight:600;margin-top:14px;}.check input{width:18px;height:18px;}
.docfile{display:flex;flex-wrap:wrap;gap:8px;align-items:center;}.docfile form{display:flex;gap:8px;align-items:center;margin:0;}
details{margin-top:14px;}summary{cursor:pointer;color:var(--accent);font-weight:600;}
.login{max-width:380px;margin:60px auto;}
CSS;
