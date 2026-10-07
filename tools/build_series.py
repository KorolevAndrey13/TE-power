# Генерирует страницы DC/DC-серий (страница серии + страницы типоразмеров) по образцу TESD.
# Источники: каталог 2026–2027 (стр. 6, 8, 9, 19), даташит TEH5, ТУ TESDs/TESH.
# Токи, которых нет в документах, считаются как P/U (на канал для двухканальных: P/2/U).
import io, os, re
from decimal import Decimal, ROUND_HALF_UP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
CART_SVG = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M3 4h2.2l2.1 10.2a1.5 1.5 0 0 0 1.5 1.2h8.4a1.5 1.5 0 0 0 1.5-1.1L20.5 8H6.1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><circle cx="9.5" cy="19.5" r="1.4" fill="currentColor"/><circle cx="17" cy="19.5" r="1.4" fill="currentColor"/></svg>'
REQ = 'Модули с нестандартным выходным напряжением — по запросу: <a href="mailto:russia@te-power.ru" class="note__link">russia@te-power.ru</a>.'

PROTECT = ('Полный комплекс защит с автовосстановлением:', ['от короткого замыкания и перегрузки;', 'от перенапряжения на выходе;', 'от перегрева.'])

SERIES = [
 dict(
  # Данные — из даташитов TESDs (стр. 1 и 3), размеры — со страницы серии в каталоге 2026–2027.
  slug='tesds', name='TESDs', badge=None,
  subtitle='DC/DC преобразователи с повышенной энергетической плотностью',
  photo='../content/images/tesds25.png',
  inputs=[('12W', '12 В', '9…36 В', 'по ГОСТ 54073-2010'), ('27', '27 В', '17…36 В', 'по ГОСТ 19705'),
          ('24W', '24 В', '18…75 В', 'выбросы до 80 В'), ('48', '48 В', '36…75 В', 'TESDs300, TESDs500')],
  outs=['5', '12', '15', '24', '27', '36', '48', '60'], duals=['5', '12', '15'],
  chan=('S', 'D'), dual_fmt='repeat',
  temps=[('T', '−60…+125 °C'), ('S', '−60…+110 °C')],
  docs=[('ТУ', 'tu', 'tesds/ТУ-TESDs.pdf', 'Технические условия ТЛДР.436630.003 ТУ')],
  features=['Выходная мощность от 15 до 500 Вт, КПД до 93 %', 'Предельная рабочая температура корпуса −60…+125 °C',
            'Запуск на большую выходную ёмкость',
            'Металлические корпуса с крепёжными фланцами или крепёжными отверстиями', 'INPUTS',
            'Один или два гальванически развязанных выхода (TESDs15, TESDs40, TESDs60)',
            'Регулировка выходного напряжения ±5 % и дистанционное управление',
            'Параллельная работа (TESDs300, TESDs500)', 'Холостой ход без подгрузки, фиксированная частота преобразования',
            PROTECT, 'Прочность изоляции вход/выход 1500 В', 'Совместимые фильтры ЭМП серии TEFD', 'Расширенная гарантия 20 лет'],
  sizes=[
   dict(slug='tesds15', name='TESDs15', models=[('TESDs15', 15)], dims=[('40×20×10,15', 'U')], dual=True, kpd=86,
        inputs=['12W', '27', '24W'], filt='TEFD2.5', ds='tesds/ДШ-TESDs15.pdf',
        # ±12 В на канал: в даташите 1,25 А (это 30 Вт при 15 Вт) — взято 15/2/12 = 0,62 А, как у TESD15
        currents={('TESDs15', '5'): '3', ('TESDs15', '12'): '1,25', ('TESDs15', '15'): '1', ('TESDs15', '24'): '0,62',
                  ('TESDs15', '27'): '0,55', ('TESDs15', '36'): '0,41', ('TESDs15', '48'): '0,31', ('TESDs15', '60'): '0,25',
                  ('TESDs15', '±5'): '1,5', ('TESDs15', '±12'): '0,62', ('TESDs15', '±15'): '0,5'}),
   dict(slug='tesds25', name='TESDs25', models=[('TESDs25', 25)], dims=[('40×20×10,25', 'C')], dual=False, kpd=86,
        inputs=['12W', '27', '24W'], filt='TEFD2.5', ds='tesds/ДШ-TESDs25.pdf', body_labels={'C': 'с крепёжными отверстиями'},
        currents={('TESDs25', '5'): '5', ('TESDs25', '12'): '2,1', ('TESDs25', '15'): '1,67', ('TESDs25', '24'): '1',
                  ('TESDs25', '27'): '0,92', ('TESDs25', '36'): '0,7', ('TESDs25', '48'): '0,52', ('TESDs25', '60'): '0,42'}),
   dict(slug='tesds40', name='TESDs40', models=[('TESDs40', 40)], dims=[('50×30×11', 'U')], dual=True, kpd=92,
        inputs=['12W', '27', '24W'], filt='TEFD5', ds='tesds/ДШ-TESDs40.pdf',
        currents={('TESDs40', '5'): '8', ('TESDs40', '12'): '3,33', ('TESDs40', '15'): '2,67', ('TESDs40', '24'): '1,67',
                  ('TESDs40', '27'): '1,48', ('TESDs40', '36'): '1,11', ('TESDs40', '48'): '0,83', ('TESDs40', '60'): '0,67',
                  ('TESDs40', '±5'): '4', ('TESDs40', '±12'): '1,67', ('TESDs40', '±15'): '1,33'}),
   dict(slug='tesds60', name='TESDs60', models=[('TESDs50', 50), ('TESDs60', 60)], dims=[('57,5×33×11', 'U')], dual=True, kpd=92,
        inputs=['12W', '27', '24W'], filt='TEFD5', ds='tesds/ДШ-TESDs60.pdf',
        currents={('TESDs50', '5'): '10', ('TESDs50', '12'): '4,16', ('TESDs50', '15'): '3,33', ('TESDs50', '24'): '2,08',
                  ('TESDs50', '27'): '1,85', ('TESDs50', '36'): '1,38', ('TESDs50', '48'): '1,04', ('TESDs50', '60'): '0,83',
                  ('TESDs50', '±5'): '5', ('TESDs50', '±12'): '2,08', ('TESDs50', '±15'): '1,66',
                  ('TESDs60', '5'): '12', ('TESDs60', '12'): '5', ('TESDs60', '15'): '4', ('TESDs60', '24'): '2,5',
                  ('TESDs60', '27'): '2,22', ('TESDs60', '36'): '1,66', ('TESDs60', '48'): '1,25', ('TESDs60', '60'): '1',
                  ('TESDs60', '±5'): '6', ('TESDs60', '±12'): '2,5', ('TESDs60', '±15'): '2'}),
   dict(slug='tesds150', name='TESDs150', models=[('TESDs120', 120), ('TESDs150', 150)], dims=[('67,5×40×11', 'U')], dual=False, kpd=92,
        inputs=['12W', '27', '24W'], filt='TEFD10', ds='tesds/ДШ-TESDs150.pdf',
        model_outs={'TESDs120': ['3.3', '5', '12', '15', '24', '27', '36', '48', '60']},
        currents={('TESDs120', '3.3'): '36,4', ('TESDs120', '5'): '24', ('TESDs120', '12'): '10', ('TESDs120', '15'): '8',
                  ('TESDs120', '24'): '5', ('TESDs120', '27'): '4,4', ('TESDs120', '36'): '3,3', ('TESDs120', '48'): '2,5', ('TESDs120', '60'): '2',
                  ('TESDs150', '5'): '30', ('TESDs150', '12'): '12,5', ('TESDs150', '15'): '10', ('TESDs150', '24'): '6,25',
                  ('TESDs150', '27'): '5,56', ('TESDs150', '36'): '4,17', ('TESDs150', '48'): '3,13', ('TESDs150', '60'): '2,5'}),
   dict(slug='tesds300', name='TESDs300', models=[('TESDs250', 250), ('TESDs300', 300)], dims=[('84,5×52,5×12,85', 'U')], dual=False, kpd=92,
        inputs=['27', '48'], filt='TEFD20', ds='tesds/ДШ-TESDs300.pdf',
        model_outs={'TESDs250': ['3.3', '5', '12', '15', '24', '27', '36', '48', '60']},
        currents={('TESDs250', '3.3'): '40', ('TESDs250', '5'): '40', ('TESDs250', '12'): '20,8', ('TESDs250', '15'): '16,7',
                  ('TESDs250', '24'): '10,4', ('TESDs250', '27'): '9,3', ('TESDs250', '36'): '6,9', ('TESDs250', '48'): '5,2', ('TESDs250', '60'): '4,2',
                  ('TESDs300', '5'): '50', ('TESDs300', '12'): '25', ('TESDs300', '15'): '20', ('TESDs300', '24'): '12,5',
                  ('TESDs300', '27'): '11,1', ('TESDs300', '36'): '8,3', ('TESDs300', '48'): '6,3', ('TESDs300', '60'): '5'}),
   dict(slug='tesds500', name='TESDs500', models=[('TESDs500', 500)], dims=[('107×67,7×12,85', 'U')], dual=False, kpd=92,
        inputs=['27', '48'], filt='TEFD40', ds='tesds/ДШ-TESDs500.pdf',
        model_outs={'TESDs500': ['12', '15', '24', '27', '36', '48', '60']},
        currents={('TESDs500', '12'): '41,7', ('TESDs500', '15'): '33,3', ('TESDs500', '24'): '20,8', ('TESDs500', '27'): '18,5',
                  ('TESDs500', '36'): '13,9', ('TESDs500', '48'): '10,4', ('TESDs500', '60'): '8,3'}),
  ],
  related=[('tesd.html', 'TESD'), ('tesh.html', 'TESH'), ('teh.html', 'TEH (ТЕН)'), ('tpd.html', 'ТПД')],
 ),
 dict(
  slug='teh', name='TEH', page_title='TEH (ТЕН)', badge='Новинка',
  subtitle='Изолированные DC/DC преобразователи — pin-to-pin аналоги модулей TEN (Traco Power)',
  photo='../content/images/teh.png',
  inputs=[('12', '12 В', '9…36 В', 'по ГОСТ 54073-2010'), ('27', '27 В', '17…36 В', 'по ГОСТ 19705'),
          ('24', '24 В', '18…75 В', 'выбросы до 80 В')],
  outs=['3.3', '5', '12', '15'], duals=['5', '12', '15'],
  chan=('С', 'Д'), dual_fmt='slash',
  temps=[('T', '−60…+125 °C'), ('В', '−60…+110 °C')],
  docs=[('ДШ', 'ds', 'teh/ДШ-TEH5.pdf', 'Даташит TEH5'), ('ДШ', 'ds', 'teh/TEН8.pdf', 'Даташит TEH8'),
        ('ДШ', 'ds', 'teh/ТЕНс3.pdf', 'Даташит ТЕНс3')],
  features=['Pin-to-pin замена модулей TEN производства Traco Power', 'Выходная мощность от 5 до 40 Вт, КПД до 88 %',
            'Предельная рабочая температура корпуса −60…+125 °C', 'Металлический алюминиевый корпус без фланцев, монтаж на печатную плату',
            'INPUTS', 'Один или два гальванически развязанных выхода (TEH5)',
            'Регулировка выходного напряжения ±5 % и дистанционное управление',
            'Холостой ход без подгрузки, фиксированная частота преобразования',
            PROTECT, 'Прочность изоляции вход/выход 1500 В', 'Совместимые фильтры ЭМП серии TEFD', 'Расширенная гарантия 20 лет'],
  sizes=[
   # TEH5 — токи и КПД из даташита; TEH8 — P/U. КПД типоразмера — среднее одноканальных TEH5 (76, 78, 83, 83).
   dict(slug='teh8', name='TEH8', models=[('TEH5', 5), ('TEH8', 8)], dims=[('32×20×10', 'C')], dual_models=['TEH5'], kpd=80,
        filt='TEFD2.5', ds='teh/ДШ-TEH5.pdf', ds_more=[('teh/TEН8.pdf', 'Даташит TEH8')], analog='TEN (Traco Power)',
        currents={('TEH5', '3.3'): '1,2', ('TEH5', '5'): '1', ('TEH5', '12'): '0,5', ('TEH5', '15'): '0,4',
                  ('TEH5', '±5'): '0,5', ('TEH5', '±12'): '0,25', ('TEH5', '±15'): '0,2'}),
   dict(slug='teh20', name='TEH20', models=[('TEH20', 20), ('TEH30', 30), ('TEH40', 40)], dims=[('50,8×25,4×10,2', 'C')], dual_models=[], kpd=88,
        filt='TEFD5', ds='teh/TEН20.pdf', analog='TEN (Traco Power)'),
  ],
  related=[('tesd.html', 'TESD'), ('tesds.html', 'TESDs'), ('tesh.html', 'TESH'), ('tpd.html', 'ТПД')],
 ),
 dict(
  slug='tesh', name='TESH', badge=None,
  subtitle='DC/DC преобразователи со стандартной или высоковольтной сетью',
  photo='../content/images/tesav-tesh.png',
  inputs=[('96', '96 В', '58…135 В', ''), ('110', '110 В', '66…160 В', 'выбросы до 170 В'),
          ('150W', '150 В', '110…375 В', ''), ('230', '230 В', '175…342 В', '')],
  outs=['5', '9', '12', '15', '24', '27', '36', '48', '60'], duals=['5', '12', '15'],
  chan=('S', 'D'), dual_fmt='repeat',
  temps=[('T', '−60…+125 °C'), ('S', '−40…+110 °C')],
  docs=[('ТУ', 'tu', 'tesh/ТУ-TESH.pdf', 'Технические условия ТЛДР.436630.004 ТУ')],
  features=['Выходная мощность от 50 до 500 Вт, КПД до 93 %', 'Предельная рабочая температура корпуса −60…+125 °C',
            'Металлические корпуса с крепёжными фланцами', 'INPUTS',
            'Один или два гальванически развязанных выхода (TESH50)',
            'Регулировка выходного напряжения ±5 % и дистанционное управление',
            'Параллельная работа (TESH200, TESH500)', 'Холостой ход без подгрузки, фиксированная частота преобразования',
            PROTECT, 'Прочность изоляции вход/выход 1500 В', 'Расширенная гарантия 20 лет'],
  sizes=[
   dict(slug='tesh50', name='TESH50', models=[('TESH50', 50)], dims=[('84,5×52,5×12,85', 'U')], dual=True, kpd=93, filt='внешний фильтр', ds='tesh/TESH50.pdf'),
   dict(slug='tesh200', name='TESH200', models=[('TESH100', 100), ('TESH200', 200)], dims=[('107×67,7×12,85', 'U')], dual=False, kpd=93, filt='внешний фильтр', ds='tesh/TESH200.pdf', ds_name='TESH200'),
   dict(slug='tesh500', name='TESH500', models=[('TESH300', 300), ('TESH500', 500)], dims=[('122×84×15', 'U')], dual=False, kpd=93, filt='внешний фильтр', ds='tesh/TESH500.pdf', ds_name='TESH500'),
  ],
  related=[('tesd.html', 'TESD'), ('tesds.html', 'TESDs'), ('teh.html', 'TEH (ТЕН)'), ('tpd.html', 'ТПД')],
 ),
 dict(
  slug='tpd', name='ТПД', badge='Новинка',
  subtitle='Изолированные DC/DC преобразователи для железнодорожного применения',
  photo='../content/images/tpd.webp',
  inputs=[('75', '75 В', '36…135 В', ''), ('110', '110 В', '77…132 В', '')],
  outs=['5', '9', '12', '15', '24', '27'], duals=[],
  chan=('С', 'Д'), dual_fmt='repeat',
  temps=[('Л', '−40…+85 °C')],
  docs=[('ДШ', 'ds', 'http://te-power.ru/wp-content/uploads/ТПД.pdf', 'Описание серии ТПД (PDF)')],
  features=['Разработаны по техническому заданию ведущего предприятия железнодорожной отрасли, прошли полный цикл испытаний в аппаратуре Заказчика',
            'Выходная мощность от 30 до 60 Вт, КПД до 85 %', 'Рабочая температура корпуса −40…+85 °C',
            'Металлический корпус с крепёжными фланцами', 'INPUTS', 'Дистанционное управление',
            ('Защиты:', ['от короткого замыкания и перенапряжения;', 'от переполюсовки;', 'тепловая защита.']),
            'Прочность изоляции вход/выход 1500 В', 'Отечественная разработка и производство', 'Расширенная гарантия 20 лет'],
  sizes=[
   dict(slug='tpd60', name='ТПД60', models=[('ТПД30', 30), ('ТПД60', 60)], dims=[('140×80×22', '')], dual=False, kpd=85,
        ds='http://te-power.ru/wp-content/uploads/ТПД.pdf'),
  ],
  related=[('tesd.html', 'TESD'), ('tesds.html', 'TESDs'), ('tesh.html', 'TESH'), ('teh.html', 'TEH (ТЕН)')],
 ),
 # ---------- AC/DC (каталог 2026–2027: стр. 6, 13, 14, 18). Токи — P/U.
 dict(
  slug='tps', name='ТПС', badge=None, category=('AC/DC модули', 'ac-dc-moduli'),
  subtitle='Трёхфазные AC/DC источники электропитания',
  photo='../content/images/tps1000-4000.png',
  inputs=[('380', '~380 В', '323…440 В', '3 фазы, 50 Гц'), ('220', '~220 В', '187…253 В', '3 фазы, 400 Гц'),
          ('115', '~115 В', '104…122 В', '3 фазы, 400 Гц')],
  outs=['12', '15', '24', '27', '36', '48', '60'], duals=[],
  chan=('С', 'Д'), dual_fmt='repeat',
  temps=[('Л', '−40…+85 °C'), ('М', '−50…+85 °C')],
  docs=[('ТУ', 'tu', 'tps/ТУ-ТПС.pdf', 'Технические условия ТПС')],
  features=['Выходная мощность от 500 до 5000 Вт, КПД до 93 %', 'Рабочая температура корпуса до −50…+85 °C (−60…+85 °C — по запросу)',
            'Металлические фрезерованные корпуса, клеммные колодки или ножевые контакты', 'INPUTS',
            'Регулировка выходного напряжения и дистанционное управление', 'Параллельная работа',
            'Холостой ход без подгрузки, фиксированная частота преобразования',
            PROTECT, 'Прочность изоляции вход/выход ~3000 В', 'Совместимые фильтры ЭМП серии ТПФ', 'Расширенная гарантия 20 лет'],
  sizes=[
   dict(slug='tps1000', name='ТПС1000', models=[('ТПС500', 500), ('ТПС1000', 1000)], dims=[('174×92×29', 'К'), ('174×92×29', 'Н')], kpd=92,
        model_outs={m: ['12', '15', '24', '27', '36', '48'] for m in ('ТПС500', 'ТПС1000')}, filt='ТПФ15'),
   dict(slug='tps1500', name='ТПС1500', models=[('ТПС1500', 1500)], dims=[('280×170×48', 'К'), ('280×170×48', 'Н')], kpd=92,
        model_outs={'ТПС1500': ['12', '15', '24', '27', '36', '48']}, filt='ТПФ15', analog='МАА1500'),
   dict(slug='tps2000', name='ТПС2000', models=[('ТПС2000', 2000)], dims=[('210×116×37', 'К'), ('210×116×37', 'Н')], kpd=92,
        model_outs={'ТПС2000': ['15', '24', '27', '36', '48', '60']}, filt='ТПФ15'),
   dict(slug='tps3000', name='ТПС3000', models=[('ТПС3000', 3000)], dims=[('250×141×38', 'К'), ('250×141×38', 'Н')], kpd=92,
        model_outs={'ТПС3000': ['24', '27', '36', '48', '60']}, filt='ТПФ15'),
   dict(slug='tps4000', name='ТПС4000', models=[('ТПС4000', 4000)], dims=[('280×170×48', 'К'), ('280×170×48', 'Н')], kpd=93,
        model_outs={'ТПС4000': ['24', '27', '36', '48', '60']}, filt='ТПФ15'),
   dict(slug='tps5000', name='ТПС5000', models=[('ТПС5000', 5000)], dims=[('300×170×39', 'К'), ('300×170×39', 'Н')], kpd=93,
        model_outs={'ТПС5000': ['24', '27', '36', '48', '60']}, filt='ТПФ15', ds='tps/ТПС5000-380С60-КМ.PDF'),
  ],
  related=[('jetas.html', 'JETAs'), ('tesav.html', 'TESAV')],
 ),
 dict(
  slug='jetas', name='JETAs', badge=None, category=('AC/DC модули', 'ac-dc-moduli'),
  subtitle='Однофазные AC/DC источники электропитания',
  photo='../content/images/jetas300.png',
  inputs=[('115', '~115 В', '80…138 В', 'выбросы до 150 В'), ('230', '~230 В', '176…242 В', 'выбросы до 264 В'),
          ('230W', '~230 В', '100…242 В', 'по запросу 100…264 В')],
  outs=['5', '9', '12', '15', '24', '27', '36', '48', '60'], duals=['5', '12', '15'],
  chan=('S', 'D'), dual_fmt='repeat',
  temps=[('N', '−40…+85 °C'), ('P', '−50…+85 °C')],
  docs=[('ТУ', 'tu', 'jetas/ТУ-JETAs.pdf', 'Технические условия JETAs')],
  features=['Выходная мощность от 30 до 3000 Вт, КПД до 93 %', 'Рабочая температура корпуса до −50…+85 °C',
            'Металлические фрезерованные корпуса с полимерной заливкой, винтовые клеммы или ножевые контакты', 'INPUTS',
            'Один или два гальванически развязанных выхода (JETAs60 … JETAs700)',
            'Регулировка выходного напряжения и дистанционное управление', 'Параллельная работа (JETAs300 и выше)',
            'Холостой ход без подгрузки, фиксированная частота преобразования',
            PROTECT, 'Прочность изоляции вход/выход ~3000 В', 'Совместимые фильтры ЭМП серии TEFA', 'Расширенная гарантия 20 лет'],
  sizes=[
   dict(slug='jetas60', name='JETAs60', models=[('JETAs30', 30), ('JETAs40', 40), ('JETAs60', 60)], dims=[('101×51×19', 'SС'), ('101×51×19', 'SН')],
        dual=True, kpd=93, filt='TEFA1'),
   dict(slug='jetas120', name='JETAs120', models=[('JETAs80', 80), ('JETAs100', 100), ('JETAs120', 120)], dims=[('111×61×21', 'SС'), ('111×61×21', 'SН')],
        dual=True, kpd=93, filt='TEFA5'),
   dict(slug='jetas300', name='JETAs300', models=[('JETAs150', 150), ('JETAs250', 250), ('JETAs300', 300)], dims=[('134×84×27,5', 'SС'), ('134×84×27,5', 'SН')],
        dual=True, kpd=93, filt='TEFA5'),
   dict(slug='jetas700', name='JETAs700', models=[('JETAs500', 500), ('JETAs600', 600), ('JETAs700', 700)], dims=[('175×93×29', 'SС'), ('175×93×29', 'SН')],
        dual=True, kpd=93, filt='TEFA10'),
   dict(slug='jetas1200', name='JETAs1200', models=[('JETAs1000', 1000), ('JETAs1200', 1200)], dims=[('211×117×38', 'SС'), ('211×117×38', 'SН')],
        dual=False, kpd=94, inputs=['230'], filt='TEFA20'),
   dict(slug='jetas1500', name='JETAs1500', models=[('JETAs1500', 1500)], dims=[('250×140×39', 'SС'), ('250×140×39', 'SН')],
        dual=False, kpd=94, inputs=['230'], filt='TEFA20'),
   dict(slug='jetas2000', name='JETAs2000', models=[('JETAs2000', 2000)], dims=[('280×170×42', 'SС'), ('280×170×42', 'SН')],
        dual=False, kpd=94, inputs=['230'], filt='TEFA20'),
   dict(slug='jetas3000', name='JETAs3000', models=[('JETAs3000', 3000)], dims=[('280×170×48', 'SС'), ('280×170×48', 'SН')],
        dual=False, kpd=93, inputs=['230'], filt='TEFA20'),
  ],
  related=[('tps.html', 'ТПС'), ('tesav.html', 'TESAV')],
 ),
 dict(
  slug='tesav', name='TESAV', badge=None, category=('AC/DC модули', 'ac-dc-moduli'),
  subtitle='Низкопрофильные однофазные AC/DC источники электропитания',
  photo='../content/images/tesav-tesh.png',
  inputs=[('115', '~115 В', '80…138 В', '50…400 Гц, выброс 180 В / 0,1 с'), ('230', '~230 В', '176…264 В', '46…440 Гц')],
  outs=['5', '9', '12', '15', '24', '27', '36', '48', '60'], duals=['5', '12', '15'],
  chan=('S', 'D'), dual_fmt='repeat',
  temps=[('T', '−60…+125 °C'), ('S', '−40…+110 °C')],
  docs=[('ТУ', 'tu', 'tesav/ТУ-TESAV.pdf', 'Технические условия TESAV')],
  features=['Выходная мощность от 50 до 500 Вт, КПД до 93 %', 'Рабочая температура корпуса до −60…+125 °C',
            'Низкопрофильные металлические корпуса с крепёжными фланцами', 'INPUTS',
            'Один или два гальванически развязанных выхода (TESAV50)',
            'Регулировка выходного напряжения и дистанционное управление', 'Параллельная работа (TESAV100 и выше)',
            'Холостой ход без подгрузки, фиксированная частота преобразования',
            PROTECT, 'Прочность изоляции вход/выход 1500 В', 'Расширенная гарантия 20 лет'],
  sizes=[
   dict(slug='tesav50', name='TESAV50', models=[('TESAV50', 50)], dims=[('84,5×52,5×12,85', 'U')], dual=True, kpd=93, filt='внешний фильтр'),
   dict(slug='tesav200', name='TESAV200', models=[('TESAV100', 100), ('TESAV200', 200)], dims=[('107×67,7×12,85', 'U')], dual=False, kpd=93, filt='внешний фильтр'),
   dict(slug='tesav500', name='TESAV500', models=[('TESAV500', 500)], dims=[('122×84×15', 'U')], dual=False, kpd=93, filt='внешний фильтр'),
  ],
  related=[('tps.html', 'ТПС'), ('jetas.html', 'JETAs')],
 ),
]

