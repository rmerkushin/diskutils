# Задание

На языке Python реализовать скрипт, который при запуске из командной строки без параметров выводит список жестких дисков с их размерами, присутствующих в системе.

При запуске с одним числовым параметром скрипт должен выводить список партиций с их размерами, содержащихся на диске с указанным номером.

Требуется реализовать указанный функционал через класс-абстракцию и конкретные имплементации для ОС Windows + Linux.

# Системные требования

- Python 3.6+
- mypy для тестов
- Windows 7 или выше
- Linux:
    - lsblk

# Описание

Скрипт реализован с применением [Type Hints](https://www.python.org/dev/peps/pep-0484/) и нового способа форматирования строк добавленного в `Python 3.6`. Получение информации о дисках реализовано через парсинг `stdout` утилит `wmic` для Windows и `lsblk` для Linux. Выбор утилит обусловлен наличием удобного вывода результатов в виде `csv` у wmic и `json` у lsblk. Сама реализация через парсинг stdout мне не очень нравится, но готовых библиотек для получения информации о дисках для Linux я не нашел, кроме чтения информации из системы с использованием `ctypes`, но это уже _overhead_, как и использование в скрипте `win32api` или `WMI` для Windows. Программа реализована в виде единого файла, т.к. по заданию это должен быть скрипт. Так же я в эстетических целях добавил в скрипт функцию для форматированного вывода информации и использовал `argparse` вместо `sys.argv[1]`. Для запуска тестов использовать `run_tests.(sh|bat)`.

# Пример работы скрипта:

![diskutils](https://github.com/rmerkushin/diskutils/blob/master/diskutils.png)
