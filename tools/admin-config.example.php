<?php
// Настройки админки. Скопируйте этот файл на сервер как  <папка рядом с сайтом>/te-admin/config.php,
// то есть НЕ внутрь папки сайта: если сайт лежит в www/te-power.ru/, файл должен быть www/te-admin/config.php.
// Права на файл — 600 (читает только владелец). В репозиторий настоящий config.php не кладётся.
return [
    // Ключ доступа GitHub (fine-grained personal access token):
    // github.com → Settings → Developer settings → Fine-grained tokens → Generate new token
    //   Repository access: Only select repositories → TE-power
    //   Permissions → Repository: Contents — Read and write; Actions — Read-only (для строки «Последнее обновление сайта»)
    'github_token' => 'github_pat_ВСТАВЬТЕ_КЛЮЧ',
    'repo'   => 'KorolevAndrey13/TE-power',
    'branch' => 'main',

    // Пользователи: строки делает  python tools/admin_user.py
    'users' => [
        // 'andrey' => ['name' => 'Андрей', 'hash' => 'pbkdf2_sha256$600000$…$…'],
    ],
];
