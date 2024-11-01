import os
import json
import locale
from pathlib import Path
from tldextract import extract
from jinja2 import Environment, FileSystemLoader

def load_translations():
    path = os.path.join(Path('.') / 'assets', 'translations.json')
    with open(path, 'r') as file:
        return json.load(file)

translations = load_translations()

def get_system_language():
    lang = locale.getdefaultlocale()[0]
    return lang.split('_')[0] if lang else 'en'

def get_message(key, lang='en'):
    return translations.get(lang, translations['en']).get(key, '')

templates = [
    {'name': 'Madara', 'template': 'wordpress_madara.py.jinja', 'variables': [
        {'name': 'Link do site', 'value': 'link'},
    ]},
    {'name': 'Base', 'template': 'base.py.jinja', 'variables': []},
    {'name': 'Manga Reader CMS', 'template': 'manga_reader_cms.py.jinja', 'variables': [
        {'name': 'Link do site', 'value': 'link'},
    ]},
    {'name': 'Scan Madara Clone', 'template': 'scan_madara_clone.py.jinja', 'variables': [
        {'name': 'Link do site', 'value': 'link'},
    ]}
]

providers = os.path.join(Path('.') / 'src', 'core', 'providers', 'infra')

def generate():
    lang = get_system_language()
    file_loader = FileSystemLoader('scripts/templates')
    env = Environment(loader=file_loader)
    for index, template in enumerate(templates):
        print(f'{index} - {template["name"]}')
    template_index = int(input(get_message('select_template', lang)))
    selected_template = templates[template_index]
    template = env.get_template(selected_template['template'])
    variables = {}
    variables['lang'] = input(get_message('enter_language', lang))
    variables['domain'] = input(get_message('enter_domain', lang))
    variables['class'] = input(get_message('enter_class', lang))
    variables['name'] = input(get_message('enter_name', lang))
    for var in selected_template['variables']:
        user_value = input(get_message('enter_value', lang).format(var=var["name"]))
        variables[var['value']] = user_value
    template_content = template.render(variables)
    extract_info = extract(variables['domain'])
    folder = os.path.join(providers, variables['lang'], extract_info.domain)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, '__init__.py'), 'w') as f:
        f.write(template_content)
    
    print(get_message('success_message', lang))

if __name__ == "__main__":
    generate()
