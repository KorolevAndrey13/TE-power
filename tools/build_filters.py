# Страницы модулей фильтрации (TEFD, TEFA, ТПФ, TEFS) по образцу TESD: страница серии + страницы типоразмеров.
# Источники: каталог 2026–2027 (стр. 5, 11, 15, 16) и прежние страницы сайта (TEFS — в каталоге нет).
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
CART_SVG = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 4h2.2l2.1 10.2a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.1L20.5 8H6.1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9.5" cy="19.5" r="1.4" fill="currentColor"/><circle cx="17" cy="19.5" r="1.4" fill="currentColor"/></svg>'
CAT = ('Модули фильтрации', 'moduli-filtratsii')

SERIES = [
 dict(slug='tefd', name='TEFD', subtitle='Модули защиты и фильтрации для DC сетей',
      photo='https://te-power.ru/wp-content/uploads/TEFD5.png',
      docs=[('ТУ', 'tu', 'tefd/ТУ-TEFD.pdf', 'Технические условия TEFD')],
      inputs=[('12W', '=12 В (9…36 В)'), ('24W', '=24 В (17…84 В)')],
      bodies=[('U', 'с фланцами')], body_prefix='',
      temps=[('T', '−60…+125 °C'), ('S', '−60…+110 °C')],
      features=['Номинальный проходной ток от 2,5 до 40 А', 'Металлический корпус с крепёжными фланцами или без фланцев',
                ('Варианты входного напряжения:', ['12W — 12 В (9…36 В)', '24W — 24 В (17…84 В)']),
                'Рабочая температура корпуса до −60…+125 °C',
                ('Вносимое затухание:', ['0,15…0,3 МГц — 30 дБ;', '0,3…1 МГц — 40 дБ;', '1…10 МГц — 50 дБ;', '10…30 МГц — 60 дБ.']),
                'Максимальный импульсный ток защиты 250–1200 А', 'Прочность изоляции вход/корпус, выход/корпус 1000 В',
                'Согласованы по посадочным размерам с модулями серии TESD', 'Расширенная гарантия 20 лет'],
      sizes=[dict(name='TEFD2.5', slug='tefd2-5', cur='2,5', dims='40×20,2×10,15', imp='250–1200 А', iso='=1000 В', compat='TESD5, TESD10, TESD15'),
             dict(name='TEFD5', slug='tefd5', cur='5', dims='50×30,2×10,15', imp='250–1200 А', iso='=1000 В', compat='TESD20, TESD30'),
             dict(name='TEFD10', slug='tefd10', cur='10', dims='57,5×33,2×10,15', imp='250–1200 А', iso='=1000 В', compat='TESD40, TESD60'),
             dict(name='TEFD20', slug='tefd20', cur='20', dims='67,5×40,2×10,15', imp='250–1200 А', iso='=1000 В', compat='TESD100, TESD150, TESD200'),
             dict(name='TEFD40', slug='tefd40', cur='40', dims='84,5×52,5×12,85', imp='250–1200 А', iso='=1000 В', compat='TESD500')],
      related=[('tefs.html', 'TEFS'), ('tpf.html', 'ТПФ'), ('tefa.html', 'TEFA')]),
 dict(slug='tefa', name='TEFA', subtitle='Модули защиты и фильтрации для однофазных AC сетей',
      photo='https://te-power.ru/wp-content/uploads/TEFA20241209-387x200.png',
      inputs=[('115', '~115 В (83…138 В)'), ('230', '~230 В (182…264 В)'), ('230W', '~230 В (100…264 В)')],
      bodies=[('С', 'клеммные колодки'), ('Н', 'ножевые контакты')], body_prefix='S',
      temps=[('N', '−40…+85 °C'), ('P', '−50…+85 °C')],
      features=['Номинальный проходной ток от 1 до 20 А', 'Исполнение с полимерной заливкой, клеммные колодки или ножевые контакты',
                ('Варианты входного напряжения:', ['115 — 115 В (83…138 В)', '230 — 230 В (182…264 В)', '230W — 230 В (100…264 В)']),
                'Рабочая температура корпуса до −50…+85 °C', 'Максимальный импульсный ток защиты 1200 А',
                'Прочность изоляции вход/корпус, выход/корпус 1000 В', 'Рекомендуются к применению с модулями JETAs и TESAV',
                'Расширенная гарантия 20 лет'],
      sizes=[dict(name='TEFA1', slug='tefa1', cur='1', dims='67,5×40,2×10,15', imp='1200 А', iso='=1000 В', compat='JETAs30, JETAs40, JETAs60'),
             dict(name='TEFA5', slug='tefa5', cur='5', dims='101×51×19', imp='1200 А', iso='=1000 В', compat='JETAs80 … JETAs300'),
             dict(name='TEFA10', slug='tefa10', cur='10', dims='111×61×21', imp='1200 А', iso='=1000 В', compat='JETAs500, JETAs600, JETAs700'),
             dict(name='TEFA20', slug='tefa20', cur='20', dims='134×84×27,5', imp='1200 А', iso='=1000 В', compat='JETAs1000 … JETAs3000')],
      related=[('tpf.html', 'ТПФ'), ('tefd.html', 'TEFD'), ('tefs.html', 'TEFS')]),
 dict(slug='tpf', name='ТПФ', subtitle='Модуль защиты и фильтрации для трёхфазных AC сетей',
      photo='https://te-power.ru/wp-content/uploads/TEFA20241209-387x200.png',
      inputs=[('380', '~380 В (304…456 В)')],
      bodies=[('К', 'клеммные колодки'), ('Н', 'ножевые контакты')], body_prefix='',
      temps=[('Л', '−40…+85 °C'), ('М', '−50…+85 °C')],
      features=['Номинальный проходной ток 15 А', 'Фрезерованный алюминиевый корпус, клеммные колодки или ножевые контакты',
                'Входное напряжение ~380 В (304…456 В), 3 фазы', 'Рабочая температура корпуса до −50…+85 °C',
                'Вносимое затухание 30 дБ (1–10 МГц)', 'Прочность изоляции вход/корпус, выход/корпус ~1500 В',
                'Рекомендуется к применению с модулями серии ТПС', 'Расширенная гарантия 20 лет'],
      sizes=[dict(name='ТПФ15', slug='tpf15', cur='15', dims='134×84×28', imp='—', iso='~1500 В', compat='ТПС500 … ТПС5000')],
      related=[('tefa.html', 'TEFA'), ('tefd.html', 'TEFD'), ('tefs.html', 'TEFS')]),
 # TEFS: схемы наименования нет ни в каталоге, ни в документах — только страница серии
 dict(slug='tefs', name='TEFS', subtitle='Модули защиты для DC сетей', no_sizes=True,
      photo='https://te-power.ru/wp-content/uploads/TESAV100-F5-400x200.png',
      inputs=[('', '=9…36 В'), ('', '=17…80 В')], bodies=[], body_prefix='', temps=[('', '−60…+125 °C')],
      features=['Номинальный ток 5, 10 и 20 А',
                ('Защиты:', ['от обратной полярности;', 'от превышения выходного тока;', 'от повышенного и пониженного напряжения.']),
                'Дистанционное включение и выключение', 'Выводы индикации режимов работы',
                'Входное напряжение 9…36 В или 17…80 В', 'Рабочая температура корпуса −60…+125 °C', 'Расширенная гарантия 20 лет'],
      sizes=[dict(name='TEFS5', cur='5', dims='57,5×40,2×10,15', imp='—', iso='—', compat='—'),
             dict(name='TEFS10', cur='10', dims='72,5×52,5×12,85', imp='—', iso='—', compat='—'),
             dict(name='TEFS20', cur='20', dims='95×67,7×12,85', imp='—', iso='—', compat='—')],
      related=[('tefd.html', 'TEFD'), ('tefa.html', 'TEFA'), ('tpf.html', 'ТПФ')]),
]

