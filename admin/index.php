<?php
// Админка сайта TE POWER: новости (с выводом в карусель на главной) и PDF-документы серий.
// Всё сохраняется в репозиторий GitHub; оттуда сайт пересобирается и выкладывается автоматически (1–3 минуты).
declare(strict_types=1);
require __DIR__ . '/lib/app.php';

$p = (string)($_GET['p'] ?? '');

// ---------- вход / выход ----------
if ($p === 'logout') {
    check_csrf();
    $_SESSION = [];
    session_regenerate_id(true);
    redirect('./');
}
if (!user()) {
    $error = '';
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        check_csrf();
        if (login_blocked()) { $error = 'Слишком много неудачных попыток. Попробуйте через 15 минут.'; }
        elseif (try_login(trim((string)($_POST['login'] ?? '')), (string)($_POST['password'] ?? ''))) { redirect('./'); }
        else { $error = 'Неверный логин или пароль.'; }
    }
    page_start('Вход');
    if ($error) { echo '<div class="msg msg--err">' . h($error) . '</div>'; }
    echo '<form method="post" class="card login">' . csrf_field()
       . '<label for="l">Логин</label><input type="text" id="l" name="login" autocomplete="username" required autofocus>'
       . '<label for="pw">Пароль</label><input type="password" id="pw" name="password" autocomplete="current-password" required>'
       . '<div class="actions"><button class="btn">Войти</button></div></form>';
    page_end();
    exit;
}

// ---------- новости ----------
function news_all(): array {
    $out = [];
    foreach (store()->files('content/news') as $path) {
        if (substr($path, -5) !== '.json') { continue; }
        $n = json_decode((string)store()->read($path), true);
        if (!is_array($n)) { continue; }
        $n['slug'] = basename($path, '.json');
        $out[] = $n;
    }
    usort($out, function ($a, $b) { return strcmp($b['date'] . $b['slug'], $a['date'] . $a['slug']); });
    return $out;
}
function doc_options(): array {
    $out = [];
    foreach (store()->files('content/docs') as $path) {
        if (preg_match('~^content/docs/(?!common/)[^/]+/[^/]+\.pdf$~iu', $path)) { $out[] = $path; }
    }
    return $out;
}

if ($p === 'news') {
    page_start('Новости');
    echo '<p><a class="btn" href="./?p=news-edit">+ Добавить новость</a></p><div class="card"><ul class="list">';
    $shown = 0;
    foreach (news_all() as $n) {
        $inCarousel = !empty($n['carousel']) && $shown < 10;
        if (!empty($n['carousel'])) { $shown++; }
        echo '<li><span class="list__date">' . h(date('d.m.Y', strtotime($n['date']))) . '</span><span class="list__main">' . h($n['title'])
           . ($inCarousel ? '<span class="badge">в карусели</span>' : '') . '</span>'
           . '<a class="btn btn--line btn--small" href="./?p=news-edit&amp;slug=' . h($n['slug']) . '">Изменить</a>'
           . '<a class="btn btn--line btn--small" href="../novosti/' . h($n['slug']) . '.html" target="_blank" rel="noreferrer">На сайте ↗</a></li>';
    }
    echo '</ul></div><p class="hint">В карусели на главной — до 10 последних новостей с отметкой «Показывать в карусели».</p>';
    page_end();
    exit;
}

