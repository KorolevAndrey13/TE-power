# Пересобирает все сгенерированные страницы сайта. Запуск из любой папки:  python tools/build_all.py
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
# порядок важен: TESD-страницы типоразмеров берут шапку из serii/tesd.html, ТПИ — из serii/tpd.html
STEPS = ['build_tesd.py', 'build_sizes.py', 'build_series.py', 'build_tpi.py',
         'build_filters.py', 'build_chokes.py', 'build_docs.py']

env = dict(os.environ, PYTHONIOENCODING='utf-8')
for step in STEPS:
    print(f'== {step}')
    r = subprocess.run([sys.executable, os.path.join(HERE, step)], env=env)
    if r.returncode:
        sys.exit(f'Ошибка в {step}')
print('Готово.')