BODY_LABEL = {'U': 'с фланцами', 'C': 'без фланцев', '': 'с фланцами',
              'К': 'клеммные колодки', 'Н': 'ножевые контакты', 'SС': 'клеммные колодки', 'SН': 'ножевые контакты'}

def num(s):
    return float(s.replace(',', '.').lstrip('±'))

def fmt(v):
    q = Decimal('0.01') if v < 10 else (Decimal('0.1') if v < 100 else Decimal('1'))
    s = str(Decimal(str(v)).quantize(q, ROUND_HALF_UP))
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s.replace('.', ',')

def vcode(u):
    return u if '.' in u else u.zfill(2)

def ru(u):
    return u.replace('.', ',')

def current(size, m, p, u, dual):
    key = (m, ('±' + u) if dual else u)
    if key in size.get('currents', {}):
        return size['currents'][key]
    return fmt(p / (2 if dual else 1) / float(u))

def dual_models(size):
    if 'dual_models' in size:
        return size['dual_models']
    return [m for m, _ in size['models']] if size.get('dual') else []

def options(values, fmt_label):
    return ''.join(f'<option value="{v}">{fmt_label(v)}</option>' for v in values)

def feature_html(s, ser):
    items = []
    for f in s['features']:
        if f == 'INPUTS':
            sub = [f'{k} — {a} ({b}){", " + c if c else ""}' for k, a, b, c in ser['inputs']]
            f = ('Варианты входного напряжения:', sub)
        if isinstance(f, tuple):
            items.append(f'<li>{f[0]}\n        <ul class="check-list__sub">' + ''.join(f'<li>{x}</li>' for x in f[1]) + '</ul>\n      </li>')
        else:
            items.append(f'<li>{f}</li>')
    return '\n      '.join(items)

