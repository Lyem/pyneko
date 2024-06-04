import PyInstaller.__main__
from pathlib import Path
from sys import platform
import os

is_posix = platform.startswith(("darwin", "cygwin", "linux", "linux2"))

src_path = Path(__file__).resolve().parent.parent / 'src'
path_to_main = str(src_path / 'GUI_qt' / '__init__.py')
icon = str(src_path.parent / 'assets' / 'icon.ico')

separator = ':' if is_posix else ';'

os.environ['PYTHONPATH'] = str(src_path)

def install():
    PyInstaller.__main__.run([
        path_to_main,
        '--onefile',
        '--noconfirm',
        '--noconsole',
        '--collect-all=PyQt6',
        '--collect-all=nodriver',
        '--collect-all=bs4',
        '--collect-all=httpx',
        '--collect-all=fake_useragent',
        f'--icon="{icon}"',
        '--exclude-module=tests',
        f'--add-data=src/core/providers/infra{separator}core/providers/infra',
        f'--add-data=src/core/__seedwork/infra{separator}core/__seedwork/infra',
        f'--add-data=src/core/cloudflare{separator}core/cloudflare',
        f'--add-data=src/core/config{separator}core/config',
        f'--add-data=src/core/download{separator}core/download',
        f'--add-data=src/GUI_qt/assets{separator}GUI_qt/assets'
    ])
