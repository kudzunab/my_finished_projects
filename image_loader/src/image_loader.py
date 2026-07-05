import fake_useragent
import os
import io
import sys
import time
import requests
import pathlib
import asyncio
import ipaddress
from aioconsole import ainput
import prettytable
"""
python3 -m venv .venv           # Создаете новое чистое окружение
source .venv/bin/activate       # Активируете его
pip install -r work_progs.txt   # Одной командой ставите все библиотеки
"""
def get_path_math(_my_file):
    """!
        @detail Функция, возвращающая полный путь до файла относительно директории, в которой запущен скрипт.
        @param _my_file - имя файла или относительный путь, который нужно преобразовать.
        @return полный путь до файла, в котором сохраняется изображение.
    """
    try:
        _path = pathlib.Path(__file__).resolve().parent
    except NameError:
        _path = pathlib.Path.cwd()
    return _path.joinpath(_my_file).resolve()

def name_former(_url, _count):
    """!
        @detail Функция генерации имени изображения.
        @param _url - ссылка на изображение, которое нужно скачать;
        @param _count - номер скачиваемого изображения, начиная с нуля.
        @return имя файла, в котором сохраняется скачиваемое изображение.
    """
    _url = _url.split('?')[0]
    dop =_url[_url.rfind('.'):] if _url.rfind('.') != -1 and len(_url) > _url.rfind('.') + 1 else '.jpg'
    _name = f"image{_count}{dop}"
    return _name

def download_image_from_url(_url, _proxy_addr, _user_agent, _count, _work_dir) -> bool:
    """!
        @detail Функция, скачивающая изображение в существующую папку, адрес которой указывается относительно src.
        @param _url - ссылка на изображение, которое нужно скачать;
        @param _proxy_addr - адрес SOCKS5 прокси-сервера (IP:PORT). Если была введена пустая строка,
            скачивание будет происходить через прямое соединение;
        @param _user_agent - строка User-Agent для HTTP-заголовков;
        @param _count - номер скачиваемого изображения, начиная с нуля;
        @param _work_dir - объект pathlib.Path, указывающий на существующую директорию для сохранения.
        @return True при успешном скачивании изображения и False в случае ошибки.
    """
    header = {'User-Agent': _user_agent}
    my_proxies = {}
    if _proxy_addr:
        url_proxy = f'socks5h://{_proxy_addr}'
        my_proxies = { 'http': url_proxy, 'https': url_proxy}
    max_retries = 5
    picture_name = None
    type_of_picture = ""
    total_size = 0
    bad_attemp = 0
    with requests.Session() as session:
        while bad_attemp < max_retries:
            try:
                if not picture_name:
                    with session.head(_url, headers=header, proxies = my_proxies, timeout=20) as head:
                        type_of_picture = head.headers.get('Content-Type', '')
                        if 'image' not in type_of_picture:
                            return False
                        str_size = head.headers.get('Content-Length')
                        total_size = int(str_size) if str_size else 0
                        if _url.rfind('.') == -1:
                            dop = '.' + type_of_picture.split(';')[0].split('/')[-1]
                            if len(dop) > 5 or len(dop) <= 1: dop = '.jpg'
                        else:
                            dop = pathlib.Path(_url).suffix
                            if '?' in dop: dop = dop.split('?')[0]

                        picture_name = (_work_dir / f"image{_count}{dop}").resolve()

                current_size = picture_name.stat().st_size if picture_name.exists() else 0
                c_header = header.copy()
                if current_size > 0:
                    c_header['Range'] = f'bytes={current_size}-'

                with session.get(_url, headers=c_header, proxies = my_proxies, timeout=20, stream=True) as my_picture:
                    if my_picture.status_code == 416:
                        return True

                    if my_picture.status_code in [200, 206] and 'image' in type_of_picture:
                        regim = 'wb' if my_picture.status_code == 200 else 'ab'
                        with open(picture_name, regim) as f:
                            for piece in my_picture.iter_content(chunk_size=1024):
                                if piece:
                                    f.write(piece)
                                    bad_attemp = 0

                        if picture_name.exists() and picture_name.stat().st_size >= total_size:
                            return True
                        elif total_size == 0 and picture_name.stat().st_size > 0:
                            return True
                    elif my_picture.status_code in [403, 404]:
                        return False

            except (requests.RequestException, OSError):
                bad_attemp += 1
                time.sleep(1)
                pass
    if picture_name and picture_name.exists():
        if total_size > 0 and total_size > picture_name.stat().st_size:
            picture_name.unlink()
    return False

async def get_urls_queue(_queue: asyncio.Queue):
    """!
        @detail Функция добавление ссылок из командной строки в очередь. Ввод завершается вводом пустой строки.
        @param queue - асинхронная очередь ссылок на скачивание изображений
    """
    while True:
        _url = await ainput()
        if not _url.strip():
            await _queue.put(None)
            break
        await _queue.put(_url.strip())

async def urls_work(_queue: asyncio.Queue, _proxy_addr, _user_agent, _dict_stat, _work_dir):
    """!
        @detail Асинхронная функция скачивание изображение с помощью модуля requests.
        @param queue - асинхронная очередь ссылок на скачивание изображений
        @param _proxy_addr - адрес SOCKS5 прокси-сервера (IP:PORT);
        @param _user_agent - строка User-Agent для HTTP-заголовков;
        @param _dict_stat - словарь, в котором ключом является ссылка на изображение, а значением
            результат скачивания(Успех/Ошибка);
        @param _work_dir - объект pathlib.Path, указывающий на существующую директорию для сохранения.
    """
    request_stream = asyncio.get_running_loop()
    count = 0
    while True:
        _url_ = await _queue.get()
        if _url_ is None:
            _queue.task_done()
            break
        try:
            is_download = await request_stream.run_in_executor(
                None,
                download_image_from_url,_url_, _proxy_addr, _user_agent, count, _work_dir
            )
            _dict_stat[count] =  [_url_, "Успех"] if is_download else [_url_, "Ошибка"]
            count += 1
        finally:
            _queue.task_done()

