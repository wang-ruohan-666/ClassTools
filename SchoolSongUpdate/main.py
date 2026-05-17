import os
import requests
import urllib3
import json
import re
import zipfile
import send2trash
from colorama import Fore,init
from tqdm import tqdm

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)
version=[0,0]
print("正在检查更新...")
response=requests.get("https://wrh6.qzz.io/update/Thousand_stars_main",verify=False)
def update(url):
    user_input=input("是否要更新[yes/no]: ").lower()
    if user_input=="yes" or user_input=="y":
        if os.path.isfile("file.zip"):
            os.remove("file.zip")
        response = requests.get(url, stream=True,verify=False)
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1000000
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True,bar_format=Fore.CYAN+'{l_bar}{bar}{r_bar}')
        with open("file.zip", "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        dir_name="School_Song"
        if os.path.isdir(dir_name):
            user_input=input("是否将旧版本音乐移动到回收站[yes/no]: ").lower()
            if user_input=="yes" or user_input=="y":
                send2trash.send2trash(dir_name)
                print("旧音乐已移动到回收站!")
            else:
                n=1
                while os.path.isdir(dir_name):
                    dir_name+=str(n)
                    n+=1
        with zipfile.ZipFile('file.zip', 'r') as zf:
            zf.extractall()
    elif user_input=="no" or user_input=="n":
        return
if response.status_code == 200:
    try:
        data=json.loads(response.text)
        if "version" in data:
            match=re.match(r"(\d+)\.(\d+)",data["version"])
            if int(match.group(1))>version[0]:
                print(f"{Fore.BLUE}检查到新版本 {data["version"]}")
                update(data["download_link"])
            elif int(match.group(1))==version[1] and int(match.group(2))>version[2]:
                print(f"{Fore.BLUE}检查到新版本 {data["version"]}")
                update(data["download_link"])
            else:
                print(Fore.GREEN + "你已是最新版!")
    except json.decoder.JSONDecodeError as e:
        print(Fore.RED+"JOSN转换失败!",e)
    except RuntimeError as e:
        print(Fore.RED+"检查更新失败!",e)
else:
    print(Fore.YELLOW+"检查更新失败!")