def doc_list(ser):
    # ссылки на документы серии из content/docs; пусто — если документов нет
    if not ser.get('docs'):
        return ''
    return '<ul class="doc-list">\n      ' + '\n      '.join(
        f'<li><a class="doc-list__link" href="../content/docs/{f}" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--{c}">{t}</span>{label}</a></li>'
        for t, c, f, label in ser['docs']) + '\n    </ul>\n    '

def split_page(path):
    html = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    return html[:html.index('<div class="wrap breadcrumbs">')], html[html.index('<footer class="footer">'):]

def feature_html(features):
    items = []
    for f in features:
        if isinstance(f, tuple):
            items.append(f'<li>{f[0]}\n        <ul class="check-list__sub">' + ''.join(f'<li>{x}</li>' for x in f[1]) + '</ul>\n      </li>')
        else:
            items.append(f'<li>{f}</li>')
    return '\n      '.join(items)

def merged_rows(sizes, cols, merge):
    # одна строка на типоразмер; одинаковые значения соседних строк в столбцах merge — одна ячейка
    n = len(sizes)
    span = [[1] * len(cols) for _ in range(n)]
    for ci, key in enumerate(cols):
        if key not in merge:
            continue
        r = 0
        while r < n:
            k = r
            while k + 1 < n and sizes[k + 1]['_cells'][key] == sizes[r]['_cells'][key]:
                k += 1
            span[r][ci] = k - r + 1
            for j in range(r + 1, k + 1):
                span[j][ci] = 0
            r = k + 1
    out = []
    for r, s in enumerate(sizes):
        cells = []
        for ci, key in enumerate(cols):
            if span[r][ci] == 0:
                continue
            html = s['_cells'][key]
            cells.append('  ' + (html.replace('<td', f'<td rowspan="{span[r][ci]}"', 1) if span[r][ci] > 1 else html))
        out.append('<tr class="series-models__group-start">\n' + '\n'.join(cells) + '\n</tr>')
    return out

