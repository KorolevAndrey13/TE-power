# Перестраивает раздел «Документация» на podderzhka.html: слева — серии, справа — документы выбранной серии.
import io, re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
P = os.path.join(ROOT, 'podderzhka.html')
h = io.open(P, encoding='utf-8').read().replace('\r\n', '\n')
# исходный список документов — таблица из копии страницы до перестройки
src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'podderzhka-original.html'), encoding='utf-8').read()

# текущие документы из таблицы
docs = []
for m in re.finditer(r'<tr data-series="([^"]+)" data-type="([^"]+)"[^>]*>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*<td>([^<]*)</td>\s*<td><a href="([^"]+)"', src):
    docs.append(dict(series=m.group(1), type=m.group(2), name=m.group(3), href=m.group(4)))
assert docs, 'документы не найдены'
# даташиты TESDs (добавлены в content/docs/tesds)
docs += [dict(series='tesds', type='ДШ', name=f'TESDs{n}', href=f'content/docs/tesds/ДШ-TESDs{n}.pdf') for n in (15, 25, 40, 60, 150, 300, 500)]
# ТПД и ТПИ — документы пока на старом сайте
docs += [
    dict(series='tpd', type='ДШ', name='ТПД (описание серии)', href='http://te-power.ru/wp-content/uploads/ТПД.pdf'),
    dict(series='tpi', type='ДШ', name='ТПИ200', href='http://te-power.ru/wp-content/uploads/TПИ200.pdf'),
    dict(series='tpi', type='ДШ', name='ТПИ2500', href='http://te-power.ru/wp-content/uploads/TПИ2500.pdf'),
]

GROUPS = [
    ('DC/DC модули', [('tesd', 'TESD'), ('tesds', 'TESDs'), ('tesh', 'TESH'), ('teh', 'TEH (ТЕН)'), ('tpd', 'ТПД')]),
    ('AC/DC модули', [('tps', 'ТПС'), ('jetas', 'JETAs'), ('tesav', 'TESAV')]),
    ('Инверторы', [('tpi', 'ТПИ')]),
    ('Модули фильтрации', [('tefd', 'TEFD'), ('tefs', 'TEFS'), ('tpf', 'ТПФ'), ('tefa', 'TEFA')]),
    ('Дроссели фильтрации', [('dft', 'ДФТ, ДФТК'), ('dftp', 'ДФТП, ДФТПК')]),
]
TYPES = [('ТУ', 'tu', 'Технические условия'), ('ДШ', 'ds', 'Даташиты'), ('3D', '3d', '3D-модели и чертежи')]
TYPE_LABEL = {'ТУ': 'Технические условия', 'ДШ': 'Даташит', '3D': '3D-модель'}
DL_SVG = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 4v11m0 0l-4.5-4.5M12 15l4.5-4.5M5 19.5h14" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>'

series_names = {k: v for _, items in GROUPS for k, v in items}
known = set(series_names)
assert all(d['series'] in known for d in docs), {d['series'] for d in docs} - known

nav, sections = [], []
first = GROUPS[0][1][0][0]
for gtitle, items in GROUPS:
    nav.append(f'<div class="docs-browser__group">{gtitle}</div>')
    for key, title in items:
        own = [d for d in docs if d['series'] == key]
        cls = ' docs-browser__series-btn--active' if key == first else ''
        nav.append(f'<button type="button" class="docs-browser__series-btn{cls}" data-series="{key}" onclick="selectDocsSeries(\'{key}\')">'
                   f'<span>{title}</span><span class="docs-browser__count">{len(own)}</span></button>')
        blocks = []
        for t, c, tl in TYPES:
            items_t = [d for d in own if d['type'] == t]
            if not items_t:
                continue
            lis = []
            for d in items_t:
                label = f'{TYPE_LABEL[t]} {d["name"]}'
                search = f'{t} {title} {TYPE_LABEL[t]} {d["name"]}'.lower()
                external = d['href'].startswith('http')
                dl = '' if external else ' download'
                lis.append(
                    f'<li class="docs-browser__item" data-type="{t}" data-search="{search}">'
                    f'<a class="docs-browser__doc" href="{d["href"]}" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--{c}">{t}</span><span>{label}</span></a>'
                    f'<a class="docs-browser__dl" href="{d["href"]}"{dl} target="_blank" rel="noreferrer" title="Скачать" aria-label="Скачать: {label}">{DL_SVG}</a></li>')
            blocks.append(f'<div class="docs-browser__type" data-type="{t}"><h4 class="docs-browser__type-title">{tl}</h4><ul class="docs-browser__list">{"".join(lis)}</ul></div>')
        hidden = '' if key == first else ' hidden'
        sections.append(
            f'<section class="docs-browser__section" data-series="{key}"{hidden}>'
            f'<div class="docs-browser__head"><h3 class="docs-browser__title">{title}</h3><a href="serii/{key}.html" class="docs-browser__series-link">Страница серии →</a></div>'
            + ''.join(blocks) +
            f'<p class="docs-browser__none"{" hidden" if own else ""}>Документы по этой серии скоро появятся. Их можно запросить у менеджера: '
            f'<a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>.</p></section>')

series_opts = '<option value="">Все серии</option>' + ''.join(f'<option value="{k}">{v}</option>' for _, items in GROUPS for k, v in items)
type_opts = '<option value="">Все типы</option>' + ''.join(f'<option value="{t}">{TYPE_LABEL[t] if t != "ДШ" else "Даташит"}</option>' for t, _, _ in TYPES).replace('>3D-модель<', '>3D-модель / чертёж<')

block = f'''    <h2 class="section__title">Документация</h2>
    <div class="docs-filter">
  <input id="docs-search" type="text" placeholder="Поиск по названию…" class="docs-filter__input" oninput="filterDocs()">
  <select id="docs-filter-series" class="docs-filter__select" onchange="selectDocsSeries(this.value)">{series_opts}</select>
  <select id="docs-filter-type" class="docs-filter__select" onchange="filterDocs()">{type_opts}</select>
</div>
<div class="docs-browser" data-first="{first}">
  <nav class="docs-browser__series" aria-label="Серии">
    {chr(10).join('    ' + n for n in nav).strip()}
  </nav>
  <div class="docs-browser__panel">
    <p class="docs-browser__hint" hidden></p>
    {chr(10).join('    ' + s for s in sections).strip()}
    <div id="docs-empty" class="note" hidden>Ничего не найдено — попробуйте другой запрос.</div>
  </div>
</div>
'''
a = h.index('    <h2 class="section__title">Документация</h2>')
b = h.index('<div id="docs-empty"')
b = h.index('</div>', b) + len('</div>\n')
if '<div class="docs-browser"' in h[a:b + 200]:   # повторный запуск: заменить уже собранный блок целиком
    b = h.index('</div>\n</div>\n', b) + len('</div>\n</div>\n')
h = h[:a] + block + h[b:]
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('docs:', len(docs), 'series:', len(series_names))
