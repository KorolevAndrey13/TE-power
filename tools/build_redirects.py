# Переадресация со старого сайта te-power.ru (WordPress) на новый сайт.
# Источник адресов — data/wp-urls.json (выгрузка из базы WordPress). Результат — в data/redirects/:
#   redirects.csv         таблица «старый адрес → новый адрес» (для проверки и для людей)
#   wp-redirection.csv    импорт в плагин Redirection для WordPress (Инструменты → Redirection → Импорт)
#   htaccess.txt          правила для Apache (.htaccess в корне старого сайта)
#   nginx.conf            правила для nginx (если хостинг даёт править конфиг)
#   not-mapped.txt        старые файлы, которым на новом сайте нет замены
# Адреса старого WordPress: страницы и новости — /<slug>/, товары — /product/<slug>/, файлы — /wp-content/uploads/…
import csv, io, json, os, re
from urllib.parse import unquote, quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
from site_config import SITE_URL as TARGET  # куда ведут переадресации — адрес сайта из tools/site_config.py
OUT = os.path.join(HERE, 'data', 'redirects')
data = json.load(io.open(os.path.join(HERE, 'data', 'wp-urls.json'), encoding='utf-8'))

PAGES = {
    'home': '', 'home-en': '',
    'news': 'novosti.html', 'newspage': 'novosti.html', 'news-en': 'novosti.html',
    'contact': 'kontakty.html', 'contact-en': 'kontakty.html',
    'about': 'o-kompanii.html', 'our-history-en': 'o-kompanii.html',
    'certificate': 'o-kompanii.html', 'certificate-en': 'o-kompanii.html',
    'information': 'podderzhka.html', 'datasheets': 'podderzhka.html', 'elementor-4838': 'podderzhka.html',
    'catalog-archive': 'podderzhka.html',
    'new-dev': 'produktsiya.html', 'tesa': 'produktsiya.html',
    'tesd': 'serii/tesd.html', 'elementor-4844': 'serii/tesd.html',
    'tesds': 'serii/tesds.html', 'tesds-2': 'serii/tesds.html',
    'tesh': 'serii/tesh.html', 'tesh-2': 'serii/tesh.html',
    'tesav': 'serii/tesav.html', 'tesav_ru': 'serii/tesav.html',
    'jetas': 'serii/jetas.html', 'jetas-en': 'serii/jetas.html',
    'tefa': 'serii/tefa.html', 'tefd': 'serii/tefd.html', 'tefs': 'serii/tefs.html',
    'tpc': 'serii/tps.html', 'tpf': 'serii/tpf.html',
    'dft': 'serii/dft.html', 'dftp-dftpk': 'serii/dft.html', 'ten': 'serii/ten.html',
    'cart': 'korzina.html', 'заказ': 'korzina.html', 'request-quote': 'korzina.html',
}
PRODUCTS = {
    'tesd5': 'serii/tesd10.html', 'tesd10': 'serii/tesd10.html', 'tesd15': 'serii/tesd15.html', 'tesd30': 'serii/tesd30.html',
    'tesd60': 'serii/tesd60.html', 'tesd100': 'serii/tesd100.html', 'tesd200': 'serii/tesd200.html',
    'tesd250': 'serii/tesd.html', 'tesd500': 'serii/tesd500.html',
    'tesds15': 'serii/tesds15.html', 'tesds25': 'serii/tesds25.html', 'tesds40': 'serii/tesds40.html',
    'tesds60': 'serii/tesds60.html', 'tesds120': 'serii/tesds150.html', 'tesds300': 'serii/tesds300.html',
    'tesds500': 'serii/tesds500.html', 'tesds600': 'serii/tesds.html',
    'tesh-50': 'serii/tesh50.html', 'tesh-200': 'serii/tesh200.html', 'tesh-500': 'serii/tesh500.html',
    'jetas30-a1': 'serii/jetas60.html', 'jetas60-a1': 'serii/jetas60.html', 'jetas120-a2': 'serii/jetas120.html',
    'jetas300-a3': 'serii/jetas300.html', 'jetas700-a4': 'serii/jetas700.html', 'jetas1200-a5': 'serii/jetas1200.html',
    'jetas1500-a6': 'serii/jetas1500.html',
    'tesav-50': 'serii/tesav50.html', 'tesav-100': 'serii/tesav200.html', 'tesav-200': 'serii/tesav200.html',
    'tesav-500': 'serii/tesav500.html',
    'tefa1': 'serii/tefa1.html', 'tefa5': 'serii/tefa5.html', 'tefa10': 'serii/tefa10.html', 'tefa20': 'serii/tefa20.html',
    'tefd2-5': 'serii/tefd2-5.html', 'tefd5': 'serii/tefd5.html', 'tefd10': 'serii/tefd10.html',
    'tefd20': 'serii/tefd20.html', 'tefd40': 'serii/tefd40.html',
    'tefs-5': 'serii/tefs.html', 'tefs10': 'serii/tefs.html', 'tefs-20': 'serii/tefs.html',
    'тпс1000-380': 'serii/tps1000.html', 'тпс1500-380': 'serii/tps1500.html', 'тпс2000-380': 'serii/tps2000.html',
    'тпс3000-380': 'serii/tps3000.html', 'тп4000-380': 'serii/tps4000.html',
    'tpf15-380': 'serii/tpf15.html', 'dft': 'serii/dft.html',
    'тен-5': 'serii/ten5.html', 'тен-8': 'serii/ten8.html', 'тен-20': 'serii/ten20.html',
}
POSTS = {  # новости, у которых на новом сайте есть своя страница или прямая тема; остальные — на список новостей
    10422: 'novosti/novinka-tpd-zheleznodorozhnye.html', 10382: 'novosti/novinka-tpi-dc-ac-invertory.html',
    10287: 'novosti/novinka-tps1500-analog-maa1500.html', 10459: 'novosti/novinka-ten-analog-traco-power.html',
    10582: 'novosti/s-dnem-pobedy.html',
    10242: 'serii/tesd480.html', 10222: 'serii/tefs.html', 8280: 'serii/tesav.html', 7827: 'serii/tps.html',
    2796: 'serii/tesd.html', 3291: 'serii/tesd.html', 9309: 'serii/dft.html', 9814: 'serii/dft.html',
    9377: 'podderzhka.html', 9522: 'podderzhka.html', 4055: 'podderzhka.html', 8337: 'podderzhka.html',
    4968: 'podderzhka.html', 4980: 'podderzhka.html', 6076: 'podderzhka.html',
    8967: 'produktsiya.html', 7805: 'korzina.html',
}

