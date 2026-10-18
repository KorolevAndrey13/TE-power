# Пересобирает все сгенерированные страницы сайта. Запуск из любой папки:  python tools/build_all.py
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
# порядок важен: TESD-страницы типоразмеров берут шапку из serii/tesd.html, ТПИ — из serii/tpd.html
STEPS = ['build_tesd.py', 'build_sizes.py', 'build_series.py', 'build_tpi.py',
         'build_filters.py', 'build_chokes.py', 'build_docs.py', 'build_legal.py', 'build_news.py', 'build_series_docs.py', 'build_meta.py', 'build_404.py', 'build_redirects.py']  # build_meta — после страниц; build_redirects проверяет адреса

env = dict(os.environ, PYTHONIOENCODING='utf-8')
for step in STEPS:
    print(f'== {step}')
    # папка проекта лежит в OneDrive: при синхронизации файл может на миг заблокироваться — шаг повторяется
    for attempt in range(3):
        r = subprocess.run([sys.executable, os.path.join(HERE, step)], env=env)
        if not r.returncode:
            break
        print(f'   повтор {step} ({attempt + 2}-я попытка)')
        time.sleep(2)
    else:
        sys.exit(f'Ошибка в {step}')
print('Готово.')