if ($p === 'news-edit') {
    $slug = (string)($_GET['slug'] ?? '');
    if ($slug !== '' && !preg_match('/^[a-z0-9-]+$/', $slug)) { redirect('./?p=news'); }
    $path = $slug !== '' ? "content/news/$slug.json" : '';
    $n = $slug !== '' ? json_decode((string)store()->read($path), true) : null;
    if ($slug !== '' && !is_array($n)) { flash('Новость не найдена.', 'err'); redirect('./?p=news'); }
    $n = $n ?: ['title' => '', 'date' => date('Y-m-d'), 'image' => '', 'excerpt' => '', 'body' => '', 'attachments' => [], 'related' => null,
                'carousel' => true, 'carousel_style' => 'photo'];

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        check_csrf();
        try {
            if (isset($_POST['delete'])) {
                if ($slug === '') { redirect('./?p=news'); }
                $del = [$path => null];
                if (strpos((string)$n['image'], 'content/images/news/') === 0) { $del[$n['image']] = null; }  // картинка, загруженная для этой новости
                store()->commit("Новости: удалена «{$n['title']}»", $del, user()['name']);
                flash('Новость удалена. Сайт обновится через 1–3 минуты.');
                redirect('./?p=news');
            }
            $title = trim((string)($_POST['title'] ?? ''));
            $date = (string)($_POST['date'] ?? '');
            if ($title === '') { throw new RuntimeException('Заполните заголовок.'); }
            if (!preg_match('/^\d{4}-\d\d-\d\d$/', $date)) { throw new RuntimeException('Укажите дату.'); }
            $body = trim(str_replace("\r\n", "\n", (string)($_POST['body'] ?? '')));
            if ($body === '') { throw new RuntimeException('Заполните текст новости.'); }
            $excerpt = trim((string)($_POST['excerpt'] ?? ''));
            if ($excerpt === '') {  // анонс не заполнен — первый абзац текста
                $first = preg_split('/\n\s*\n/u', $body)[0];
                $excerpt = mb_substr((string)preg_replace('/\s+/u', ' ', $first), 0, 200, 'UTF-8');
            }
            $changes = [];
            if ($slug === '') {  // новая новость: адрес страницы из заголовка
                $base = slugify($title); $slug = $base; $i = 2;
                $existing = array_map(function ($f) { return basename($f, '.json'); }, store()->files('content/news'));
                while (in_array($slug, $existing, true) || is_file(dirname(__DIR__) . "/novosti/$slug.html")) { $slug = $base . '-' . $i++; }
                $path = "content/news/$slug.json";
            }
            $img = uploaded('image');
            if ($img) {
                [$bytes, $ext] = read_image($img);
                $newImage = "content/images/news/$slug.$ext";
                if ($n['image'] !== '' && $n['image'] !== $newImage && strpos($n['image'], 'content/images/news/') === 0) { $changes[$n['image']] = null; }
                $changes[$newImage] = $bytes;
                $n['image'] = $newImage;
            }
            if ($n['image'] === '') { throw new RuntimeException('Добавьте картинку новости.'); }
            $docs = doc_options();
            $att = [];
            foreach ((array)($_POST['docs'] ?? []) as $d) {
                if ($d !== '' && in_array($d, $docs, true)) { [$type, $label] = doc_label($d); $att[] = ['type' => $type, 'label' => $label, 'href' => $d]; }
            }
            $related = null;
            foreach (series_list() as $s) { if (($s['href'] ?? '') === ($_POST['related'] ?? '')) { $related = ['name' => $s['name'], 'href' => $s['href']]; } }
            $new = ['title' => $title, 'date' => $date, 'image' => $n['image'], 'excerpt' => $excerpt, 'body' => $body, 'attachments' => $att,
                    'related' => $related, 'carousel' => !empty($_POST['carousel']),
                    'carousel_style' => ($_POST['carousel_style'] ?? '') === 'product' ? 'product' : 'photo'];
            foreach (['carousel_title', 'carousel_text'] as $k) { $v = trim((string)($_POST[$k] ?? '')); if ($v !== '') { $new[$k] = $v; } }
            $changes[$path] = json_encode($new, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . "\n";
            store()->commit(($n['title'] === '' ? 'Новости: добавлена' : 'Новости: изменена') . " «{$title}»", $changes, user()['name']);
            flash('Сохранено. Сайт обновится через 1–3 минуты.');
            redirect('./?p=news-edit&slug=' . rawurlencode($slug));
        } catch (RuntimeException $e) {
            flash($e->getMessage(), 'err');
            $n = array_merge($n, array_intersect_key($_POST, array_flip(['title', 'date', 'excerpt', 'body', 'carousel_title', 'carousel_text'])));
        }
    }

    page_start($slug === '' ? 'Новая новость' : 'Изменить новость');
    $chosen = array_column($n['attachments'] ?? [], 'href');
    $docs = doc_options();
    echo '<form method="post" enctype="multipart/form-data" class="card">' . csrf_field()
       . '<label for="t">Заголовок</label><input type="text" id="t" name="title" value="' . h($n['title']) . '" required maxlength="200">'
       . '<div class="row"><div><label for="d">Дата</label><input type="date" id="d" name="date" value="' . h($n['date']) . '" required></div>'
       . '<div><label for="r">Серия (ссылка «Смотреть характеристики серии»)</label><select id="r" name="related"><option value="">— нет —</option>';
    foreach (series_list() as $s) {
        $sel = ($n['related']['href'] ?? '') === $s['href'] ? ' selected' : '';
        echo '<option value="' . h($s['href']) . '"' . $sel . '>' . h($s['name']) . '</option>';
    }
    echo '</select></div></div>'
       . '<label for="i">Картинка</label>' . ($n['image'] ? '<img class="thumb" src="../' . h($n['image']) . '" alt="">' : '')
       . '<input type="file" id="i" name="image" accept="image/jpeg,image/png,image/webp"' . ($n['image'] ? '' : ' required') . '>'
       . '<div class="hint">JPG, PNG или WebP. Большие фото уменьшаются автоматически.' . ($n['image'] ? ' Оставьте пустым, чтобы не менять.' : '') . '</div>'
       . '<label for="e">Анонс <span class="hint">— короткий текст для списка новостей и карусели; если пусто — начало текста</span></label>'
       . '<textarea id="e" name="excerpt" maxlength="400">' . h($n['excerpt']) . '</textarea>'
       . '<label for="b">Текст новости</label><textarea class="big" id="b" name="body" required>' . h($n['body']) . '</textarea>'
       . '<div class="hint">Абзацы разделяйте пустой строкой. Телефоны, e-mail и адреса сайтов станут ссылками сами.</div>'
       . '<label>Документы к новости</label>';
    for ($k = 0; $k < 3; $k++) {
        echo '<select name="docs[]" style="margin-bottom:6px;"><option value="">— нет —</option>';
        foreach ($docs as $d) {
            echo '<option value="' . h($d) . '"' . (($chosen[$k] ?? '') === $d ? ' selected' : '') . '>' . h(substr($d, strlen('content/docs/'))) . '</option>';
        }
        echo '</select>';
    }
    echo '<label class="check"><input type="checkbox" name="carousel" value="1"' . (!empty($n['carousel']) ? ' checked' : '') . '> Показывать в карусели на главной</label>'
       . '<details' . (!empty($n['carousel_title']) || !empty($n['carousel_text']) ? ' open' : '') . '><summary>Настройки слайда в карусели</summary>'
       . '<label>Вид слайда</label>'
       . '<label class="check"><input type="radio" name="carousel_style" value="photo"' . (($n['carousel_style'] ?? 'photo') !== 'product' ? ' checked' : '') . '> Фото на весь слайд</label>'
       . '<label class="check"><input type="radio" name="carousel_style" value="product"' . (($n['carousel_style'] ?? '') === 'product' ? ' checked' : '') . '> Модуль на тёмном фоне (картинка без фона, PNG/WebP)</label>'
       . '<label for="ct">Заголовок на слайде <span class="hint">— если пусто, как у новости</span></label><input type="text" id="ct" name="carousel_title" value="' . h($n['carousel_title'] ?? '') . '" maxlength="120">'
       . '<label for="cx">Текст на слайде <span class="hint">— если пусто, анонс</span></label><textarea id="cx" name="carousel_text" maxlength="300">' . h($n['carousel_text'] ?? '') . '</textarea>'
       . '</details>'
       . '<div class="actions"><button class="btn">Сохранить</button><a href="./?p=news">Отмена</a></div></form>';
    if ($slug !== '') {
        echo '<form method="post" class="actions" onsubmit="return confirm(\'Удалить новость с сайта?\')">' . csrf_field()
           . '<input type="hidden" name="delete" value="1"><button class="btn btn--danger">Удалить новость</button></form>';
    }
    page_end();
    exit;
}

