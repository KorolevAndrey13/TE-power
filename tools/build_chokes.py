# Страницы дросселей фильтрации (ДФТ/ДФТК, ДФТП/ДФТПК) по образцу TESD — страница серии с таблицей типоразмеров.
# Источник: каталог 2026–2027, стр. 12. Перечня номинальных токов по исполнениям нет — страниц типоразмеров нет.
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
CAT = ('Дроссели фильтрации', 'drosseli')
FEATURES = [
    'Полные аналоги (pin-to-pin) дросселей фильтрации серий ДФ, ДФК, ДФП, ДФПК',
    'Двухобмоточные дроссели — с подмагничиванием и без',
    'Проходной ток от 0,1 до 20 А, индуктивность от 0,12 до 11 мГн',
    'Рабочая температура корпуса до −60…+105 °C',
    'Металлический корпус с защитным покрытием',
    'Используются исключительно отечественные комплектующие, произведено в России',
    'Рекомендуются к применению совместно с модулями серий TESD, TESDs, TESH',
    'Расширенная гарантия 20 лет',
]
CODE = ('Пример наименования: <b>ДФТК7,5-2А4,0</b> — тип дросселя (ДФТК7,5), электрическая схема (2 — двухобмоточная), '
        'номинальное входное напряжение (А — 12 В, В — 27 В, Д — 60 В, Н — 110 В, М — 230 В, Р — 5 В) и номинальный проходной ток, А (4,0).')
# ТУ общие для ДФТ, ДФТК, ДФТП, ДФТПК
DOCS = ('<ul class="doc-list">\n      <li><a class="doc-list__link" href="../content/docs/dft/ТУ-ДФТ.pdf" target="_blank" rel="noreferrer">'
        '<span class="doc-icon doc-icon--tu">ТУ</span>Технические условия ТЛДР.670109.001 ТУ</a></li>\n    </ul>\n    ')
SERIES = [
 dict(slug='dft', title='ДФТ, ДФТК', subtitle='Дроссели фильтрации для DC сетей',
      types=[('ДФТК7,5', '0,2–1,5', '14,5×14,5×10', '790–3600', '196–900', '0,8'),
             ('ДФТК15', '0,4–3', '18×18×10', '900–4600*', '230–1166', '1'),
             ('ДФТК30', '0,3–6', '22×22×10', '350–11000', '90–2822', '1'),
             ('ДФТК60', '0,6–10', '26×26×12,5', '350–8900', '90–2250', '1,2'),
             ('ДФТК120', '1,1–20', '26×26×12,5', '120–6800', '32–1742', '1,2'),
             ('ДФТК240', '2,1–20', '26×26×12,5', '220–4100', '58–1040', '1,2')],
      note15=True, related=[('dftp.html', 'ДФТП, ДФТПК')]),
 dict(slug='dftp', title='ДФТП, ДФТПК', subtitle='Дроссели фильтрации для DC сетей с подмагничиванием',
      types=[('ДФТПК7,5', '0,2–4', '14,5×14,5×10', '3–715', '11–2860', '0,8'),
             ('ДФТПК15', '0,4–4', '18×18×10', '10–1075', '40–4300', '1'),
             ('ДФТПК30', '0,4–6', '22×22×10', '8–1915', '30–7660', '1'),
             ('ДФТПК60', '0,4–20', '26×26×12,5', '1–3564', '5–14250', '1,2')],
      note15=False, related=[('dft.html', 'ДФТ, ДФТК')]),
]

for ser in SERIES:
    path = os.path.join(ROOT, f'serii/{ser["slug"]}.html')
    html = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    head, foot = html[:html.index('<div class="wrap breadcrumbs">')], html[html.index('<footer class="footer">'):]
    photo = 'https://te-power.ru/wp-content/uploads/dft-2-300x239.png'
    # одинаковые соседние значения (размер, диаметр выводов) — одна ячейка
    t = ser['types']; n = len(t)
    span = [[1] * 6 for _ in range(n)]
    for c in (2, 5):
        r = 0
        while r < n:
            k = r
            while k + 1 < n and t[k + 1][c] == t[r][c]:
                k += 1
            span[r][c] = k - r + 1
            for j in range(r + 1, k + 1):
                span[j][c] = 0
            r = k + 1
    rows = []
    for r, row in enumerate(t):
        cells = []
        for c, v in enumerate(row):
            if span[r][c] == 0:
                continue
            rs = f' rowspan="{span[r][c]}"' if span[r][c] > 1 else ''
            v = f'<span class="series-models__model">{v}</span>' if c == 0 else (v + (' А' if c == 1 else ''))
            cls = ' class="series-models__name"' if c == 0 else ''
            cells.append(f'  <td{rs}{cls}>{v}</td>')
        rows.append('<tr class="series-models__group-start">\n' + '\n'.join(cells) + '\n</tr>')
    feats = '\n      '.join(f'<li>{f}</li>' for f in FEATURES)
    body = f'''<div class="wrap breadcrumbs"><a href="../produktsiya.html" class="breadcrumbs__link">Продукция</a> / <a href="../produktsiya.html#{CAT[1]}" class="breadcrumbs__link">{CAT[0]}</a> / {ser['title']}</div>
<section class="series-hero series-hero--plain"><div class="wrap series-hero__row">
  <div><h1 class="series-hero__title">{ser['title']} </h1><p class="series-hero__subtitle">{ser['subtitle']}</p></div>
</div></section>
<div class="wrap series-page">
<section class="series-intro">
  <div class="series-intro__col">
    <h2 class="series-intro__title">Особенности</h2>
    <ul class="check-list">
      {feats}
    </ul>
  </div>
  <div class="series-intro__col">
    <div class="series-intro__photo"><img src="{photo}" alt="Дроссели {ser['title']}"></div>
    <h2 class="series-intro__title">Документация серии</h2>
    {DOCS}<p class="series-intro__more">Даташиты, технические условия и 3D-модели — по запросу у менеджера: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>. Также см. страницу <a href="../podderzhka.html" class="note__link">Техническая поддержка</a>.</p>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модели</h2>
  <div class="series-models__scroll">
  <table class="series-models__table">
  <thead><tr><th>Тип</th><th>Номинальный проходной ток</th><th>Размеры**, мм</th><th>Индуктивность обмотки, мкГн (1 кГц, 1 В)</th><th>Индуктивность обмотки, мкГн (100 кГц, 1 В)</th><th>Диаметр выводов, мм</th></tr></thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
  </table>
  </div>
  <div class="series-models__notes">
    <p>{CODE}</p>
    {'<p>* В каталоге указано «900–460» — вероятно, опечатка; уточняйте у менеджера.</p>' if ser['note15'] else ''}
    <p>** Без учёта длины выводов. Индуктивность — одной обмотки, не менее.</p>
    <p>Подбор исполнения под требуемые ток и индуктивность — по запросу: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>.</p>
  </div>
</section>

<div class="series-related">
  <span class="series-related__title">Другие серии этой категории:</span>
  {''.join(f'<a href="{h}" class="series-related__link">{t_}</a>' for h, t_ in ser['related'])}
</div>
</div>

'''
    io.open(path, 'w', encoding='utf-8', newline='').write(head + body + foot)
    print(ser['slug'], len(rows), 'types')
