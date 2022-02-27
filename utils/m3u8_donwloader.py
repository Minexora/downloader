import datetime
import subprocess
import requests
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class DownloadM3U8:

    def __init__(self, url, base_url, download_path, combine_path, file_name) -> None:
        self.download_path = download_path
        self.url = url
        self.base_url = base_url
        self.combine_path = combine_path
        self.file_name = file_name
        self.get_ts_urls()
        self.download()
        self.combine()
        # self.convert_ts_to_mp4()

    def get_ts_urls(self):
        self.urls = []
        r = requests.get(self.url)
        with open('sil', "wb") as file:
            file.write(r.content)
        with open('sil', "r") as file:
            lines = file.readlines()
            for line in lines:
                if ".ts" in line:
                    self.urls.append(self.base_url + '/' + line.strip("\n"))
        os.remove('sil')

    def file_check(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def download(self):
        for i in range(len(self.urls)):
            ts_url = self.urls[i]
            file_name = ts_url.split(".ts")[0].split('-')[-1]
            print("Start downloading %s" % file_name)
            start = datetime.datetime.now().replace(microsecond=0)
            try:
                response = requests.get(ts_url, stream=True, verify=False)
            except Exception as e:
                print("Exception request:%s" % e.args)
                return
            self.file_cunk_path = f'{self.download_path}/{self.file_name}'
            ts_path = self.file_cunk_path + "/{0}.ts".format(i)
            try:
                self.file_check(self.file_cunk_path)
                with open(ts_path, "wb+") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
            except Exception as e:
                print(str(e))
            end = datetime.datetime.now().replace(microsecond=0)
            print("Time consuming:%s" % (end-start))

    def file_walker(self):
        self.file_list = []
        for root, dirs, files in os.walk(self.file_cunk_path):
            #ada göre sıralayıp dosyaları düzgin şekilde birleştirmek için kullanılıyor.
            def get_key(obj):
                first_split = obj.split('.')[0]
                return int(first_split)

            files.sort(key=get_key)
            for fn in files:
                p = str(root+'/'+fn)
                self.file_list.append(p)

    def combine(self):
        self.file_walker()
        file_path = self.combine_path + self.file_name + '.ts'
        with open(file_path, 'wb+') as fw:
            for i in range(len(self.file_list)):
                fw.write(open(self.file_list[i], 'rb').read())
                os.remove(self.file_list[i])
            os.rmdir(self.file_cunk_path)

    def convert_ts_to_mp4(self):
        in_path = self.combine_path + self.file_name + '.ts'
        out_path = self.combine_path + self.file_name + '.mp4'
        try:
            subprocess.run(
                ['ffmpeg', '-i', in_path, '-bsf:a aac_adtstoasc -movflags +faststart', out_path])
        except Exception as e:
            print(str(e))