def lines(items):
    return ''.join(f'<span class="series-models__line">{x}</span>' for x in items)

def build(ser):
    path = os.path.join(ROOT, f'serii/{ser["slug"]}.html')
    head, foot = split_page(path)
    inputs_html = '<td class="series-models__inputs">' + lines(f'<b>{k}</b> — {v}' if k else v for k, v in ser['inputs']) + '</td>'
    for s in ser['sizes']:
        link = (f'<a class="series-models__model" href="{s["slug"]}.html">{s["name"]}</a>' if not ser.get('no_sizes')
                else f'<span class="series-models__model">{s["name"]}</span>')
        s['_cells'] = dict(name=f'<td class="series-models__name">{link}</td>', cur=f'<td>{s["cur"]} А</td>',
                           dims=f'<td>{s["dims"]}</td>', inputs=inputs_html, imp=f'<td>{s["imp"]}</td>',
                           iso=f'<td>{s["iso"]}</td>', compat=f'<td>{s["compat"]}</td>')
    cols = ['name', 'cur', 'dims', 'inputs', 'imp', 'iso', 'compat']
    heads = ['Типоразмер', 'Номинальный проходной ток', 'Размеры*, мм', 'Входное напряжение', 'Импульсный ток защиты', 'Прочность изоляции', 'Совместимые модули']
    if all(s['imp'] == '—' for s in ser['sizes']):
        cols.remove('imp'); heads.remove('Импульсный ток защиты')
    if all(s['iso'] == '—' for s in ser['sizes']):
        cols.remove('iso'); heads.remove('Прочность изоляции')
    if all(s['compat'] == '—' for s in ser['sizes']):
        cols.remove('compat'); heads.remove('Совместимые модули')
    rows = merged_rows(ser['sizes'], cols, merge={'inputs', 'imp', 'iso'})
    body = f'''<div class="wrap breadcrumbs"><a href="../produktsiya.html" class="breadcrumbs__link">Продукция</a> / <a href="../produktsiya.html#{CAT[1]}" class="breadcrumbs__link">{CAT[0]}</a> / {ser['name']}</div>
<section class="series-hero series-hero--plain"><div class="wrap series-hero__row">
  <div><h1 class="series-hero__title">{ser['name']} </h1><p class="series-hero__subtitle">{ser['subtitle']}</p></div>
</div></section>
<div class="wrap series-page">
<section class="series-intro">
  <div class="series-intro__col">
    <h2 class="series-intro__title">Особенности</h2>
    <ul class="check-list">
      {feature_html(ser['features'])}
    </ul>
  </div>
  <div class="series-intro__col">
    <div class="series-intro__photo"><img src="{ser['photo']}" alt="Модуль {ser['name']}"></div>
    <h2 class="series-intro__title">Документация серии</h2>
    {doc_list(ser)}<p class="series-intro__more">Даташиты, технические условия и 3D-модели по этой серии — по запросу у менеджера: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>. Также см. страницу <a href="../podderzhka.html" class="note__link">Техническая поддержка</a>.</p>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модели</h2>
  <div class="series-models__scroll">
  <table class="series-models__table">
  <thead><tr>{''.join(f'<th>{h}</th>' for h in heads)}</tr></thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
  </table>
  </div>
  <div class="series-models__notes">
    <p>* Без учёта длины выводов.</p>
  </div>
</section>

<div class="series-related">
  <span class="series-related__title">Другие серии этой категории:</span>
  {''.join(f'<a href="{h}" class="series-related__link">{t}</a>' for h, t in ser['related'])}
</div>
</div>

'''
    io.open(path, 'w', encoding='utf-8', newline='').write(head + body + foot)
    print(ser['slug'], 'series page,', len(ser['sizes']), 'sizes')
    if ser.get('no_sizes'):
        return

    for s in ser['sizes']:
        rows = []
        for k, inp in ser['inputs']:
            for b, blabel in ser['bodies']:
                for t, temp in ser['temps']:
                    nm = f'{s["name"]}-{k}-{ser["body_prefix"]}{b}{t}'
                    desc = f'{s["cur"]} А; вход {inp}; корпус: {blabel}; {s["dims"]} мм; {temp}'
                    rows.append(
                        f'<tr data-in="{k}" data-body="{b}" data-temp="{temp}">'
                        f'<td class="size-models__name">{nm}</td><td>{s["cur"]} А</td><td>{inp}</td><td>{blabel}</td>'
                        f'<td>{s["dims"]} мм</td><td>{temp}</td>'
                        f'<td><button type="button" class="cart-btn" data-cart-name="{nm}" data-cart-desc="{desc}" title="Добавить в корзину" aria-label="Добавить {nm} в корзину">{CART_SVG}</button></td></tr>')
        def opts(pairs):
            return '<option value="">Не выбрано</option>' + ''.join(f'<option value="{v}">{t}</option>' for v, t in pairs)
        params = [('Номинальный проходной ток', f'{s["cur"]} А'), ('Входное напряжение', [v for _, v in ser['inputs']]),
                  ('Исполнение корпуса', [l for _, l in ser['bodies']]), ('Габариты', f'{s["dims"]} мм'),
                  ('Температура корпуса', [t for _, t in ser['temps']])]
        if s['imp'] != '—':
            params.append(('Импульсный ток защиты', s['imp']))
        params += [('Прочность изоляции', s['iso']), ('Совместимые модули', s['compat']), ('Гарантия', '20 лет')]
        def val(v):
            return ''.join(f'<span class="spec-panel__row-line">{x}</span>' for x in v) if isinstance(v, list) else v
        params_html = ''.join(f'<div class="spec-panel__row"><span>{a}</span><span class="spec-panel__row-value">{val(v)}</span></div>' for a, v in params)
        sbody = f'''<div class="wrap breadcrumbs"><a href="../produktsiya.html" class="breadcrumbs__link">Продукция</a> / <a href="../produktsiya.html#{CAT[1]}" class="breadcrumbs__link">{CAT[0]}</a> / <a href="{ser['slug']}.html" class="breadcrumbs__link">{ser['name']}</a> / {s['name']}</div>
<section class="series-hero series-hero--plain"><div class="wrap series-hero__row">
  <div><h1 class="series-hero__title">{s['name']}</h1><p class="series-hero__subtitle">{ser['subtitle']}</p></div>
</div></section>
<div class="wrap series-page">
<section class="series-intro">
  <div class="series-intro__col">
    <h2 class="series-intro__title">Описание типоразмера</h2>
    {params_html}
  </div>
  <div class="series-intro__col">
    <div class="series-intro__photo"><img src="{ser['photo']}" alt="Модуль {s['name']}"></div>
    <h2 class="series-intro__title">Документация</h2>
    {doc_list(ser)}<p class="series-intro__more">Даташит и 3D-модель — по запросу у менеджера: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>.</p>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модельный ряд {s['name']}</h2>
  <div class="series-models__scroll">
  <table class="series-models__table size-models" data-model-filter>
  <thead>
  <tr><th>Наименование</th><th>Проходной ток</th><th>Входное напряжение</th><th>Исполнение корпуса</th><th>Размеры*</th><th>Диапазон рабочих температур</th><th>Заказ</th></tr>
  <tr class="size-models__filters">
    <th></th><th></th>
    <th><select class="size-models__select" data-key="in">{opts(ser['inputs'])}</select></th>
    <th><select class="size-models__select" data-key="body">{opts(ser['bodies'])}</select></th>
    <th></th>
    <th><select class="size-models__select" data-key="temp">{opts([(t, t) for _, t in ser['temps']])}</select></th>
    <th></th>
  </tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  <tr class="size-models__empty" hidden><td colspan="7">Нет моделей с такими параметрами</td></tr>
  </tbody>
  </table>
  </div>
  <button type="button" class="size-models__toggle" hidden></button>
  <div class="series-models__notes">
    <p>* Без учёта длины выводов.</p>
  </div>
</section>

<div class="series-related">
  <span class="series-related__title">Вернуться к серии:</span>
  <a href="{ser['slug']}.html" class="series-related__link">{ser['name']} — все типоразмеры</a>
</div>
</div>

'''
        shead = re.sub(r'<title>[^<]*</title>', f'<title>{s["name"]} — {ser["name"]} — TE-POWER</title>', head, count=1)
        io.open(os.path.join(ROOT, f'serii/{s["slug"]}.html'), 'w', encoding='utf-8', newline='').write(shead + sbody + foot)
        print('  ', s['slug'], len(rows), 'rows')

for ser in SERIES:
    build(ser)