async def manager(first_task: asyncio.Task, second_task: asyncio.Task):
    """!
        @detail Асинхронная функция, управляющая последовательным завершением задач. Если первая задача ввода
            завершается раньше задачи скачивания, то выводится соответствующее сообщение.
        @param first_task - объект типа asyncio.Task (задача ввода);
        @param second_task - объект типа asyncio.Task (задача загрузки).
    """
    await first_task
    if not second_task.done():
        print("Пожалуйста, подождите окончания загрузки")
    await second_task

async def main(_work_dir, my_proxy_addr):
    """!
        @detail Асинхронная функция для скачивания изображений, ссылки на которые вводятся с клавиатуры.
            После окончания работы выводится сводная таблица результатов.
        @param _work_dir - объект pathlib.Path, указывающий на существующую директорию для сохранения;
        @param my_proxy_addr - адрес SOCKS5 прокси-сервера (IP:PORT).
    """
    def print_table(_dict: dict):
        result_table = prettytable.PrettyTable(["Ссылка", "Статус"])
        result_table.align["Ссылка"] = "l"
        result_table.align["Статус"] = "l"
        for value in _dict.values():
            result_table.add_row([value[0], value[1]])
        print(result_table)

    my_user_agent = fake_useragent.UserAgent().random
    dict_stat = {}
    queue = asyncio.Queue()
    get_urls = asyncio.create_task(get_urls_queue(queue))
    load_urls = asyncio.create_task(urls_work(queue, my_proxy_addr, my_user_agent, dict_stat, _work_dir))
    await manager(get_urls, load_urls)
    sys.stdout.write("\033[H\033[J")
    print_table(dict_stat)

def check_proxy():
    """!
        @detail Функция проверки работоспособности адреса SOCKS5 прокси-сервера (IP:PORT). Если адрес по умолчанию
            не работает, то адресс вводится с клавиатуры.
        @return адрес SOCKS5 прокси-сервера (IP:PORT).
    """
    _proxy_addr = '37.220.81.2:10522' #'193.233.254.8:1080'
    while True:
        try:
            if not _proxy_addr:
                return ''
            proxy_url = f'socks5h://{_proxy_addr}'
            proxies = {'http': proxy_url, 'https': proxy_url}
            requests.get("https://www.pics4learning.com/", proxies=proxies, timeout=10)
            return _proxy_addr

        except requests.exceptions.RequestException as e:
            print(f"Ошибка соединения {e}")
            _proxy_addr = input(f"{_proxy_addr} не работает.\n" 
                        "Для продолжения работы с оригинальными настройками введите Enter.\n"
                        "Для работы через прокси введите новый в формате ip:port_number.\n").strip()
            if not _proxy_addr:
                return ''
            mass = _proxy_addr.split(':', 1)
            if len(mass) == 2:
                ip_part, port = mass
                try:
                    ipaddress.ip_address(ip_part)
                    if port.isdigit() and 0 < int(port) <= 65535:
                        continue
                except ValueError:
                    pass
            _proxy_addr = 'NOT_CORRECTED'

def get_work_dir():
    """!
        @detail Функция, возвращающая объект pathlib.Path, указывающий на существующую директорию для сохранения.
            Запрос ввода осуществляется до тех пор, пока не будет введено корректное имя директории,
            в которую возможна запись.
        @return Объект pathlib.Path, указывающий на проверенную директорию для сохранения.
    """
    my_input = input("./").strip()
    work_folder = get_path_math(my_input)
    while True:
        if not work_folder.exists():
            print('Папка не найдена')
        elif not work_folder.is_dir():
            print('Данный путь не является папкой')
        elif not os.access(work_folder, os.W_OK):
            print('У вас нет прав на запись')
        else:
            break
        work_folder = get_path_math(input("./").strip())
    return work_folder

# worked fast: '193.233.254.8:1080'
# worked fast: '37.220.81.2:10522'
# worked slowly: '178.22.31.205:1081'
# worked extremely slowly: '194.163.167.32:1080'
# https://images2.pics4learning.com/catalog/s/swamp_15.jpg
# https://bad-link-no-website-here.strange/img.png
# https://images2.pics4learning.com/catalog/p/parrot.jpg
# https://telescoper.blog/wp-content/uploads/2025/11/x4.png
# https://upload.wikimedia.org/wikipedia/commons/c/c7/Thure_de_Thulstrup_-_L._Prang_and_Co._-_Battle_of_Gettysburg_-_Restoration_by_Adam_Cuerden.jpg
# https://upload.wikimedia.org/wikipedia/commons/1/13/Syzygium_fruit.jpg
# https://upload.wikimedia.org/wikipedia/commons/c/c7/Thure_de_Thulstrup_-_L._Prang_and_Co._-_Battle_of_Gettysburg_-_Restoration_by_Adam_Cuerden.jpg
if __name__ == '__main__':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
    proxy_addr = check_proxy()
    work_dir = get_work_dir()
    asyncio.run(main(work_dir, proxy_addr))