def doc_list(ser, extra=None, tail=None):
    docs = list(extra or []) + ser['docs'] + list(tail or [])
    seen, out = set(), []
    for t, c, f, label in docs:
        if f in seen:
            continue
        seen.add(f)
        href = f if f.startswith('http') else f'../content/docs/{f}'
        out.append(f'<li><a class="doc-list__link" href="{href}" target="_blank" rel="noreferrer"><span class="doc-icon doc-icon--{c}">{t}</span>{label}</a></li>')
    return '\n      '.join(out)

def size_docs(s, default_name):
    # даташиты типоразмера: основной (ds, подпись ds_name) и дополнительные (ds_more)
    docs = [('ДШ', 'ds', s['ds'], 'Даташит ' + s.get('ds_name', default_name))] if s.get('ds') else []
    return docs + [('ДШ', 'ds', f, label) for f, label in s.get('ds_more', [])]

def split_page(path):
    html = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    head = html[:html.index('<div class="wrap breadcrumbs">')]
    foot = html[html.index('<footer class="footer">'):]
    return head, foot

def size_inputs(ser, s):
    codes = s.get('inputs')
    return [x for x in ser['inputs'] if not codes or x[0] in codes]

def model_outs(ser, s, m):
    return s.get('model_outs', {}).get(m, ser['outs'])

