# Метатеги всех страниц: описание, превью для соцсетей и мессенджеров (Open Graph), canonical, иконка сайта.
# Запускается последним в build_all.py: генераторы копируют шапку страниц, а этот скрипт переписывает
# блок между <!-- meta --> и <!-- /meta --> на каждой странице. Плюс sitemap.xml и robots.txt.
import datetime, glob, hashlib, html, io, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
BASE = 'https://korolevandrey13.github.io/TE-power/'  # адрес сайта; при переезде на свой домен поменять здесь
BASE_PATH = '/' + BASE.split('/', 3)[3]  # путь сайта на хосте: '/TE-power/'
SITE = 'TE-POWER'
DEFAULT_IMAGE = 'assets/catalog-cover-2026.jpg'
NOINDEX = {'korzina.html'}  # корзина — личная страница посетителя, в поиске не нужна

DESCRIPTIONS = {
    'index.html': 'ООО «ТЕ» — российский разработчик и производитель модулей электропитания: DC/DC и AC/DC преобразователи, '
                  'инверторы, модули и дроссели фильтрации. Расширенная гарантия 20 лет.',
    'produktsiya.html': 'Каталог продукции ООО «ТЕ»: DC/DC и AC/DC преобразователи TESD, TESDs, TESH, ТЕН, ТПС, JETAs, TESAV, '
                        'инверторы ТПИ, модули фильтрации TEFD, TEFA, ТПФ и дроссели ДФТ.',
    'novosti.html': 'Новости ООО «ТЕ»: новые серии модулей электропитания, аналоги импортных модулей и события компании.',
    'podderzhka.html': 'Техническая поддержка ООО «ТЕ»: технические условия, даташиты, руководства по применению и 3D-модели '
                       'модулей электропитания.',
    'o-kompanii.html': 'ООО «ТЕ» (Воронеж) — разработка и производство модулей электропитания полного цикла в России.',
    'kontakty.html': 'Контакты ООО «ТЕ»: Воронеж, ул. Комиссаржевской, 10. Телефон +7 (473) 257-40-41, russia@te-power.ru.',
    'korzina.html': 'Корзина: выбранные модули и отправка заявки в ООО «ТЕ».',
}

def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def clip(s, n=200):
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0].rstrip(',;:—–- ') + '…'

def describe(rel, page):
    if rel in DESCRIPTIONS:
        return DESCRIPTIONS[rel]
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', page, re.S)
    h1 = text(h1.group(1)) if h1 else ''
    if rel.startswith('novosti/'):
        body = re.search(r'<div class="news-article__body">(.*?)</div>', page, re.S)
        return clip(text(body.group(1)) if body else h1)
    sub = re.search(r'<p class="series-hero__subtitle">(.*?)</p>', page, re.S)
    sub = text(sub.group(1)) if sub else ''
    return clip(f'{h1} — {sub}. Модельный ряд, характеристики и документация. Производство ООО «ТЕ», Россия.')

def image(rel, page):
    m = (re.search(r'<div class="series-intro__photo"><img src="([^"]+)"', page)
         or re.search(r'<img src="([^"]+)"[^>]*class="news-article__img"', page))
    if not m or m.group(1).startswith('http'):
        return BASE + DEFAULT_IMAGE
    return BASE + os.path.normpath(os.path.join(os.path.dirname(rel), m.group(1))).replace(os.sep, '/')

def esc(s):
    return html.escape(s, quote=True)

# Метка версии у style.css и theme.js (style.css?v=…): хостинг разрешает браузерам хранить их 45 дней,
# а с меткой новая версия файла подхватывается сразу после выкладки.
ASSET_VER = {name: hashlib.sha256(io.open(os.path.join(ROOT, name), 'rb').read()).hexdigest()[:10] for name in ('style.css', 'theme.js')}
def versioned(page):
    return re.sub(r'((?:\.\./)?(style\.css|theme\.js))(?:\?v=[0-9a-f]*)?"', lambda m: f'{m.group(1)}?v={ASSET_VER[m.group(2)]}"', page)

pages = sorted(f.replace(os.sep, '/') for f in glob.glob('*.html', root_dir=ROOT) + glob.glob('serii/*.html', root_dir=ROOT)
               + glob.glob('novosti/*.html', root_dir=ROOT) if f != '404.html')  # 404 собирает build_404.py
sitemap = []
for rel in pages:
    path = os.path.join(ROOT, rel)
    raw = io.open(path, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in raw else '\n'
    page = raw.replace('\r\n', '\n')
    if 'http-equiv="refresh"' in page:  # страница-перенаправление: только запрет индексации
        if 'name="robots"' not in page:
            page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="robots" content="noindex">', 1)
            io.open(path, 'w', encoding='utf-8', newline='').write(page.replace('\n', nl))
        continue
    page = re.sub(r'\n?<!-- meta -->.*?<!-- /meta -->', '', page, flags=re.S)
    title = text(re.search(r'<title>(.*?)</title>', page, re.S).group(1))
    url = BASE + ('' if rel == 'index.html' else rel)
    prefix = '../' if '/' in rel else ''
    desc = describe(rel, page)
    tags = [
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="canonical" href="{url}">',
        f'<link rel="icon" type="image/png" href="{prefix}assets/favicon.png">',
        f'<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">',
        '<meta name="theme-color" content="#215FA6">',
        '<meta property="og:locale" content="ru_RU">',
        f'<meta property="og:site_name" content="{SITE}">',
        f'<meta property="og:type" content="{"article" if rel.startswith("novosti/") else "website"}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image(rel, page)}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if rel in NOINDEX:
        tags.insert(0, '<meta name="robots" content="noindex">')
    block = '<!-- meta -->\n' + '\n'.join(tags) + '\n<!-- /meta -->'
    page = versioned(re.sub(r'(<title>.*?</title>)', lambda m: m.group(1) + '\n' + block, page, count=1, flags=re.S))
    io.open(path, 'w', encoding='utf-8', newline='').write(page.replace('\n', nl))
    if rel not in NOINDEX:
        # дата последнего коммита страницы; если страница только что изменена и ещё не сохранена в git — сегодня
        changed = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        date = datetime.date.today().isoformat() if changed else \
            subprocess.run(['git', 'log', '-1', '--format=%cs', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        sitemap.append(f'  <url><loc>{url}</loc>' + (f'<lastmod>{date}</lastmod>' if date else '') + '</url>')

io.open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + '\n'.join(sitemap) + '\n</urlset>\n')
io.open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(
    f'User-agent: *\nDisallow: {BASE_PATH}tools/\nDisallow: {BASE_PATH}admin/\nDisallow: {BASE_PATH}korzina.html\n\nSitemap: {BASE}sitemap.xml\n')
print('meta:', len(pages), 'pages, sitemap:', len(sitemap), 'urls')
