# Таблица «Модели» на странице серии serii/tesd.html (данные даташитов TESD). Остальная страница правится вручную.
# Одна строка на типоразмер. Ток — у старшей модели при 5 В (или при минимальном
# стандартном напряжении, если 5 В нет). КПД — среднее по одноканальным исполнениям (стр. 1).
from decimal import Decimal, ROUND_HALF_UP

IN_ALL = ['12W', '27', '24W']
INPUTS = {'12W': ('12 В', '9…36 В'), '27': ('27 В', '17…36 В'), '24W': ('24 В', '18…75 В')}

# (модели, аналоги, мощности, габариты, входы, даташит, выходные напряжения, (ток, при U), КПД по исполнениям)
G = [
    (['TESD10'], 'МДМ3-ЕП, МДМ5-ЕП, МДМ8-ЕП, МДМ5-П', [('5', '1'), ('10', '2')],
     [('40×20,2×10,15', 'с фланцами'), ('30,2×20,2×10,15', 'без фланцев')], IN_ALL, 'ДШ-TESD10.pdf',
     ['3,3', '5', '9', '12', '15', '24', '27', '36', '48', '60'], '5',
     [88, 88, 88, 90, 90, 90, 90, 92, 92, 92]),
    (['TESD15'], 'МДМ7,5-П, МДМ10-ЕП', [('10', '2'), ('15', '3')],
     [('50×30,2×11', 'с фланцами'), ('40,2×30×10,2', 'без фланцев')], IN_ALL, 'ДШ-TESD15.pdf',
     ['5', '12', '15', '24', '27', '36', '48', '60'], '5',
     [86, 87, 87, 88, 88, 89, 90, 90]),
    (['TESD30'], 'МДМ15-П, МДМ20-ЕП', [('20', '4'), ('30', '6')],
     [('57,5×33×11', 'с фланцами'), ('47,5×33×11', 'без фланцев')], IN_ALL, 'ДШ-TESD30.pdf',
     ['5', '12', '15', '24', '27', '36', '48', '60'], '5',
     [86, 88, 88, 89, 89, 89, 89, 90]),
    (['TESD60'], 'МДМ30-П, МДМ40-ЕП', [('40', '8'), ('60', '12')],
     [('67,5×40,2×11', 'с фланцами'), ('57,5×40,2×11', 'без фланцев')], IN_ALL, 'ДШ-TESD60.pdf',
     ['5', '12', '15', '24', '27', '36', '48', '60'], '5',
     [89, 91, 92, 92, 92, 93, 93, 93]),
    (['TESD100'], 'МДМ60-П, МДМ80-ЕП', [('80', '16'), ('100', '20')],
     [('84,5×52,5×12,85', 'с фланцами')], IN_ALL, 'ДШ-TESD100.pdf',
     ['5', '12', '15', '24', '27', '36', '48', '60'], '5',
     [88, 90, 91, 92, 92, 93, 93, 93]),
    (['TESD200'], 'МДМ120-П, МДМ160-П, МДМ160-ЕП', [('150', '12,5'), ('200', '16,7')],
     [('107×67,7×12,85', 'с фланцами')], IN_ALL, 'ДШ-TESD200.pdf',
     ['12', '15', '24', '27', '36', '48', '60'], '12',
     [88, 90, 90, 90, 91, 91, 91]),
    (['TESD480'], None, [('480', '40')],
     [('139×97×12,9', 'с фланцами'), ('127×97×12,9', 'без фланцев')], ['12W', '27'], 'ДШ-TESD480.pdf',
     ['12', '15', '24', '27', '36', '48', '60'], '12',
     [84, 84, 85, 85, 86, 86, 86]),
    (['TESD500'], 'МДМ240-П, МДМ320-П, МДМ240-ЕП', [('400', '33,3'), ('500', '41,7')],
     [('122×84,2×15', 'с фланцами')], ['27'], 'ДШ-TESD500.pdf',
     ['12', '15', '24', '27', '36', '48', '60'], '12',
     [91, 91, 92, 92, 93, 93, 93]),
]

out = []
# типоразмеры с двухканальными исполнениями (±5, ±12, ±15 В)
DUAL_SIZES = {'TESD10', 'TESD15', 'TESD30', 'TESD60'}
groups = []
for models, analogs, powers, dims, inputs, ds, volts, at, effs in G:
    eff = (Decimal(sum(effs)) / len(effs)).quantize(Decimal('1'), ROUND_HALF_UP)
    vols = volts + (['±5', '±12', '±15'] if models[-1] in DUAL_SIZES else [])
    name = f'<a class="series-models__model" href="{models[-1].lower()}.html">{" / ".join(models)}</a>'
    groups.append(dict(n=len(powers), powers=powers, cells=dict(
        name=f'<td class="series-models__name">{name}</td>',
        dims='<td>' + ''.join(f'<span class="series-models__line">{s_} <small>{c}</small></span>' for s_, c in dims) + '</td>',
        inputs='<td class="series-models__inputs">' + ''.join(f'<span class="series-models__line"><b>{k}</b> — {INPUTS[k][0]} ({INPUTS[k][1]})</span>' for k in inputs) + '</td>',
        volts=f'<td class="series-models__volts">{"; ".join(vols[:-1])}; <span class="series-models__nowrap">{vols[-1]} В</span></td>',
        eff=f'<td>{eff} %</td>',
        ds=f'<td><a class="series-models__ds" href="../content/docs/tesd/{ds}" target="_blank" rel="noreferrer" title="Даташит {models[-1]} (PDF)"><span class="doc-icon doc-icon--ds">ДШ</span></a></td>',
    )))

# одинаковые значения у соседних типоразмеров объединяются в одну ячейку
MERGE = {'inputs', 'volts', 'eff'}
span = [dict() for _ in groups]
for col in ['name', 'dims', 'inputs', 'volts', 'eff', 'ds']:
    g = 0
    while g < len(groups):
        k = g
        if col in MERGE:
            while k + 1 < len(groups) and groups[k + 1]['cells'][col] == groups[g]['cells'][col]:
                k += 1
        span[g][col] = sum(groups[j]['n'] for j in range(g, k + 1))
        for j in range(g + 1, k + 1):
            span[j][col] = 0
        g = k + 1

def cell(gi, col):
    rows = span[gi][col]
    if rows == 0:
        return None
    html = groups[gi]['cells'][col]
    return '  ' + (html.replace('<td', f'<td rowspan="{rows}"', 1) if rows > 1 else html)

for gi, grp in enumerate(groups):
    for i, (p, cur) in enumerate(grp['powers']):
        out.append('<tr class="series-models__group-start">' if i == 0 else '<tr>')
        first = i == 0
        if first: out.append(cell(gi, 'name'))
        out.append(f'  <td class="series-models__per">{p} Вт</td>')
        if first:
            out += [c for c in (cell(gi, 'dims'), cell(gi, 'inputs'), cell(gi, 'volts')) if c]
        out.append(f'  <td class="series-models__per">{cur} А</td>')
        if first:
            out += [c for c in (cell(gi, 'eff'), cell(gi, 'ds')) if c]
        out.append('</tr>')
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'serii', 'tesd.html')
h = io.open(P, encoding='utf-8').read().replace('\r\n', '\n')
a = h.index('<tbody>\n') + len('<tbody>\n'); b = h.index('  </tbody>')
h = h[:a] + chr(10).join(out) + '\n\n' + h[b:]
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('tesd series table ok')
