import PyInstaller.__main__
from pathlib import Path
from sys import platform
import os

is_posix = platform.startswith(("darwin", "cygwin", "linux", "linux2"))
is_mac = platform.startswith('darwin')

src_path = Path(__file__).resolve().parent.parent / 'src'
path_to_main = str(src_path / 'GUI_qt' / '__init__.py')

separator = ':' if is_posix else ';'

splash = 'splash.jpg' if is_posix else 'splash.png'

os.environ['PYTHONPATH'] = str(src_path)

args = [
    path_to_main,
    '--onefile',
    '--noconfirm',
    '--noconsole',
    '--collect-all=PyQt6',
    '--collect-all=nodriver',
    '--collect-all=bs4',
    '--collect-all=cv2',
    '--collect-all=cloudscraper',
    '--collect-all=fake_useragent',
    '--collect-all=cryptography',
    '--collect-all=cairosvg',
    '--collect-all=pillow_avif',
    f'--icon=assets/icon.ico',
    '--exclude-module=tests',
    f'--add-data=src/core/providers/infra{separator}core/providers/infra',
    f'--add-data=src/core/__seedwork/infra{separator}core/__seedwork/infra',
    f'--add-data=src/core/cloudflare{separator}core/cloudflare',
    f'--add-data=src/core/config{separator}core/config',
    f'--add-data=src/core/download{separator}core/download',
    f'--add-data=src/GUI_qt/assets{separator}GUI_qt/assets'
]

if not is_mac:
    args.append(f'--splash=assets/{splash}')

def install():
    PyInstaller.__main__.run(args)
