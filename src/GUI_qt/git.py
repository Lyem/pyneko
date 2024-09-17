import os
from dulwich import porcelain
from packaging import version
from platformdirs import user_data_path

data_path = user_data_path('pyneko')

def update_providers():
    if not os.path.isdir(data_path / 'pyneko'):
        porcelain.clone('https://github.com/Lyem/pyneko', data_path / 'pyneko')
    else:
        porcelain.pull(data_path / 'pyneko')

def get_last_version():
    tags = porcelain.tag_list(data_path / 'pyneko')
    versions_str = [v.decode('utf-8')[1:] for v in tags]
    ordered_versions = sorted(versions_str, key=version.parse)
    return ordered_versions[-1]
