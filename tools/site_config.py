# Адрес сайта — одно место на весь проект. При переезде (например, на https://te-power.ru/)
# поменять SITE_URL здесь и пересобрать: python tools/build_all.py
# Отсюда берутся canonical, og:url, og:image, sitemap.xml, robots.txt, переадресации и страница 404.
SITE_URL = 'https://te-power.ru/'           # с «/» на конце
SITE_PATH = '/' + SITE_URL.split('/', 3)[3]      # путь сайта на хосте: '/'
