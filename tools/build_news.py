# Новости: страницы novosti/<slug>.html, список novosti.html и новостные слайды карусели на главной.
# Данные — content/news/<slug>.json (их же правит админка):
#   title, date (ГГГГ-ММ-ДД), image, excerpt — анонс для списка, body — текст: абзацы через пустую строку,
#   attachments — [{type: ДШ|ТУ, label, href}], related — {name, href} или null (ссылка на серию),
#   carousel — показывать на главной; carousel_style — photo (фото фоном) | product (модуль на тёмном фоне);
#   carousel_title, carousel_text, carousel_image — необязательные замены заголовка, анонса и картинки для слайда.
# Телефоны, e-mail и адреса http(s) в тексте становятся ссылками сами.
import glob, html, io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
CAROUSEL_MAX = 10  # сколько последних новостей с carousel=true показывать на главной
DOC_ICON = {'ДШ': 'ds', 'ТУ': 'tu', 'РП': 'rp', '3D': '3d'}

def esc(s):
    return html.escape(s, quote=True)

def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read().replace('\r\n', '\n')

def write(rel, s):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='\n').write(s)

def ru_date(d):
    y, m, dd = d.split('-')
    return f'{dd}.{m}.{y}'

LINK = re.compile(r'(?P<url>https?://[^\s<]+[^\s<.,;:!?)»])'
                  r'|(?P<mail>[\w.+-]+@[\w-]+(?:\.[\w-]+)+)'
                  r'|(?P<tel>(?:\+7\s?|8\s?)?\(\d{3,4}\)\s?\d{2,3}-\d{2}-\d{2})')

def linkify(text):
    out, pos = [], 0
    for m in LINK.finditer(text):
        out.append(esc(text[pos:m.start()]))
        v = m.group(0)
        if m.group('url'):
            out.append(f'<a href="{esc(v)}" class="text-link" target="_blank" rel="noreferrer">{esc(v)}</a>')
        elif m.group('mail'):
            out.append(f'<a href="mailto:{v}" class="text-link">{esc(v)}</a>')
        else:
            digits = re.sub(r'\D', '', v)
            digits = '7' + digits[1:] if digits[0] == '8' and len(digits) == 11 else ('7' + digits if len(digits) == 10 else digits)
            out.append(f'<a href="tel:+{digits}" class="text-link">{esc(v)}</a>')
        pos = m.end()
    out.append(esc(text[pos:]))
    return ''.join(out)

def body_html(body):
    paras = [p.strip() for p in re.split(r'\n\s*\n', body.replace('\r\n', '\n')) if p.strip()]
    return '\n'.join('<p>' + '<br>\n'.join(linkify(l) for l in p.split('\n')) + '</p>' for p in paras)

def to_sub(fragment):
    # относительные ссылки страницы из корня -> для страницы в novosti/
    return re.sub(r'(\s(?:href|src)=")(?!https?:|mailto:|tel:|#|/|data:|\.\./)', r'\1../', fragment)

# ---- данные ----
news = []
for f in glob.glob(os.path.join(ROOT, 'content', 'news', '*.json')):
    n = json.load(io.open(f, encoding='utf-8'))
    n['slug'] = os.path.splitext(os.path.basename(f))[0]
    assert re.fullmatch(r'[a-z0-9-]+', n['slug']), n['slug']
    assert re.fullmatch(r'\d{4}-\d\d-\d\d', n['date']), (n['slug'], n['date'])
    news.append(n)
news.sort(key=lambda n: (n['date'], n['slug']), reverse=True)

# ---- шапка и подвал: со страницы «Все новости» ----
arch = read('novosti.html')
head = arch[:arch.index('</header>') + len('</header>\n')]
foot = arch[arch.index('<footer class="footer">'):]
head = re.sub(r'\n?<!-- meta -->.*?<!-- /meta -->', '', head, flags=re.S)  # метатеги допишет build_meta.py
sub_head, sub_foot = to_sub(head), to_sub(foot)

# ---- страницы новостей ----
os.makedirs(os.path.join(ROOT, 'novosti'), exist_ok=True)
for old in glob.glob(os.path.join(ROOT, 'novosti', '*.html')):  # удалённые в админке новости
    if os.path.basename(old)[:-5] not in {n['slug'] for n in news}:
        os.remove(old)
