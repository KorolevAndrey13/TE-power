# Страницы серии ТПИ (DC/AC инверторы): страница серии + страницы типоразмеров ТПИ200 и ТПИ2500.
# Данные: каталог 2026–2027 (стр. 5, 17) и новость о ТПИ.
# Наименование по каталогу: ТПИ200-27220-КЛ = серия+мощность, вход 27, выход (115/220), корпус (У/К), температура (Л).
# Выход по типоразмеру — из таблицы каталога (ТПИ200 ~115 В 400 Гц, ТПИ2500 ~220 В 50 Гц).
# Ток — P/U (действующее значение).
import io, re, os
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
tpl = io.open(os.path.join(ROOT, 'serii/tpd.html'), encoding='utf-8').read().replace('\r\n', '\n')
HEAD = tpl[:tpl.index('<div class="wrap breadcrumbs">')]
FOOT = tpl[tpl.index('<footer class="footer">'):]

DS200 = 'http://te-power.ru/wp-content/uploads/TПИ200.pdf'
DS2500 = 'http://te-power.ru/wp-content/uploads/TПИ2500.pdf'
PHOTO = '../content/images/tpi200.webp'
CART_SVG = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 4h2.2l2.1 10.2a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.1L20.5 8H6.1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9.5" cy="19.5" r="1.4" fill="currentColor"/><circle cx="17" cy="19.5" r="1.4" fill="currentColor"/></svg>'
REQ = 'Модули с нестандартным выходным напряжением — по запросу: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>.'

INPUT = ('27', '=27 В (24…30 В)')
BODIES = [('У', 'усиленный корпус с фланцами', 'с фланцами'), ('К', 'основание с крышкой и клеммными колодками', 'с клеммными колодками')]
TEMP = ('Л', '−40…+85 °C')
SIZES = [
    dict(slug='tpi200', name='ТПИ200', models=[('ТПИ200', 200), ('ТПИ250', 250)], dims='122×84,2×15',
         out_code='115', out='~115 В, 400 Гц', ds=DS200),
    dict(slug='tpi2500', name='ТПИ2500', models=[('ТПИ2500', 2500)], dims='280×170×48',
         out_code='220', out='~220 В, 50 Гц', ds=DS2500),
]

def fmt(v):
    q = Decimal('0.01') if v < 10 else Decimal('0.1')
    s = str(Decimal(str(v)).quantize(q, ROUND_HALF_UP)).rstrip('0').rstrip('.')
    return s.replace('.', ',')

def current(p, size):
    return fmt(p / float(size['out_code']))

def ds_cell(href, rowspan=''):
    return (f'  <td{rowspan}><a class="series-models__ds" href="{href}" target="_blank" rel="noreferrer" title="Даташит (PDF)">'
            f'<span class="doc-icon doc-icon--ds">ДШ</span></a></td>')

def page_head(title):
    return re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', HEAD, count=1)

# ---------- страница серии ----------
rows = []
TOTAL = sum(len(x['models']) for x in SIZES)
for si, s in enumerate(SIZES):
    n = len(s['models'])
    r = f' rowspan="{n}"' if n > 1 else ''
    for i, (m, p) in enumerate(s['models']):
        rows.append('<tr class="series-models__group-start">' if i == 0 else '<tr>')
        if i == 0:
            rows.append(f'  <td{r} class="series-models__name"><a class="series-models__model" href="{s["slug"]}.html">{s["name"]}</a></td>')
        rows.append(f'  <td class="series-models__per">{p} Вт</td>')
        if i == 0:
            rows.append(f'  <td{r}><span class="series-models__line">{s["dims"]}</span></td>')
            if si == 0:
                rows.append(f'  <td rowspan="{TOTAL}" class="series-models__inputs"><span class="series-models__line"><b>{INPUT[0]}</b> — 27 В (24…30 В)</span></td>')
            rows.append(f'  <td{r}>{s["out"]}</td>')
        rows.append(f'  <td class="series-models__per">{current(p, s)} А</td>')
        if i == 0:
            if si == 0:
                rows.append(f'  <td rowspan="{TOTAL}">не менее 82 %</td>')
            rows.append(ds_cell(s['ds'], r))
        rows.append('</tr>')