// ---------- документы серий ----------
if ($p === 'docs') {
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        check_csrf();
        try {
            $f = uploaded('pdf');
            if (!$f) { throw new RuntimeException('Выберите PDF-файл.'); }
            $pdf = read_pdf($f);
            $series = array_column(series_list(), 'name', 'slug');
            if (isset($_POST['replace'])) {
                $target = (string)$_POST['replace'];
                if (!in_array($target, store()->files('content/docs'), true) || !preg_match('~\.pdf$~i', $target)) { throw new RuntimeException('Документ не найден.'); }
                store()->commit('Документы: обновлён ' . basename($target), [$target => $pdf], user()['name']);
                flash('Документ ' . basename($target) . ' заменён. Сайт обновится через 1–3 минуты.');
            } else {
                $s = (string)($_POST['series'] ?? '');
                $type = (string)($_POST['type'] ?? '');
                $name = trim(preg_replace('/\s+/u', '-', (string)($_POST['name'] ?? '')), '-');
                if (!isset($series[$s])) { throw new RuntimeException('Выберите серию.'); }
                if (!in_array($type, ['ДШ', 'ТУ'], true)) { throw new RuntimeException('Выберите тип документа.'); }
                if (!preg_match('/^[\p{L}0-9.,_+-]{1,60}$/u', $name)) { throw new RuntimeException('Название — буквы, цифры, точка, дефис (например, TESD10).'); }
                $target = "content/docs/$s/$type-$name.pdf";
                $exists = in_array($target, store()->files('content/docs'), true);
                store()->commit(($exists ? 'Документы: обновлён ' : 'Документы: добавлен ') . basename($target), [$target => $pdf], user()['name']);
                flash(($exists ? 'Документ заменён: ' : 'Документ добавлен: ') . basename($target) . '. Сайт обновится через 1–3 минуты.');
            }
        } catch (RuntimeException $e) {
            flash($e->getMessage(), 'err');
        }
        redirect('./?p=docs');
    }
    page_start('Документы серий');
    $series = series_list();
    echo '<div class="card"><h2 style="margin-top:0">Добавить документ</h2><form method="post" enctype="multipart/form-data">' . csrf_field()
       . '<div class="row"><div><label for="s">Серия</label><select id="s" name="series" required><option value="">—</option>';
    foreach ($series as $s) { echo '<option value="' . h($s['slug']) . '">' . h($s['name']) . '</option>'; }
    echo '</select></div><div><label for="ty">Тип</label><select id="ty" name="type"><option value="ДШ">Даташит (ДШ)</option><option value="ТУ">Технические условия (ТУ)</option></select></div></div>'
       . '<label for="nm">Название <span class="hint">— модель или серия, например TESD10; файл будет назван «ДШ-TESD10.pdf»</span></label><input type="text" id="nm" name="name" required maxlength="60">'
       . '<label for="f">PDF-файл</label><input type="file" id="f" name="pdf" accept="application/pdf" required><div class="hint">До ' . max_upload_mb() . ' МБ. Если такой документ уже есть, он будет заменён.</div>'
       . '<div class="actions"><button class="btn">Загрузить</button></div></form></div>';
    $files = store()->files('content/docs');
    foreach ($series as $s) {
        $docs = array_values(array_filter($files, function ($f) use ($s) { return strpos($f, "content/docs/{$s['slug']}/") === 0 && preg_match('~\.pdf$~i', $f); }));
        if (!$docs) { continue; }
        echo '<div class="card"><h2 style="margin-top:0">' . h($s['name']) . '</h2><ul class="list">';
        foreach ($docs as $d) {
            echo '<li><span class="list__main"><a href="../' . h($d) . '" target="_blank" rel="noreferrer">' . h(basename($d)) . '</a></span>'
               . '<form method="post" enctype="multipart/form-data" class="docfile">' . csrf_field() . '<input type="hidden" name="replace" value="' . h($d) . '">'
               . '<input type="file" name="pdf" accept="application/pdf" required><button class="btn btn--line btn--small">Заменить</button></form></li>';
        }
        echo '</ul></div>';
    }
    page_end();
    exit;
}

// ---------- главная админки ----------
page_start('Здравствуйте, ' . user()['name']);
echo '<div class="row"><a class="card" href="./?p=news"><h2 style="margin-top:0">Новости</h2>Добавить, изменить, удалить; вывод в карусель на главной.</a>'
   . '<a class="card" href="./?p=docs"><h2 style="margin-top:0">Документы</h2>Загрузить или заменить даташиты и технические условия серий.</a></div>';
$run = method_exists(store(), 'lastBuild') ? store()->lastBuild() : null;
if ($run) {
    $state = $run['status'] !== 'completed' ? 'идёт сейчас…' : ($run['conclusion'] === 'success' ? 'готово' : 'ошибка — сообщите разработчику');
    echo '<div class="card">Последнее обновление сайта: <b>' . h($state) . '</b> <span class="hint">(' . h(date('d.m.Y H:i', strtotime($run['updated_at']))) . ')</span></div>';
}
page_end();