def upload_target(name):
    """Файл из /wp-content/uploads/ → файл нового сайта или None, если замены нет."""
    n = name
    D = 'content/docs/'
    rules = [
        # старые версии даташитов действующих моделей → текущий даташит того же типоразмера
        (r'TESD(\d+)_TEP(?:ower|_rev\.1\.2)\.pdf', lambda m: f'{D}tesd/ДШ-TESD{m[1]}.pdf'),
        (r'TESD\d+-(\d+)_rev\.1\.2\.pdf', lambda m: f'{D}tesd/ДШ-TESD{m[1]}.pdf'),
        (r'TESDs15_TEPower_en\.pdf', lambda m: f'{D}tesds/ДШ-TESDs15.pdf'),
        (r'TESDs50_TEPower(?:_en)?\.pdf', lambda m: f'{D}tesds/ДШ-TESDs60.pdf'),
        (r'(JETAs\d+)\.pdf', lambda m: f'{D}jetas/ДШ-{m[1]}.pdf'),
        (r'(TEFA\d+)\.pdf', lambda m: f'{D}tefa/ДШ-{m[1]}.pdf'),
        (r'(TEFD[\d.]+)\.pdf', lambda m: f'{D}tefd/ДШ-{m[1]}.pdf'),
        (r'(TEFS\d+)\.pdf', lambda m: f'{D}tefs/ДШ-{m[1]}.pdf'),
        (r'(TESAV\d+)\.pdf', lambda m: f'{D}tesav/ДШ-{m[1]}.pdf'),
        (r'(TESDs\d+)\.pdf', lambda m: f'{D}tesds/ДШ-{m[1]}.pdf'),
        (r'(TESD\d+)\.pdf', lambda m: f'{D}tesd/ДШ-{m[1]}.pdf'),
        (r'(TESH\d+)\.pdf', lambda m: f'{D}tesh/{m[1]}.pdf'),
        (r'TEН5\.pdf', lambda m: f'{D}ten/ДШ-ТЕН5.pdf'),
        (r'(TEН(?:8|20))\.pdf', lambda m: f'{D}ten/ДШ-ТЕН{m[1][3:]}.pdf'),
        (r'TПИ(\d+)\.pdf', lambda m: f'{D}tpi/ДШ-ТПИ{m[1]}.pdf'),
        (r'ТПД\.pdf', lambda m: f'{D}tpd/ДШ-ТПД.pdf'),
        (r'ТПС(\d+)\.pdf', lambda m: f'{D}tps/ДШ-ТПС{m[1]}.pdf'),
        (r'ТПФ15\.pdf', lambda m: f'{D}tpf/ДШ-ТПФ15.pdf'),
        (r'(?:ДШ-ДФТ|dft-datasheet)\.pdf', lambda m: f'{D}dft/ДШ-ДФТ-ДФТК.pdf'),
        (r'ДШ-ДФТП\.pdf', lambda m: f'{D}dft/ДШ-ДФТП-ДФТПК.pdf'),
        # технические условия, в том числе старые названия файлов
        (r'(?:ТУ-JETAs|TU-JETAs|Технические-условия-на-модули-серии-JETAs-NEW)\.pdf', lambda m: f'{D}jetas/ТУ-JETAs.pdf'),
        (r'(?:ТУ-TESDs|TU-TESDs|Технические_условия_на_модули_серии_TESDs)\.pdf', lambda m: f'{D}tesds/ТУ-TESDs.pdf'),
        (r'(?:ТУ-TESD_корр|TU_TESD|Технические_условия_на_модули_серии_TESD_NEW)\.pdf', lambda m: f'{D}tesd/ТУ-TESD.pdf'),
        (r'(?:ТУ-TESH|Технические-условия-на-модули-серии-TESH)\.pdf', lambda m: f'{D}tesh/ТУ-TESH.pdf'),
        (r'(?:ТУ-TESAV|Технические_условия_на_модули_серии_TESAV)\.pdf', lambda m: f'{D}tesav/ТУ-TESAV.pdf'),
        (r'(?:ТУ-ТПС|Технические_условия_на_модули_серии_ТПС-380)\.pdf', lambda m: f'{D}tps/ТУ-ТПС.pdf'),
        (r'ТУ-(TEFA|TEFD|TEFS)\.pdf', lambda m: f'{D}{m[1].lower()}/ТУ-{m[1]}.pdf'),
        (r'ТУ-ДФТ\.pdf', lambda m: f'{D}dft/ТУ-ДФТ.pdf'),
        # руководства по применению и рекомендации по радиаторам
        (r'РТМ-JETAs-и-ТПС\.pdf', lambda m: f'{D}common/РП-JETAs-ТПС.pdf'),
        (r'РТМ-TESD-и-TESDs\.pdf', lambda m: f'{D}common/РП-TESD-TESDs.pdf'),
        (r'Рекомендации-по-выбору-.*радиатора.*\.pdf', lambda m: f'{D}common/Рекомендации-по-выбору-радиатора.pdf'),
        (r'Каталог-продукции-2026\.pdf', lambda m: 'assets/catalog-2026-2027.pdf'),
        # 3D-модели: отдельные модели и старые архивы → архив серии на новом сайте
        (r'JETAs\d+-230.*\.(?:stp|zip)', lambda m: f'{D}jetas/3D-JETAs.zip'),
        (r'(TEFA|TEFD|TEFS)-?\d+\.stp', lambda m: f'{D}{m[1].lower()}/3D-{m[1]}.zip'),
        (r'TESAV\d+-230.*\.(?:stp|zip)', lambda m: f'{D}tesav/3D-TESAV.zip'),
        (r'TESDs.*\.(?:stp|zip)', lambda m: f'{D}tesds/3D-TESDs.zip'),
        (r'TESD\d+-28W.*\.(?:stp|zip)', lambda m: f'{D}tesd/3D-TESD.zip'),
        (r'TESH\d+-150W.*\.(?:stp|zip)', lambda m: f'{D}tesh/3D-TESH.zip'),
        (r'ТПС-\d+\.stp', lambda m: f'{D}tps/3D-ТПС.zip'),
        (r'ТПФ15-380\.stp', lambda m: f'{D}tpf/3D-ТПФ.zip'),
    ]
    for pat, fn in rules:
        m = re.fullmatch(pat, n)
        if m:
            return fn(m)
    return None

