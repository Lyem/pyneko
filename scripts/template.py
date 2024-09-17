import os
from pathlib import Path
from tldextract import extract
from jinja2 import Environment, FileSystemLoader

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
    file_loader = FileSystemLoader('scripts/templates')
    env = Environment(loader=file_loader)
    for index, template in enumerate(templates):
        print(f'{index} - {template['name']}')
    template_index = int(input('Escolha o template: '))
    selected_template = templates[template_index]
    template = env.get_template(selected_template['template'])
    variables = {}
    variables['lang'] = input('Qual a lingua?: ')
    variables['domain'] =  input('Qual o dominio do site?: ')
    variables['class'] =  input('Qual o classe do provider?: ')
    variables['name'] = input('Qual o nome do provider?: ')
    for var in selected_template['variables']:
        user_value = input(f'Digite o valor para {var["name"]}: ')
        variables[var['value']] = user_value
    template_content = template.render(variables)
    extract_info = extract(variables['domain'])
    folder = os.path.join(providers, variables['lang'], extract_info.domain)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, '__init__.py'), 'w') as f:
        f.write(template_content)
    
    print('Template criado com sucesso')

if __name__ == "__main__":
    generate()