series_body = f'''<div class="wrap breadcrumbs"><a href="../produktsiya.html" class="breadcrumbs__link">Продукция</a> / <a href="../produktsiya.html#invertory" class="breadcrumbs__link">Инверторы</a> / ТПИ</div>
<section class="series-hero series-hero--plain"><div class="wrap series-hero__row">
  <div><h1 class="series-hero__title">ТПИ <span class="series-hero__badge">Новинка</span></h1><p class="series-hero__subtitle">Отечественные DC/AC инверторы</p></div>
</div></section>
<div class="wrap series-page">
<section class="series-intro">
  <div class="series-intro__col">
    <h2 class="series-intro__title">Особенности</h2>
    <ul class="check-list">
      <li>Преобразование постоянного тока в переменный для задач:
        <ul class="check-list__sub"><li>автономные энергосистемы на базе солнечных панелей и ветрогенераторов;</li><li>резервные источники питания;</li><li>мобильные и переносные энергоустановки;</li><li>промышленное оборудование.</li></ul>
      </li>
      <li>Выходная мощность от 200 до 2500 Вт</li>
      <li>Выходное напряжение ~115 В, 400 Гц или ~220 В, 50 Гц</li>
      <li>Входное напряжение 27 В (24…30 В) по ГОСТ 19705</li>
      <li>Коэффициент искажения синусоидальной кривой выходного напряжения не более 2 %</li>
      <li>КПД не менее 82 %</li>
      <li>Рабочая температура корпуса −40…+85 °C</li>
      <li>Фрезерованный алюминиевый корпус с металлической крышкой</li>
      <li>Дистанционное управление</li>
      <li>Прочность изоляции вход/выход 1500 В</li>
      <li>Срок поставки — от 5 рабочих дней с момента оформления заказа</li>
      <li>Расширенная гарантия 20 лет</li>
    </ul>
  </div>
  <div class="series-intro__col">
    <div class="series-intro__photo"><img src="{PHOTO}" alt="Инверторы ТПИ"></div>
    <h2 class="series-intro__title">Документация серии</h2>
    <ul class="doc-list">
      <li><a class="doc-list__link" href="{DS200}" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--ds">ДШ</span>Даташит ТПИ200</a></li>
      <li><a class="doc-list__link" href="{DS2500}" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--ds">ДШ</span>Даташит ТПИ2500</a></li>
    </ul>
    <p class="series-intro__more">Технические характеристики и расчёт стоимости — по запросу у менеджера: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>, <a href="tel:+74732574041" class="note__link">+7 (473) 257-40-41</a>.</p>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модели</h2>
  <div class="series-models__scroll">
  <table class="series-models__table">
  <thead><tr><th>Типоразмер</th><th>Мощность</th><th>Размеры**, мм</th><th>Входное напряжение</th><th>Выходное напряжение*</th><th>Макс. вых. ток</th><th>КПД</th><th>Даташит</th></tr></thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
  </table>
  </div>
  <div class="series-models__notes">
    <p>* {REQ}</p>
    <p>** Без учёта длины выводов.</p>
  </div>
</section>
</div>

'''
io.open(os.path.join(ROOT, 'serii/tpi.html'), 'w', encoding='utf-8', newline='').write(page_head('ТПИ — TE-POWER') + series_body + FOOT)
print('tpi series ok')

# ---------- страницы типоразмеров ----------
def opts(pairs):
    return '<option value="">Не выбрано</option>' + ''.join(f'<option value="{v}">{t}</option>' for v, t in pairs)

def merge_rows(matrix, merge_cols, group_starts):
    # matrix: строки из ячеек (html, ключ); в столбцах merge_cols одинаковые соседние ключи -> одна ячейка с rowspan
    n = len(matrix)
    span = [[1] * len(matrix[0]) for _ in range(n)]
    for c in merge_cols:
        r = 0
        while r < n:
            k = r
            while k + 1 < n and matrix[k + 1][c][1] == matrix[r][c][1]:
                k += 1
            span[r][c] = k - r + 1
            for j in range(r + 1, k + 1):
                span[j][c] = 0
            r = k + 1
    out = []
    for r, row in enumerate(matrix):
        cells = []
        for c, (html, _) in enumerate(row):
            if span[r][c] == 0:
                continue
            rs = f' rowspan="{span[r][c]}"' if span[r][c] > 1 else ''
            cells.append(html.replace('<td', f'<td{rs}', 1))
        cls = ' class="series-models__group-start"' if r in group_starts and r else ''
        out.append(f'<tr{cls}>' + ''.join(cells) + '</tr>')
    return out

