# Документы, добавленные через админку, — на страницы серий.
# Запускается после генераторов страниц: в блок «Документация серии» страницы serii/<серия>.html дописывает
# PDF из content/docs/<серия>/ с именами ТУ-… и ДШ-…, которых в блоке ещё нет (ТУ — в начало, даташиты — после имеющихся).
import io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
KIND = {'ТУ': ('tu', 'Технические условия'), 'ДШ': ('ds', 'Даташит')}
added = 0
for s in json.load(io.open(os.path.join(ROOT, 'content', 'series.json'), encoding='utf-8')):
    page = os.path.join(ROOT, 'serii', f'{s["slug"]}.html')
    folder = os.path.join(ROOT, 'content', 'docs', s['slug'])
    if not (os.path.isfile(page) and os.path.isdir(folder)):
        continue
    raw = io.open(page, encoding='utf-8', newline='').read()
    m = re.search(r'(<h2 class="series-intro__title">Документация серии</h2>\s*<ul class="doc-list">)(.*?)(\s*</ul>)', raw, re.S)
    if not m:
        continue
    items = re.findall(r'\s*<li>.*?</li>', m.group(2), re.S)
    indent = re.match(r'\s*', items[0]).group(0) if items else '\n    '
    new_tu, new_ds = [], []
    for fn in sorted(os.listdir(folder)):
        k = re.match(r'(ТУ|ДШ)-(.+)\.pdf$', fn, re.I)
        href = f'../content/docs/{s["slug"]}/{fn}'
        if not k or f'href="{href}"' in m.group(2):
            continue
        t = k.group(1).upper()
        cls, word = KIND[t]
        li = (f'{indent}<li><a class="doc-list__link" href="{href}" target="_blank" rel="noreferrer">'
              f'<span class="doc-icon doc-icon--{cls}">{t}</span>{word} {k.group(2)}</a></li>')
        (new_tu if t == 'ТУ' else new_ds).append(li)
    if not (new_tu or new_ds):
        continue
    last = max([i for i, li in enumerate(items) if 'doc-icon--tu' in li or 'doc-icon--ds' in li], default=-1)
    items = new_tu + items[:last + 1] + new_ds + items[last + 1:]
    raw = raw[:m.start(2)] + ''.join(items) + raw[m.end(2):]
    io.open(page, 'w', encoding='utf-8', newline='').write(raw)
    added += len(new_tu) + len(new_ds)
print('series docs: added', added)
