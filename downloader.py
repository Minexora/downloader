import traceback
import os
import json
from utils.m3u8_donwloader import DownloadM3U8


def read_source(source):
    download_source = None
    try:
        with open(source, "r+",encoding="utf-8") as file:
            download_source = file.read()
            if download_source:
                download_source = json.loads(download_source)['source']
    except Exception:
        print(traceback.format_exc())
    return download_source


def get_difference_between_two_lists(array1, delete_dict):
    return[x for x in array1 if x != delete_dict]


def save_source(source, data):
    try:
        with open(source, "w+", encoding="utf-8") as file:
            file.write(data)
    except Exception:
        print(traceback.format_exc())


def file_control(source, delete_dict=None, check=False):
    try:
        if check:
            readed_file = read_source(source)
            delete_dict.pop('download_path', None)
            delete_dict.pop('combine_path', None)
            response_different = get_difference_between_two_lists(readed_file, delete_dict)
            save_source(
                source=source,
                data=json.dumps({'source': response_different}, indent=4)
            )
            return response_different
        else:
            return read_source(source=source)
    except Exception:
        print(traceback.format_exc())


def get_base_url(url):
    try:
        url_split_arr = url.split('/')
        return '/'.join(url_split_arr[:-1])
    except Exception:
        print(traceback.format_exc())


def check_file_name(file_name):
    try:
        check_list = ['/', '\\', '.', '\'', '"', '{', '}', '?', '']
        file_name = file_name.strip()
        for item in check_list:
            file_name = file_name.replace(item, '')
        file_name = file_name.strip()
        return file_name
    except Exception:
        print(traceback.format_exc())


def balance_class(data):
    try:
        if '.m3u8' in data['url']:
            file_name = check_file_name(data['file_name'])
            base_url = get_base_url(data['url'])
            if file_name and base_url:
                DownloadM3U8(
                    url=data['url'],
                    base_url=base_url,
                    download_path=data['download_path'],
                    combine_path=data['combine_path'],
                    file_name=file_name
                )
            else:
                raise ValueError(f'Veriler eksik geldi.Gelen veriler: file_name : {file_name} - base_url: {base_url}')
    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(__file__))
    source = os.path.join(base_dir, 'downloader/indir.json')
    con = True
    download_source = file_control(source=source)
    while con:
        if not download_source:
            con = False
        for i, data in enumerate(download_source):
            data['download_path'] = os.path.join(base_dir, 'downloader/chunk')
            data['combine_path'] = os.path.join(base_dir, 'downloader/conbine/')
            # balance_class(data)
            download_source = file_control(source=source, delete_dict=data, check=True)

    print('Bitti :D')