for s in SIZES:
    matrix, group_starts = [], set()
    for m, p in s['models']:
        i = current(p, s)
        group_starts.add(len(matrix))
        for b, blabel, bshort in BODIES:
            nm = f'{m}-{INPUT[0]}{s["out_code"]}-{b}{TEMP[0]}'
            desc = f'{p} Вт; вход {INPUT[1]}; выход {s["out"]}; корпус: {blabel}; {s["dims"]} мм; {TEMP[1]}'
            matrix.append([
                (f'<td class="size-models__name">{nm}</td>', nm),
                (f'<td>{p} Вт</td>', (m, p)),
                (f'<td>{INPUT[1]}</td>', INPUT[1]),
                (f'<td>{s["out"]}</td>', s['out']),
                (f'<td>{i} А</td>', (m, i)),
                (f'<td><b>{b}</b> — {bshort}</td>', nm),
                (f'<td>{s["dims"]} мм</td>', s['dims']),
                (f'<td>{TEMP[1]}</td>', TEMP[1]),
                (f'<td><button type="button" class="cart-btn" data-cart-name="{nm}" data-cart-desc="{desc}" title="Добавить в корзину" aria-label="Добавить {nm} в корзину">{CART_SVG}</button></td>', nm),
            ])
    rows = merge_rows(matrix, merge_cols=[1, 2, 3, 4, 6, 7], group_starts=group_starts)
    powers = [p for _, p in s['models']]
    params = [
        ('Модели', ', '.join(m for m, _ in s['models'])),
        ('Мощность', f'{powers[0]}–{powers[-1]} Вт' if len(powers) > 1 else f'{powers[0]} Вт'),
        ('Входное напряжение', '27 В (24…30 В)'),
        ('Выходное напряжение', s['out']),
        ('Габариты', f'{s["dims"]} мм'),
        ('Исполнение корпуса', [f'{b} — {t}' for b, t, _ in BODIES]),
        ('Температура корпуса', TEMP[1]),
        ('КПД', 'не менее 82 %'),
        ('Искажение синусоиды', 'не более 2 %'),
        ('Гарантия', '20 лет'),
    ]
    def val(v):
        return ''.join(f'<span class="spec-panel__row-line">{x}</span>' for x in v) if isinstance(v, list) else v
    params_html = ''.join(f'<div class="spec-panel__row"><span>{a}</span><span class="spec-panel__row-value">{val(v)}</span></div>' for a, v in params)
    body = f'''<div class="wrap breadcrumbs"><a href="../produktsiya.html" class="breadcrumbs__link">Продукция</a> / <a href="../produktsiya.html#invertory" class="breadcrumbs__link">Инверторы</a> / <a href="tpi.html" class="breadcrumbs__link">ТПИ</a> / {s['name']}</div>
<section class="series-hero series-hero--plain"><div class="wrap series-hero__row">
  <div><h1 class="series-hero__title">{s['name']}</h1><p class="series-hero__subtitle">Отечественные DC/AC инверторы</p></div>
</div></section>
<div class="wrap series-page">
<section class="series-intro">
  <div class="series-intro__col">
    <h2 class="series-intro__title">Описание типоразмера</h2>
    {params_html}
  </div>
  <div class="series-intro__col">
    <div class="series-intro__photo"><img src="{PHOTO}" alt="Инвертор {s['name']}"></div>
    <h2 class="series-intro__title">Документация</h2>
    <ul class="doc-list">
      <li><a class="doc-list__link" href="{s['ds']}" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--ds">ДШ</span>Даташит {s['name']}</a></li>
    </ul>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модельный ряд {s['name']}</h2>
  <div class="series-models__scroll">
  <table class="series-models__table size-models size-models--merged">
  <thead>
  <tr><th>Наименование</th><th>Мощность</th><th>Входное напряжение</th><th>Выходное напряжение*</th><th>Макс. вых. ток</th><th>Исполнение корпуса</th><th>Размеры**</th><th>Диапазон рабочих температур</th><th>Заказ</th></tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
  </table>
  </div>
  <div class="series-models__notes">
    <p>* {REQ}</p>
    <p>** Без учёта длины выводов.</p>
  </div>
</section>

<div class="series-related">
  <span class="series-related__title">Вернуться к серии:</span>
  <a href="tpi.html" class="series-related__link">ТПИ — все типоразмеры</a>
</div>
</div>

'''
    io.open(os.path.join(ROOT, f'serii/{s["slug"]}.html'), 'w', encoding='utf-8', newline='').write(page_head(f'{s["name"]} — ТПИ — TE-POWER') + body + FOOT)
    print('  ', s['slug'], len(rows), 'rows')
