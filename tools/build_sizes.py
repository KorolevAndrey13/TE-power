# Генерирует страницы типоразмеров serii/tesd10.html … serii/tesd500.html
# по шаблону шапки/подвала serii/tesd.html. Данные — из даташитов TESD (стр. 1 и 3).
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
TPL = io.open(os.path.join(ROOT, 'serii/tesd.html'), encoding='utf-8').read().replace('\r\n', '\n')
HEAD = TPL[:TPL.index('<div class="wrap breadcrumbs">')]
FOOT = TPL[TPL.index('<footer class="footer">'):]

INPUTS = {'12W': '=12 В (9…36 В)', '27': '=27 В (17…36 В)', '24W': '=24 В (18…75 В)'}
IN_ALL = ['12W', '27', '24W']
TEMP = '−60…+125 °C'
TEMPS = [('T', '−60…+125 °C'), ('S', '−60…+110 °C')]
CART_SVG = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 4h2.2l2.1 10.2a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.1L20.5 8H6.1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9.5" cy="19.5" r="1.4" fill="currentColor"/><circle cx="17" cy="19.5" r="1.4" fill="currentColor"/></svg>'

def cur(d):  # "5:1 12:0,42" -> [('5','1'),('12','0,42')]
    return [tuple(p.split(':')) for p in d.split()]

# slug: (заголовок, даташит, фото, габариты [(размер, подпись)], входы, суффикс, [(модель, мощность, токи)], КПД до, аналоги)
S = {
 'tesd10': ('TESD10', 'ДШ-TESD10.pdf', 'tesd10.jpeg', [('40×20,2×10,15', 'с фланцами'), ('30,2×20,2×10,15', 'без фланцев')], IN_ALL, '', [
    ('TESD5', '5', cur('5:1 12:0,42 15:0,33 24:0,21 27:0,18 36:0,14 48:0,10 60:0,08')),
    ('TESD10', '10', cur('3.3:3,03 5:2 9:1,11 12:0,84 15:0,66 24:0,42 27:0,37 36:0,28 48:0,21 60:0,17'))], '92',
    'МДМ3-ЕП, МДМ5-ЕП, МДМ8-ЕП, МДМ5-П (БКЮС)'),
 'tesd15': ('TESD15', 'ДШ-TESD15.pdf', 'tesd15.webp', [('50×30,2×11', 'с фланцами'), ('40,2×30×10,2', 'без фланцев')], IN_ALL, '', [
    ('TESD10', '10', cur('5:2 12:0,84 15:0,66 24:0,42 27:0,37 36:0,28 48:0,21 60:0,17')),
    ('TESD15', '15', cur('5:3 12:1,25 15:1 24:0,62 27:0,55 36:0,41 48:0,31 60:0,25'))], '92',
    'МДМ7,5-П, МДМ10-ЕП (БКЮС)'),
 'tesd30': ('TESD30', 'ДШ-TESD30.pdf', 'tesd30.jpeg', [('57,5×33×11', 'с фланцами'), ('47,5×33×11', 'без фланцев')], IN_ALL, '', [
    ('TESD20', '20', cur('5:4 12:1,67 15:1,33 24:0,83 27:0,74 36:0,56 48:0,42 60:0,33')),
    ('TESD30', '30', cur('5:6 12:2,5 15:2 24:1,25 27:1,1 36:0,83 48:0,62 60:0,5'))], '90',
    'МДМ15-П, МДМ20-ЕП (БКЮС)'),
 'tesd60': ('TESD60', 'ДШ-TESD60.pdf', 'tesd60.jpeg', [('67,5×40,2×11', 'с фланцами'), ('57,5×40,2×11', 'без фланцев')], IN_ALL, '', [
    ('TESD40', '40', cur('5:8 12:3,33 15:2,67 24:1,67 27:1,48 36:1,11 48:0,83 60:0,67')),
    ('TESD60', '60', cur('5:12 12:5 15:4 24:2,5 27:2,22 36:1,66 48:1,25 60:1'))], '93',
    'МДМ30-П, МДМ40-ЕП (БКЮС)'),
 'tesd100': ('TESD100', 'ДШ-TESD100.pdf', 'tesd100.jpeg', [('84,5×52,5×12,85', 'с фланцами')], IN_ALL, '', [
    # TESD80: в даташите нет таблицы токов — рассчитано как P/U (правило выполняется для всех моделей серии)
    ('TESD80', '80', cur('5:16 12:6,67 15:5,33 24:3,33 27:2,96 36:2,22 48:1,67 60:1,33')),
    ('TESD100', '100', cur('5:20 12:8,33 15:6,67 24:4,16 27:3,7 36:2,77 48:2,08 60:1,66'))], '93',
    'МДМ60-П, МДМ80-ЕП (БКЮС)'),
 'tesd200': ('TESD200', 'ДШ-TESD200.pdf', 'tesd200.jpeg', [('107×67,7×12,85', 'с фланцами')], IN_ALL, '', [
    ('TESD150', '150', cur('12:12,5 15:10 24:6,25 27:5,56 36:4,17 48:3,13 60:2,5')),
    ('TESD200', '200', cur('12:16,7 15:13,3 24:8,3 27:7,4 36:5,6 48:4,1 60:3,3'))], '91',
    'МДМ120-П, МДМ160-П, МДМ160-ЕП (БКЮС)'),
 'tesd480': ('TESD480', 'ДШ-TESD480.pdf', 'tesd480.jpeg', [('139×97×12,9', 'с фланцами'), ('127×97×12,9', 'без фланцев')], ['12W', '27'], '-А', [
    ('TESD480', '480', cur('12:40 15:32 24:20 27:17,7 36:13,3 48:10 60:8'))], '86', None),
 'tesd500': ('TESD500', 'ДШ-TESD500.pdf', 'tesd500.jpeg', [('122×84,2×15', 'с фланцами')], ['27'], '', [
    # TESD400: в даташите нет таблицы токов — рассчитано как P/U
    ('TESD400', '400', cur('12:33,3 15:26,7 24:16,7 27:14,8 36:11,1 48:8,33 60:6,67')),
    ('TESD500', '500', cur('12:41,7 15:33,3 24:20,8 27:18,5 36:13,9 48:10,4 60:8,3'))], '93',
    'МДМ240-П, МДМ320-П, МДМ240-ЕП (БКЮС)'),
}

