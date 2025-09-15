import os
import time
from pathlib import Path
from shutil import copy, copytree
from distutils.sysconfig import get_python_lib

# 1. activate virtual environment
#    $ conda activate YOUR_ENV_NAME
#
# 2. run deploy script
#    $ python deploy.py

# 记录部署开始时间
start_time = time.time()
print(f"开始部署时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
print("="*50)

args = [
    'nuitka',
    '--standalone',
    '--assume-yes-for-downloads',
    '--mingw64',
    '--windows-icon-from-ico=D:/Users/markchen.DESKTOP-SNGEVAJ/AppData/Local/Temp/icon.ico',
    '--enable-plugins=pyqt5',
    '--include-package=websockets',
    '--include-module=websockets.client',
    '--include-module=websockets.server',
    '--include-module=websockets.protocol',
    '--include-module=websockets.exceptions',
    '--include-data-dir=models=models',
    '--include-data-dir=libs=libs',
    '--windows-console-mode=disable',
    '--windows-file-description="XiaoZhi AI"',
    '--windows-product-version=1.0.2',
    '--windows-company-name=markingchen.inc',
    '--show-progress',
    '--show-memory',
    '--windows-file-version=1.0.2',
    '--output-dir=D:/Code/xiaozhiAI/build',
    'D:/Code/xiaozhiAI/Xiaozhi-ai.py'
]

dist_folder = Path("D:/Code/xiaozhiAI/build/Xiaozhi-ai.dist")

copied_site_packages = [
    
]

copied_standard_packages = [
    "ctypes"
]

# run nuitka
# https://blog.csdn.net/qq_25262697/article/details/129302819
# https://www.cnblogs.com/happylee666/articles/16158458.html
os.system(" ".join(args))

# copy site-packages to dist folder
site_packages = Path(get_python_lib())

for src in copied_site_packages:
    src = site_packages / src
    dist = dist_folder / src.name

    print(f"Coping site-packages `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass

# 计算并显示部署总耗时
end_time = time.time()
total_time = end_time - start_time
hours = int(total_time // 3600)
minutes = int((total_time % 3600) // 60)
seconds = int(total_time % 60)

print("="*50)
print(f"结束部署时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
print(f"部署总耗时: {hours:02d}:{minutes:02d}:{seconds:02d} ({total_time:.2f}秒)")
print("部署完成！")


# copy standard library
for file in copied_standard_packages:
    src = site_packages.parent / file
    dist = dist_folder / src.name

    print(f"Coping stand library `{src}` to `{dist}`")

    try:
        if src.is_file():
            copy(src, dist)
        else:
            copytree(src, dist)
    except:
        pass