def size_outs(ser, s):
    return sorted({u for m, _ in s['models'] for u in model_outs(ser, s, m)}, key=num)

def body_label(s, b):
    return s.get('body_labels', {}).get(b, BODY_LABEL[b])

def same_dims(s):
    # несколько исполнений корпуса с одним и тем же размером (клеммы / ножевые контакты)
    return len(s['dims']) > 1 and len({d for d, _ in s['dims']}) == 1

def dims_lines(s):
    if same_dims(s):
        return [(s['dims'][0][0], '')]
    return [(d, body_label(s, b)) for d, b in s['dims']]

def low_out(ser, s):
    outs = size_outs(ser, s)
    return '5' if '5' in outs else outs[0]

def inputs_cell(inps):
    return ''.join(f'<span class="series-models__line"><b>{k}</b> — {a} ({b})</span>' for k, a, b, _ in inps)

def build(ser):
    slug, name = ser['slug'], ser['name']
    page_title = ser.get('page_title', name)
    path = os.path.join(ROOT, f'serii/{slug}.html')
    head, foot = split_page(path)
    crumb_html = io.open(path, encoding='utf-8').read().replace('\r\n', '\n')
    crumb = re.search(r'<div class="wrap breadcrumbs">.*?</div>', crumb_html).group(0)
    has_ds = any(s.get('ds') for s in ser['sizes'])
    badge = f'<span class="series-hero__badge">{ser["badge"]}</span>' if ser['badge'] else ''
    hero = f'''<section class="series-hero series-hero--plain"><div class="wrap series-hero__row">
  <div><h1 class="series-hero__title">{page_title} {badge}</h1><p class="series-hero__subtitle">{ser['subtitle']}</p></div>
</div></section>'''

    # ---------- страница серии ----------
    groups = []
    for s in ser['sizes']:
        dm = dual_models(s)
        outs = [ru(u) for u in size_outs(ser, s)] + (['±' + d for d in ser['duals']] if dm else [])
        low = low_out(ser, s)
        d = ''.join(f'<span class="series-models__line">{dim}{" <small>" + lb + "</small>" if lb else ""}</span>' for dim, lb in dims_lines(s))
        ds_cell = ''
        if has_ds:
            ds_cell = ('<td>' + (f'<a class="series-models__ds" href="{s["ds"] if s["ds"].startswith("http") else "../content/docs/" + s["ds"]}" target="_blank" rel="noreferrer" title="Даташит (PDF)"><span class="doc-icon doc-icon--ds">ДШ</span></a>'
                                 if s.get('ds') else '—') + '</td>')
        groups.append(dict(s=s, low=low, cells=dict(
            name=f'<td class="series-models__name"><a class="series-models__model" href="{s["slug"]}.html">{s["name"]}</a></td>',
            dims=f'<td>{d}</td>',
            inputs=f'<td class="series-models__inputs">{inputs_cell(size_inputs(ser, s))}</td>',
            volts=f'<td class="series-models__volts">{"; ".join(outs[:-1])}; <span class="series-models__nowrap">{outs[-1]} В</span></td>',
            eff=f'<td>{s["kpd"]} %</td>',
            ds=ds_cell)))
    # одинаковые значения у соседних типоразмеров — одна ячейка
    MERGE = ('inputs', 'volts', 'eff')
    span = [dict() for _ in groups]
    for col in ('name', 'dims', 'inputs', 'volts', 'eff', 'ds'):
        g = 0
        while g < len(groups):
            k = g
            if col in MERGE:
                while k + 1 < len(groups) and groups[k + 1]['cells'][col] == groups[g]['cells'][col]:
                    k += 1
            span[g][col] = sum(len(groups[j]['s']['models']) for j in range(g, k + 1))
            for j in range(g + 1, k + 1):
                span[j][col] = 0
            g = k + 1
    def cell(gi, col):
        n_ = span[gi][col]
        html = groups[gi]['cells'][col]
        if n_ == 0 or not html:
            return None
        return '  ' + (html.replace('<td', f'<td rowspan="{n_}"', 1) if n_ > 1 else html)
    rows = []
    for gi, grp in enumerate(groups):
        s = grp['s']
        for i, (m, p) in enumerate(s['models']):
            rows.append('<tr class="series-models__group-start">' if i == 0 else '<tr>')
            if i == 0: rows.append(cell(gi, 'name'))
            rows.append(f'  <td class="series-models__per">{p} Вт</td>')
            if i == 0: rows += [c for c in (cell(gi, 'dims'), cell(gi, 'inputs'), cell(gi, 'volts')) if c]
            rows.append(f'  <td class="series-models__per">{current(s, m, p, grp["low"], False)} А</td>')
            if i == 0: rows += [c for c in (cell(gi, 'eff'), cell(gi, 'ds')) if c]
            rows.append('</tr>')
    low = groups[0]['low']
    low_note = (f'При выходном напряжении {ru(low)} В.' if all(g['low'] == low for g in groups)
                else 'При выходном напряжении 5 В (если 5 В нет — при минимальном стандартном).')
    ds_th = '<th>Даташит</th>' if has_ds else ''
    series_body = f'''{crumb}
{hero}
<div class="wrap series-page">
<section class="series-intro">
  <div class="series-intro__col">
    <h2 class="series-intro__title">Особенности</h2>
    <ul class="check-list">
      {feature_html(ser, ser)}
    </ul>
  </div>
  <div class="series-intro__col">
    <div class="series-intro__photo"><img src="{ser['photo']}" alt="Модуль {page_title}"></div>
    <h2 class="series-intro__title">Документация серии</h2>
    <ul class="doc-list">
      {doc_list(ser, tail=[d for x in ser['sizes'] for d in size_docs(x, x['name'])])}
    </ul>
    <p class="series-intro__more">3D-модели и остальные файлы — на странице <a href="../podderzhka.html" class="note__link">Поддержка</a> или по запросу у менеджера.</p>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модели</h2>
  <div class="series-models__scroll">
  <table class="series-models__table">
  <thead><tr><th>Типоразмер</th><th>Мощность</th><th>Размеры**, мм</th><th>Входное напряжение***</th><th>Стандартные выходные напряжения*</th><th>Макс. вых. ток****</th><th>Типовой КПД</th>{ds_th}</tr></thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
  </table>
  </div>
  <div class="series-models__notes">
    <p>* {REQ}</p>
    <p>** Без учёта длины выводов.</p>
    <p>*** Индекс входного напряжения ставится в наименование, например {ser['sizes'][0]['models'][-1][0]}-{ser['inputs'][1][0]}{ser['chan'][0]}{vcode(low)}-{ser['sizes'][0]['dims'][0][1]}{ser['temps'][0][0]}.</p>
    <p>**** {low_note}</p>
  </div>
</section>

<div class="series-related">
  <span class="series-related__title">Другие серии этой категории:</span>
  {''.join(f'<a href="{h}" class="series-related__link">{t}</a>' for h, t in ser['related'])}
</div>
</div>

'''
    io.open(path, 'w', encoding='utf-8', newline='').write(head + series_body + foot)
    print(slug, 'series page,', len(ser['sizes']), 'sizes')

    # ---------- страницы типоразмеров ----------
    for s in ser['sizes']:
        dm = dual_models(s)
        has_dual = bool(dm)
        show_body = same_dims(s)
        rows = []
        outs_single = size_outs(ser, s)
        inps = size_inputs(ser, s)
        for m, p in s['models']:
            outputs = [(u, False) for u in model_outs(ser, s, m)] + ([(u, True) for u in ser['duals']] if m in dm else [])
            for k, a, b, _ in inps:
                for u, dual in outputs:
                    uo = ('±' if dual else '') + ru(u)
                    if dual:
                        code = ser['chan'][1] + (vcode(u) * 2 if ser['dual_fmt'] == 'repeat' else f'{vcode(u)}/-{vcode(u)}')
                    else:
                        code = ser['chan'][0] + vcode(u)
                    i = current(s, m, p, u, dual)
                    ch = '2' if dual else '1'
                    cur_html = f'{i} А <small>на канал</small>' if dual else f'{i} А'
                    ch_td = f'<td>{ch}</td>' if has_dual else ''
                    for dim, body in s['dims']:
                        for t, temp in ser['temps']:
                            nm = f'{m}-{k}{code}-{body}{t}'
                            inp = (f'{a} ({b})' if a.startswith('~') else f'={a} ({b})')
                            desc = f'{p} Вт; вход {inp}; выход {uo} В; каналов: {ch}; {dim} мм; {temp}'
                            rows.append(
                                f'<tr data-model="{m}" data-power="{p}" data-in="{k}" data-out="{uo}" data-cur="{i}" data-dims="{dim}" data-body="{body}" data-temp="{temp}" data-ch="{ch}">'
                                f'<td class="size-models__name">{nm}</td><td>{p} Вт</td><td>{inp}</td>'
                                f'<td>{uo} В</td>{ch_td}<td>{cur_html}</td>' + (f'<td>{body_label(s, body)}</td>' if show_body else '') + f'<td>{dim} мм</td><td>{temp}</td>'
                                f'<td><button type="button" class="cart-btn" data-cart-name="{nm}" data-cart-desc="{desc}" title="Добавить в корзину" aria-label="Добавить {nm} в корзину">{CART_SVG}</button></td></tr>')
        powers = [str(p) for _, p in s['models']]
        outs_opts = [ru(u) for u in outs_single] + (['±' + d for d in ser['duals']] if has_dual else [])
        cur_opts = sorted({re.search(r'data-cur="([^"]+)"', r).group(1) for r in rows}, key=num)
        params = [
            ('Модели', ', '.join(m for m, _ in s['models'])),
            ('Мощность', f'{powers[0]}–{powers[-1]} Вт' if len(powers) > 1 else f'{powers[0]} Вт'),
            ('Входное напряжение', [f'{a} ({b})' for _, a, b, _ in inps]),
            ('Выходные напряжения', [f'{ru(outs_single[0])}–{ru(outs_single[-1])} В'] + ([', '.join('±' + d for d in ser['duals']) + ' В'] if has_dual else [])),
            ('Габариты', [f'{dim} мм{" " + lb if lb else ""}' for dim, lb in dims_lines(s)]),
            ('Температура корпуса', [t for _, t in ser['temps']]),
            ('Типовой КПД', f'{s["kpd"]} %'),
            ('Гарантия', '20 лет'),
        ]
        if s.get('filt'):
            params.insert(-1, ('Совместимый фильтр ЭМП', s['filt']))
        if s.get('analog'):
            params.append(('Pin-to-pin аналог', s['analog']))
        def val(b):
            return ''.join(f'<span class="spec-panel__row-line">{x}</span>' for x in b) if isinstance(b, list) else b
        params_html = ''.join(f'<div class="spec-panel__row"><span>{a}</span><span class="spec-panel__row-value">{val(b)}</span></div>' for a, b in params)
        extra = size_docs(s, s['models'][0][0])
        ncols = 8 + (1 if has_dual else 0) + (1 if show_body else 0)
        body = f'''<div class="wrap breadcrumbs"><a href="../produktsiya.html" class="breadcrumbs__link">Продукция</a> / <a href="../produktsiya.html#{ser.get('category', ('', 'dc-dc-moduli'))[1]}" class="breadcrumbs__link">{ser.get('category', ('DC/DC модули', ''))[0]}</a> / <a href="{slug}.html" class="breadcrumbs__link">{page_title}</a> / {s['name']}</div>
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
    <ul class="doc-list">
      {doc_list(ser, extra)}
    </ul>
  </div>
</section>

<section class="series-models">
  <h2 class="series-models__title">Модельный ряд {s['name']}</h2>
  <div class="series-models__scroll">
  <table class="series-models__table size-models" data-model-filter>
  <thead>
  <tr><th>Наименование</th><th>Мощность</th><th>Входное напряжение</th><th>Выходное напряжение*</th>{'<th>Количество каналов</th>' if has_dual else ''}<th>Макс. вых. ток</th>{'<th>Исполнение корпуса</th>' if show_body else ''}<th>Размеры**</th><th>Диапазон рабочих температур</th><th>Заказ</th></tr>
  <tr class="size-models__filters">
    <th><select class="size-models__select" data-key="model"><option value="">Не выбрано</option>{options([m for m, _ in s['models']], lambda v: v)}</select></th>
    <th><select class="size-models__select" data-key="power"><option value="">Не выбрано</option>{options(powers, lambda v: v + ' Вт')}</select></th>
    <th><select class="size-models__select" data-key="in"><option value="">Не выбрано</option>{''.join(f'<option value="{k}">{"" if a.startswith("~") else "="}{a} ({b})</option>' for k, a, b, _ in inps)}</select></th>
    <th><select class="size-models__select" data-key="out"><option value="">Не выбрано</option>{options(outs_opts, lambda v: v + ' В')}</select></th>
    {'<th><select class="size-models__select" data-key="ch"><option value="">Не выбрано</option><option value="1">1</option><option value="2">2</option></select></th>' if has_dual else ''}
    <th><select class="size-models__select" data-key="cur"><option value="">Не выбрано</option>{options(cur_opts, lambda v: v + ' А')}</select></th>
    {'<th><select class="size-models__select" data-key="body"><option value="">Не выбрано</option>' + ''.join(f'<option value="{b}">{body_label(s, b)}</option>' for _, b in s['dims']) + '</select></th>' if show_body else ''}
    <th><select class="size-models__select" data-key="dims"><option value="">Не выбрано</option>{options(list(dict.fromkeys(d for d, _ in s['dims'])), lambda v: v + ' мм')}</select></th>
    <th><select class="size-models__select" data-key="temp"><option value="">Не выбрано</option>{options([t for _, t in ser['temps']], lambda v: v)}</select></th>
    <th></th>
  </tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  <tr class="size-models__empty" hidden><td colspan="{ncols}">Нет моделей с такими параметрами</td></tr>
  </tbody>
  </table>
  </div>
  <button type="button" class="size-models__toggle" hidden></button>
  <div class="series-models__notes">
    <p>* {REQ}</p>
    <p>** Без учёта длины выводов.</p>
  </div>
</section>

<div class="series-related">
  <span class="series-related__title">Вернуться к серии:</span>
  <a href="{slug}.html" class="series-related__link">{page_title} — все типоразмеры</a>
</div>
</div>

'''
        size_head = re.sub(r'<title>[^<]*</title>', f'<title>{s["name"]} — {page_title} — TE-POWER</title>', head, count=1)
        io.open(os.path.join(ROOT, f'serii/{s["slug"]}.html'), 'w', encoding='utf-8', newline='').write(size_head + body + foot)
        print('  ', s['slug'], len(rows), 'rows')

for ser in SERIES:
    build(ser)
