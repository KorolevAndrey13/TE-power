# Строка пользователя для настроек админки (te-admin/config.php на сервере).
# Запуск: python tools/admin_user.py — спросит логин, имя и пароль; пароль на экран не выводится и никуда не сохраняется.
import getpass, hashlib, os, re

ITERATIONS = 600000
login = input('Логин (латиница, цифры): ').strip()
assert re.fullmatch(r'[a-z0-9_.-]{2,32}', login), 'логин — латиница в нижнем регистре, цифры, . _ -'
name = input('Имя для приветствия: ').strip() or login
while True:
    pw = getpass.getpass('Пароль (не меньше 10 символов): ')
    if len(pw) < 10:
        print('Слишком короткий.')
    elif pw != getpass.getpass('Ещё раз: '):
        print('Не совпадает.')
    else:
        break
salt = os.urandom(16)
digest = hashlib.pbkdf2_hmac('sha256', pw.encode('utf-8'), salt, ITERATIONS).hex()
print('\nВставьте строку в раздел users файла config.php:\n')
print(f"        '{login}' => ['name' => '{name}', 'hash' => 'pbkdf2_sha256${ITERATIONS}${salt.hex()}${digest}'],")
