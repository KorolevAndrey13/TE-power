<?php
// Хранилище файлов сайта. На сервере — репозиторий GitHub (через API, одним коммитом на сохранение):
// после коммита GitHub пересобирает страницы и выкладывает сайт. Для проверки на своём компьютере — папка репозитория.

interface Store {
    /** @return string[] пути файлов (от корня репозитория) внутри папки $dir, рекурсивно */
    public function files($dir);
    /** @return string|null содержимое файла или null, если его нет */
    public function read($path);
    /** @param array $changes путь => содержимое (string) или null (удалить) */
    public function commit($message, array $changes, $author);
}

final class GitHubStore implements Store {
    private $token, $repo, $branch, $tree = null;

    public function __construct($token, $repo, $branch) {
        $this->token = $token; $this->repo = $repo; $this->branch = $branch;
    }

    private function api($method, $url, $body = null) {
        $ch = curl_init(strpos($url, 'https://') === 0 ? $url : "https://api.github.com/repos/{$this->repo}$url");
        $headers = ['Authorization: Bearer ' . $this->token, 'Accept: application/vnd.github+json',
                    'X-GitHub-Api-Version: 2022-11-28', 'User-Agent: te-power-admin'];
        if ($body !== null) { $headers[] = 'Content-Type: application/json'; }
        curl_setopt_array($ch, [CURLOPT_CUSTOMREQUEST => $method, CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => $headers,
                                CURLOPT_TIMEOUT => 120, CURLOPT_CONNECTTIMEOUT => 15]);
        if ($body !== null) { curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($body, JSON_UNESCAPED_UNICODE)); }
        $raw = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $err = curl_error($ch);
        curl_close($ch);
        if ($raw === false) { throw new RuntimeException('Нет связи с GitHub: ' . $err); }
        $data = json_decode($raw, true);
        if ($code >= 400) {
            throw new RuntimeException("GitHub ответил $code: " . (is_array($data) && isset($data['message']) ? $data['message'] : substr($raw, 0, 200)));
        }
        return $data;
    }

    private function head() {
        $ref = $this->api('GET', '/git/ref/heads/' . rawurlencode($this->branch));
        return $ref['object']['sha'];
    }

    private function tree() {
        if ($this->tree === null) {
            $commit = $this->api('GET', '/git/commits/' . $this->head());
            $t = $this->api('GET', '/git/trees/' . $commit['tree']['sha'] . '?recursive=1');
            $this->tree = [];
            foreach ($t['tree'] as $e) { if ($e['type'] === 'blob') { $this->tree[$e['path']] = $e['sha']; } }
        }
        return $this->tree;
    }

    public function files($dir) {
        $dir = rtrim($dir, '/') . '/';
        $out = [];
        foreach (array_keys($this->tree()) as $p) { if (strpos($p, $dir) === 0) { $out[] = $p; } }
        sort($out, SORT_STRING);
        return $out;
    }

    public function read($path) {
        $tree = $this->tree();
        if (!isset($tree[$path])) { return null; }
        $blob = $this->api('GET', '/git/blobs/' . $tree[$path]);
        return base64_decode($blob['content']);
    }

    public function commit($message, array $changes, $author) {
        $parent = $this->head();
        $base = $this->api('GET', '/git/commits/' . $parent);
        $entries = [];
        foreach ($changes as $path => $content) {
            if ($content === null) {
                $entries[] = ['path' => $path, 'mode' => '100644', 'type' => 'blob', 'sha' => null];
            } else {
                $blob = $this->api('POST', '/git/blobs', ['content' => base64_encode($content), 'encoding' => 'base64']);
                $entries[] = ['path' => $path, 'mode' => '100644', 'type' => 'blob', 'sha' => $blob['sha']];
            }
        }
        $tree = $this->api('POST', '/git/trees', ['base_tree' => $base['tree']['sha'], 'tree' => $entries]);
        $commit = $this->api('POST', '/git/commits', ['message' => $message . "\n\nИзменено в админке: $author", 'tree' => $tree['sha'],
                                                       'parents' => [$parent]]);
        $this->api('PATCH', '/git/refs/heads/' . rawurlencode($this->branch), ['sha' => $commit['sha']]);
        $this->tree = null;
        return $commit['sha'];
    }

    /** Состояние последней сборки сайта (нужен доступ ключа Actions: Read) */
    public function lastBuild() {
        try {
            $r = $this->api('GET', '/actions/runs?branch=' . rawurlencode($this->branch) . '&per_page=1');
            return isset($r['workflow_runs'][0]) ? $r['workflow_runs'][0] : null;
        } catch (RuntimeException $e) {
            return null;
        }
    }
}

final class LocalStore implements Store {
    private $root;

    public function __construct($root) { $this->root = rtrim($root, '/\\'); }

    public function files($dir) {
        $base = $this->root . '/' . trim($dir, '/');
        if (!is_dir($base)) { return []; }
        $out = [];
        $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($base, FilesystemIterator::SKIP_DOTS));
        foreach ($it as $f) {
            if ($f->isFile()) { $out[] = str_replace('\\', '/', substr($f->getPathname(), strlen($this->root) + 1)); }
        }
        sort($out, SORT_STRING);
        return $out;
    }

    public function read($path) {
        $f = $this->root . '/' . $path;
        return is_file($f) ? file_get_contents($f) : null;
    }

    public function commit($message, array $changes, $author) {
        foreach ($changes as $path => $content) {
            $f = $this->root . '/' . $path;
            if ($content === null) { if (is_file($f)) { unlink($f); } continue; }
            if (!is_dir(dirname($f))) { mkdir(dirname($f), 0775, true); }
            file_put_contents($f, $content);
        }
        return 'local';
    }

    public function lastBuild() { return null; }
}