for i, n in enumerate(news):
    t = esc(n['title'])
    att = ''.join(f'<a href="../{esc(a["href"])}" class="btn btn--line news-article__attachment" target="_blank" rel="noreferrer">'
                  f'<span class="doc-icon doc-icon--{DOC_ICON.get(a["type"], "pdf")}">{esc(a["type"])}</span>{esc(a["label"])}</a>'
                  for a in n.get('attachments') or [])
    att = f'<div class="news-article__attachments">{att}</div>' if att else ''
    rel = n.get('related')
    rel = (f'<div class="note news-article__related">Смотреть характеристики серии — '
           f'<a href="../{esc(rel["href"])}" class="text-link">{esc(rel["name"])} →</a></div>') if rel else ''
    newer, older = (news[i - 1] if i else None), (news[i + 1] if i + 1 < len(news) else None)
    pager = (f'<a href="{newer["slug"]}.html" class="news-article__pager-link">← {esc(newer["title"])}</a>' if newer else
             ('<span></span>' if older else ''))
    pager += f'<a href="{older["slug"]}.html" class="news-article__pager-link">{esc(older["title"])} →</a>' if older else ''
    page_head = re.sub(r'<title>.*?</title>', f'<title>{t} — TE-POWER</title>', sub_head, count=1)
    body = f'''<div class="wrap breadcrumbs"><a href="../novosti.html" class="breadcrumbs__link">Новости</a> / {t}</div>
<article class="wrap news-article">
  <img src="../{esc(n["image"])}" alt="{t}" class="news-article__img">
  <div class="news-article__date">{ru_date(n["date"])}</div>
  <h1 class="news-article__title">{t}</h1>
  <div class="news-article__body">
    {body_html(n["body"])}

  </div>
  {att}
  {rel}
  <div class="news-article__pager">{pager}</div>
</article>

'''
    write(f'novosti/{n["slug"]}.html', page_head + body + sub_foot)

# ---- список «Все новости» ----
items = ''.join(f'''
  <a href="novosti/{n["slug"]}.html" class="news-archive__item">
    <div class="news-archive__thumb" style="background-image:url('{esc(n["image"])}');"></div>
    <div>
      <div class="news-archive__date">{ru_date(n["date"])}</div>
      <h3 class="news-archive__title">{esc(n["title"])}</h3>
      <p class="news-archive__excerpt">{esc(n["excerpt"])}</p>
    </div>
  </a>''' for n in news)
arch = re.sub(r'<div class="news-archive">.*?\n</div>\n', lambda m: f'<div class="news-archive">{items}\n</div>\n', arch, count=1, flags=re.S)
write('novosti.html', arch)

# ---- карусель на главной: новостные слайды между <!-- news-slides --> и <!-- /news-slides --> ----
def slide(n):
    title = esc(n.get('carousel_title') or n['title'])
    text = esc(n.get('carousel_text') or n['excerpt'])
    img = esc(n.get('carousel_image') or n['image'])
    product = n.get('carousel_style') == 'product'
    cls = 'carousel__slide carousel__slide--news' + (' carousel__slide--product' if product else '')
    bg = '' if product else f''' style="background-image:url('{img}');"'''
    pic = f'\n            <img class="carousel__product-img" src="{img}" alt="{title}">' if product else ''
    return f'''
          <a href="novosti/{n["slug"]}.html" class="{cls}"{bg}>
            <div class="carousel__news-overlay">
              <div class="eyebrow carousel__news-eyebrow">Новости</div>
              <div class="carousel__news-date">{ru_date(n["date"])}</div>
              <h2 class="carousel__news-title">{title}</h2>
              <p class="carousel__news-excerpt">{text}</p>
              <span class="carousel__news-link">Читать →</span>
            </div>{pic}
          </a>
'''
idx = read('index.html')
slides = [n for n in news if n.get('carousel')][:CAROUSEL_MAX]
idx = re.sub(r'<!-- news-slides -->.*?<!-- /news-slides -->', lambda m: '<!-- news-slides -->' + ''.join(slide(n) for n in slides) + '\n          <!-- /news-slides -->',
             idx, count=1, flags=re.S)
total = len(re.findall(r'class="carousel__slide[" ]', idx))
dots = ''.join(f'\n        <button class="carousel__dot" aria-label="Слайд {k}"></button>' for k in range(1, total + 1))
idx = re.sub(r'(<div class="carousel__dots">).*?(\n      </div>)', lambda m: m.group(1) + dots + m.group(2), idx, count=1, flags=re.S)
write('index.html', idx)
print('news:', len(news), 'pages, carousel:', len(slides), 'slides of', total)