# Двухканальные исполнения (индекс D): ток указан на канал, даташит стр. 3.
# TESD15 ±12 В: в даташите 1,25 А — опечатка (это 30 Вт при мощности 15 Вт), взято 15/2/12 = 0,62 А.
DUAL = {
    ('tesd10', 'TESD5'): cur('5:0,5 12:0,21 15:0,16'),
    ('tesd10', 'TESD10'): cur('5:1 12:0,42 15:0,33'),
    ('tesd15', 'TESD10'): cur('5:1 12:0,42 15:0,33'),
    ('tesd15', 'TESD15'): cur('5:1,5 12:0,62 15:0,5'),
    ('tesd30', 'TESD20'): cur('5:2 12:0,84 15:0,66'),
    ('tesd30', 'TESD30'): cur('5:3 12:1,25 15:1'),
    ('tesd60', 'TESD40'): cur('5:4 12:1,67 15:1,33'),
    ('tesd60', 'TESD60'): cur('5:6 12:2,5 15:2'),
}

def vcode(u):
    return u if '.' in u else u.zfill(2)

def num(s):
    return float(s.replace(',', '.'))

def options(values, unit):
    return ''.join(f'<option value="{v}">{v} {unit}</option>' for v in values)

for slug, (title, ds, photo, dims, inputs, suffix, models, eff_max, analogs) in S.items():
    rows = []
    has_dual = any((slug, m) in DUAL for m, _, _ in models)
    bodies = [('U', dims[0][0])] + ([('C', dims[1][0])] if len(dims) > 1 else [])
    for m, p, currents in models:
        outputs = [(u, i, False) for u, i in currents] + [(u, i, True) for u, i in DUAL.get((slug, m), [])]
        for k in inputs:
            for u, i, dual in outputs:
                uo = ('±' if dual else '') + u.replace('.', ',')
                code = f'D{vcode(u) * 2}' if dual else f'S{vcode(u)}'
                cur_html = f'{i} А <small>на канал</small>' if dual else f'{i} А'
                ch = '2' if dual else '1'
                ch_td = f'<td>{ch}</td>' if has_dual else ''
                for b, dim in bodies:
                    for t, temp in TEMPS:
                        name = f'{m}-{k}{code}-{b}{t}{suffix}'
                        desc = f'{p} Вт; вход {INPUTS[k]}; выход {uo} В; каналов: {ch}; {dim} мм; {temp}'
                        rows.append(
                            f'<tr data-model="{m}" data-power="{p}" data-in="{k}" data-out="{uo}" data-cur="{i}" data-dims="{dim}" data-temp="{temp}" data-ch="{ch}">'
                            f'<td class="size-models__name">{name}</td><td>{p} Вт</td><td>{INPUTS[k]}</td>'
                            f'<td>{uo} В</td>{ch_td}<td>{cur_html}</td><td>{dim} мм</td><td>{temp}</td>'
                            f'<td><button type="button" class="cart-btn" data-cart-name="{name}" data-cart-desc="{desc}" title="Добавить в корзину" aria-label="Добавить {name} в корзину">{CART_SVG}</button></td></tr>')
    powers = [p for _, p, _ in models]
    outs = sorted({u for _, _, c in models for u, _ in c}, key=num)
    outs = [u.replace('.', ',') for u in outs]
    duals = sorted({u for m, _, _ in models for u, _ in DUAL.get((slug, m), [])}, key=num)
    currents_all = sorted({i for _, _, c in models for _, i in c} | {i for m, _, _ in models for _, i in DUAL.get((slug, m), [])}, key=num)
    pmin, pmax = powers[0], powers[-1]
    power_txt = f'{pmin}–{pmax} Вт' if len(powers) > 1 else f'{pmax} Вт'
    all_models = ', '.join(m for m, _, _ in models)
    dims_txt = [f'{d} мм {c}' for d, c in dims]
    params = [
        ('Модели', all_models),
        ('Мощность', power_txt),
        ('Входное напряжение', [INPUTS[k].lstrip('=') for k in inputs]),
        ('Выходные напряжения', [f'{outs[0]}–{outs[-1]} В'] + ([', '.join('±' + d for d in duals) + ' В'] if duals else [])),
        ('Габариты', dims_txt),
        ('Температура корпуса', [temp for _, temp in TEMPS]),
        ('КПД', f'до {eff_max} %'),
        ('Гарантия', '20 лет'),
    ]
    if analogs:
        params.append(('Pin-to-pin аналог', analogs))
    def val(b):
        return ''.join(f'<span class="spec-panel__row-line">{x}</span>' for x in b) if isinstance(b, list) else b
    params_html = ''.join(f'<div class="spec-panel__row"><span>{a}</span><span class="spec-panel__row-value">{val(b)}</span></div>' for a, b in params)

    body = f'''<div class="wrap breadcrumbs"><a href="../produktsiya.html" class="breadcrumbs__link">Продукция</a> / <a href="../produktsiya.html#dc-dc-moduli" class="breadcrumbs__link">DC/DC модули</a> / <a href="tesd.html" class="breadcrumbs__link">TESD</a> / {title}</div>
<section class="series-hero series-hero--plain"><div class="wrap series-hero__row">
  <div><h1 class="series-hero__title">{title}</h1><p class="series-hero__subtitle">DC/DC преобразователи с безоптронной обратной связью</p></div>
</div></section>
<div class="wrap series-page">
<section class="series-intro">
  <div class="series-intro__col">
    <h2 class="series-intro__title">Описание типоразмера</h2>
    {params_html}
  </div>
  <div class="series-intro__col">
    <div class="series-intro__photo"><img src="../content/images/{photo}" alt="Модуль {title}"></div>
    <h2 class="series-intro__title">Документация</h2>
    <ul class="doc-list">
      <li><a class="doc-list__link" href="../content/docs/tesd/{ds}" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--ds">ДШ</span>Даташит {title}</a></li>
      <li><a class="doc-list__link" href="../content/docs/tesd/ТУ-TESD.pdf" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--tu">ТУ</span>Технические условия ТЛДР.436630.001 ТУ</a></li>
    </ul>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модельный ряд {title}</h2>
  <div class="series-models__scroll">
  <table class="series-models__table size-models" data-model-filter>
  <thead>
  <tr><th>Наименование</th><th>Мощность</th><th>Входное напряжение</th><th>Выходное напряжение*</th>{'<th>Количество каналов</th>' if has_dual else ''}<th>Макс. вых. ток</th><th>Размеры**</th><th>Диапазон рабочих температур</th><th>Заказ</th></tr>
  <tr class="size-models__filters">
    <th><select class="size-models__select" data-key="model"><option value="">Не выбрано</option>{''.join(f'<option value="{m}">{m}</option>' for m, _, _ in models)}</select></th>
    <th><select class="size-models__select" data-key="power"><option value="">Не выбрано</option>{options(powers, 'Вт')}</select></th>
    <th><select class="size-models__select" data-key="in"><option value="">Не выбрано</option>{''.join(f'<option value="{k}">{INPUTS[k]}</option>' for k in inputs)}</select></th>
    <th><select class="size-models__select" data-key="out"><option value="">Не выбрано</option>{options(outs + ['±' + d for d in duals], 'В')}</select></th>
    {'<th><select class="size-models__select" data-key="ch"><option value="">Не выбрано</option><option value="1">1</option><option value="2">2</option></select></th>' if has_dual else ''}
    <th><select class="size-models__select" data-key="cur"><option value="">Не выбрано</option>{options(currents_all, 'А')}</select></th>
    <th><select class="size-models__select" data-key="dims"><option value="">Не выбрано</option>{''.join(f'<option value="{d}">{d} мм</option>' for _, d in bodies)}</select></th>
    <th><select class="size-models__select" data-key="temp"><option value="">Не выбрано</option>{''.join(f'<option value="{t}">{t}</option>' for _, t in TEMPS)}</select></th>
    <th></th>
  </tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  <tr class="size-models__empty" hidden><td colspan="{9 if has_dual else 8}">Нет моделей с такими параметрами</td></tr>
  </tbody>
  </table>
  </div>
  <button type="button" class="size-models__toggle" hidden></button>
  <div class="series-models__notes">
    <p>* Модули с нестандартным выходным напряжением — по запросу: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>.</p>
    <p>** Без учёта длины выводов.</p>
  </div>
</section>

<div class="series-related">
  <span class="series-related__title">Вернуться к серии:</span>
  <a href="tesd.html" class="series-related__link">TESD — все типоразмеры</a>
</div>
</div>

'''
    html = HEAD.replace('<title>TESD — TE-POWER</title>', f'<title>{title} — TESD — TE-POWER</title>') + body + FOOT
    io.open(os.path.join(ROOT, f'serii/{slug}.html'), 'w', encoding='utf-8', newline='').write(html)
    print(slug, len(rows), 'rows')
