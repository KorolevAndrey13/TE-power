<?php
// Отправка заявок с сайта на почту отдела продаж: «Заказать звонок», форма на странице «Контакты», заявка из корзины.
// Страница шлёт сюда JSON, письмо уходит на SALES_EMAIL. Работает на хостинге REG.RU; на GitHub Pages PHP нет —
// там theme.js предлагает отправить заявку письмом из почтовой программы.
declare(strict_types=1);

const SALES_EMAIL = 'russia@te-power.ru';
const FROM_EMAIL = 'noreply@te-power.ru';
const LIMIT_PER_IP = 5;     // заявок с одного адреса…
const LIMIT_WINDOW = 600;   // …за 10 минут
const LIMIT_TOTAL = 60;     // и всего с сайта за час — на случай рассылки спама с разных адресов

date_default_timezone_set('Europe/Moscow');
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
header('Cache-Control: no-store');

function reply(int $code, string $error = ''): void {
    http_response_code($code);
    echo json_encode($error === '' ? ['ok' => true] : ['ok' => false, 'error' => $error], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { reply(405, 'Нужен POST'); }
// заявки принимаются только со страниц этого же сайта
$origin = (string)($_SERVER['HTTP_ORIGIN'] ?? '');
if ($origin !== '' && parse_url($origin, PHP_URL_HOST) !== parse_url('//' . ($_SERVER['HTTP_HOST'] ?? ''), PHP_URL_HOST)) { reply(403, 'Чужой сайт'); }

$data = json_decode((string)file_get_contents('php://input', false, null, 0, 65536), true);
if (!is_array($data)) { reply(400, 'Неверный запрос'); }
if (trim((string)($data['_honey'] ?? '')) !== '') { reply(200); }  // поле-ловушка заполнено — бот; отвечаем «ок», письмо не шлём
if (($data['consent'] ?? false) !== true) { reply(400, 'Отметьте согласие на обработку персональных данных.'); }

// ---- ограничение частоты: счётчики лежат вне папки сайта ----
$dir = dirname((string)($_SERVER['DOCUMENT_ROOT'] ?? __DIR__)) . '/te-forms';
if (!is_dir($dir)) { @mkdir($dir, 0700, true); }
if (!is_dir($dir) || !is_writable($dir)) { $dir = sys_get_temp_dir(); }
function hits(string $file, int $window): array {
    $a = is_file($file) ? (json_decode((string)file_get_contents($file), true) ?: []) : [];
    return array_values(array_filter($a, function ($t) use ($window) { return is_int($t) && $t > time() - $window; }));
}
foreach (glob($dir . '/ip-*.json') ?: [] as $old) {  // хэши IP-адресов старше суток удаляются (срок указан в политике)
    if (filemtime($old) < time() - 86400) { @unlink($old); }
}
$ipFile = $dir . '/ip-' . hash('sha256', (string)($_SERVER['REMOTE_ADDR'] ?? '')) . '.json';
$allFile = $dir . '/all.json';
$ip = hits($ipFile, LIMIT_WINDOW);
$all = hits($allFile, 3600);
if (count($ip) >= LIMIT_PER_IP || count($all) >= LIMIT_TOTAL) { reply(429, 'Слишком много заявок подряд. Попробуйте через несколько минут или позвоните нам.'); }

// ---- поля ----
function field(array $d, string $key, int $max, bool $required, string $title): string {
    $v = (string)($d[$key] ?? '');
    $v = trim((string)preg_replace('/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/u', '', $v));  // без управляющих символов
    if ($required && $v === '') { reply(400, "Заполните поле «{$title}»."); }
    return mb_substr($v, 0, $max, 'UTF-8');
}
function phone(string $v): string {
    if (strlen((string)preg_replace('/\D/', '', $v)) < 6) { reply(400, 'Проверьте номер телефона.'); }
    return $v;
}
function email(string $v, bool $required): string {
    if ($v === '' && !$required) { return ''; }
    if (!filter_var($v, FILTER_VALIDATE_EMAIL) || preg_match('/[\r\n]/', $v)) { reply(400, 'Проверьте адрес e-mail.'); }
    return $v;
}
function line(string $label, string $value): string { return $label . ': ' . ($value === '' ? '—' : $value) . "\n"; }

$type = (string)($data['type'] ?? '');
$page = field($data, 'page', 300, false, 'Страница');
$replyTo = '';
if ($type === 'callback') {
    $name = field($data, 'name', 100, true, 'Имя');
    $tel = phone(field($data, 'phone', 40, true, 'Телефон'));
    $subject = "Заказ звонка с сайта: $name";
    $body = "Посетитель сайта просит перезвонить.\n\n" . line('Имя', $name) . line('Телефон', $tel);
} elseif ($type === 'contact') {
    $name = field($data, 'name', 100, true, 'Имя');
    $company = field($data, 'company', 150, true, 'Название компании');
    $replyTo = email(field($data, 'email', 150, true, 'E-mail'), true);
    $tel = phone(field($data, 'phone', 40, true, 'Телефон'));
    $comment = field($data, 'comment', 3000, false, 'Комментарий');
    $subject = "Заявка с сайта: $company";
    $body = "Заявка со страницы «Контакты».\n\n" . line('Имя', $name) . line('Компания', $company) . line('E-mail', $replyTo)
          . line('Телефон', $tel) . "\nКомментарий:\n" . ($comment === '' ? '—' : $comment) . "\n";
} elseif ($type === 'order') {
    $name = field($data, 'fio', 150, true, 'ФИО');
    $company = field($data, 'company', 150, true, 'Компания');
    $tel = phone(field($data, 'phone', 40, true, 'Телефон'));
    $replyTo = email(field($data, 'email', 150, true, 'E-mail'), true);
    $comment = field($data, 'comment', 3000, false, 'Комментарий');
    $items = is_array($data['items'] ?? null) ? array_slice($data['items'], 0, 100) : [];
    if (!$items) { reply(400, 'Корзина пуста.'); }
    $list = '';
    foreach (array_values($items) as $i => $it) {
        if (!is_array($it)) { continue; }
        $qty = max(1, min(1000000, (int)($it['qty'] ?? 1)));
        $list .= ($i + 1) . '. ' . field($it, 'name', 150, true, 'Модель') . " — $qty шт."
               . (($desc = field($it, 'desc', 300, false, '')) !== '' ? " ($desc)" : '') . "\n";
    }
    $subject = 'Заявка с сайта: ' . count($items) . ' поз., ' . $company;
    $body = "Заявка из корзины сайта.\n\n" . line('ФИО', $name) . line('Компания', $company) . line('Телефон', $tel) . line('E-mail', $replyTo)
          . "\nСостав заявки:\n" . $list . "\nКомментарий:\n" . ($comment === '' ? '—' : $comment) . "\n";
} else {
    reply(400, 'Неизвестная форма');
}
$body .= "\n" . line('Страница', $page) . line('Время', date('d.m.Y H:i'))
       . line('Согласие на обработку персональных данных', 'дано ' . date('d.m.Y H:i') . ' (галочка в форме; Политика и Согласие на сайте)')
       . "\nОтветить клиенту: " . ($replyTo !== '' ? 'кнопкой «Ответить».' : 'по телефону.') . "\n";

// ---- письмо ----
$enc = function (string $s): string { return '=?UTF-8?B?' . base64_encode($s) . '?='; };
$headers = [
    'From: ' . $enc('Сайт TE POWER') . ' <' . FROM_EMAIL . '>',
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: base64',
];
if ($replyTo !== '') { $headers[] = 'Reply-To: ' . $replyTo; }
$sent = mail(SALES_EMAIL, $enc($subject), chunk_split(base64_encode($body)), implode("\r\n", $headers), '-f' . FROM_EMAIL);
if (!$sent) { reply(500, 'Не удалось отправить письмо.'); }

$ip[] = time(); $all[] = time();
@file_put_contents($ipFile, json_encode($ip), LOCK_EX);
@file_put_contents($allFile, json_encode($all), LOCK_EX);
reply(200);