rows, missing = [], []
def add(old, new, kind, title):
    assert new == '' or os.path.exists(os.path.join(ROOT, new)), f'нет на новом сайте: {new} (для {old})'
    rows.append((old, new, kind, title))

for p in data['pages']:
    slug = unquote(p['slug'])
    add(f'/{slug}/', PAGES[slug], 'страница', p['title'])
for p in data['products']:
    slug = unquote(p['slug'])
    add(f'/product/{slug}/', PRODUCTS[slug], 'товар', p['title'])
for p in data['posts']:
    add(f'/{unquote(p["slug"])}/', POSTS.get(p['id'], 'novosti.html'), 'новость', re.sub(r'<[^>]+>', '', p['title']))
for u in data['uploads']:
    t = upload_target(u.rsplit('/', 1)[1])
    if t and os.path.exists(os.path.join(ROOT, t)):
        add(u, t, 'файл', '')
    else:
        missing.append(u)

assert len({r[0] for r in rows}) == len(rows), 'повторяющиеся старые адреса'
os.makedirs(OUT, exist_ok=True)
def full(new):
    return TARGET + quote(new, safe='/.-_')

with io.open(os.path.join(OUT, 'redirects.csv'), 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['Тип', 'Старый адрес (te-power.ru)', 'Новый адрес', 'Название на старом сайте'])
    for old, new, kind, title in rows:
        w.writerow([kind, 'https://te-power.ru' + old, full(new), title])
