import os
import importlib.util
from typing import List
from pathlib import Path
from GUI_qt.config import get_config
from platformdirs import user_data_path
from core.providers.domain.provider_repository import ProviderRepository

data_path = user_data_path('pyneko')

def base_path():
    if os.environ.get('PYNEKOENV') != 'dev':
        return data_path / 'pyneko' / 'src'

    return Path('.') / 'src'

package_path = os.path.join(base_path(), 'core', 'providers', 'infra')
ignore_folders = ['template', '__pycache__']

def _get_class(package_path, ignore_folders):
    classes = []

    for root, dirs, files in os.walk(package_path):
        dirs[:] = [d for d in dirs if d not in ignore_folders]
        
        for file in files:
            if file.endswith('.py'):
                module_name = os.path.splitext(file)[0]
                module_path = os.path.join(root, file)

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and name.endswith('Provider'):
                        classes.append(obj)
    
    return classes

def import_classes_recursively() -> List[ProviderRepository]:
    global ignore_folders, package_path
    classes = []

    config = get_config()

    classes += _get_class(package_path, ignore_folders)

    if config.external_provider:
        external = _get_class(config.external_provider_path, ignore_folders)

        for c in classes:
            for ex in external:
                if c.domain == ex.domain:
                    classes.remove(c)
        
        classes += external

    return classes
