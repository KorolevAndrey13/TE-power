# Страница «Страница не найдена» (404.html) в оформлении сайта.
# Шапка и подвал берутся с главной. Страница открывается по любому несуществующему адресу,
# поэтому относительные ссылки отсчитываются от корня сайта через <base> (на github.io — от /TE-power/).
import io, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # папка сайта (на уровень выше tools/)
src = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read().replace('\r\n', '\n')
head = src[:src.index('<section')]                  # всё до первого блока главной: <head>, шапка сайта
foot = src[src.index('<footer class="footer">'):]
head = re.sub(r'\n?<!-- meta -->.*?<!-- /meta -->', '', head, flags=re.S)
head = re.sub(r'<title>.*?</title>', '<title>Страница не найдена — TE-POWER</title>', head, count=1)
base = ('<script>document.write(\'<base href="\' + (location.hostname.slice(-10) === \'github.io\' ? '
        '\'/TE-power/\' : \'/\') + \'">\');</script>\n<meta name="robots" content="noindex">\n'
        '<link rel="icon" type="image/png" href="assets/favicon.png">')
head = head.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n' + base, 1)
head = head.replace('header__nav-link header__nav-link--active', 'header__nav-link')
body = '''<section class="section">
  <div class="wrap" style="padding-top:40px; padding-bottom:80px;">
    <div class="eyebrow">Ошибка 404</div>
    <h1 class="section__title" style="margin-top:14px;">Страница не найдена</h1>
    <p style="color:var(--graphite-2); max-width:640px; margin-bottom:26px;">Возможно, страница переехала: сайт ООО «ТЕ» обновился.
      Модули и документацию можно найти в каталоге и на странице поддержки.</p>
    <div style="display:flex; flex-wrap:wrap; gap:12px;">
      <a href="produktsiya.html" class="btn btn--accent">Каталог продукции</a>
      <a href="podderzhka.html" class="btn btn--line">Документация</a>
      <a href="index.html" class="btn btn--line">На главную</a>
    </div>
  </div>
</section>

'''
io.open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8', newline='\n').write(head + body + foot)
print('404.html ok')