# Redirection (WordPress): source, target, regex, code
with io.open(os.path.join(OUT, 'wp-redirection.csv'), 'w', encoding='utf-8', newline='') as f:
    w = csv.writer(f)
    for old, new, _, _ in rows:
        w.writerow([quote(old, safe='/.-_'), full(new), 0, 301])
# Apache: сравнение идёт с раскодированным путём, поэтому кириллица — как есть
with io.open(os.path.join(OUT, 'htaccess.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# Переадресация на новый сайт. Вставить в начало .htaccess в корне старого сайта (до блока WordPress).\n')
    for old, new, _, _ in rows:
        f.write(f'Redirect 301 "{old}" "{full(new)}"\n')
with io.open(os.path.join(OUT, 'nginx.conf'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# Переадресация на новый сайт: вставить в блок server { … } старого сайта.\n')
    for old, new, _, _ in rows:
        f.write(f'location = "{old}" {{ return 301 {full(new)}; }}\n')
# .htaccess нового сайта на хостинге REG.RU (te-power.ru): переадресации старых адресов WordPress на этом же домене.
# На GitHub Pages файл не действует, выкладывается на хостинг вместе с сайтом.
DOMAIN = 'https://te-power.ru/'
# Политика источников: скрипты и стили только свои (плюс встроенные в страницы) и шрифты с этого же сайта,
# заявки — на send.php этого же сайта. Сайт нельзя встроить в чужой фрейм.
CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
       "font-src 'self'; img-src 'self' data:; connect-src 'self'; "
       "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'")
with io.open(os.path.join(ROOT, '.htaccess'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# Собирается tools/build_redirects.py — вручную не править.\n'
            'AddDefaultCharset UTF-8\n'
            'DirectoryIndex index.html\n'          # главная — index.html, даже если на сервере остался index.php WordPress
            'Options -Indexes\n'
            'ErrorDocument 404 /404.html\n\n'
            '# Служебные файлы (.git, .env и т.п.) не отдаются\n'
            '<FilesMatch "^\\.">\n  Require all denied\n</FilesMatch>\n\n'
            '# Заголовки безопасности\n'
            '<IfModule mod_headers.c>\n'
            '  Header always set X-Content-Type-Options "nosniff"\n'
            '  Header always set X-Frame-Options "SAMEORIGIN"\n'
            '  Header always set Referrer-Policy "strict-origin-when-cross-origin"\n'
            '  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"\n'
            f'  Header always set Content-Security-Policy "{CSP}"\n'
            '  # страницы браузер каждый раз сверяет с сервером (не изменилась — короткий ответ 304),\n'
            '  # чтобы после выкладки посетители сразу видели новую версию\n'
            '  <FilesMatch "\\.html$">\n    Header set Cache-Control "no-cache"\n  </FilesMatch>\n'
            '</IfModule>\n\n'
            '# Старые адреса te-power.ru (WordPress) → страницы и файлы нового сайта\n')
    for old, new, _, _ in rows:
        if old.rstrip('/') and new != '':
            f.write(f'Redirect 301 "{old}" "{DOMAIN}{quote(new, safe="/.-_")}"\n')
        elif old.rstrip('/'):
            f.write(f'Redirect 301 "{old}" "{DOMAIN}"\n')

with io.open(os.path.join(OUT, 'not-mapped.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('# Файлы старого сайта, которым на новом сайте нет замены (старые серии, каталоги прошлых лет, презентации).\n')
    f.write('\n'.join(missing) + '\n')

kinds = {}
for r in rows:
    kinds[r[2]] = kinds.get(r[2], 0) + 1
print('redirects:', len(rows), kinds, '| без замены:', len(missing))
