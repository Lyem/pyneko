from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class SinensistoonProvider(ScanMadaraClone):
    name = 'Sinensis toon'
    lang = 'pt-Br'
    domain = ['sinensis.leitorweb.com']

    def __init__(self):
        self.url = 'https://sinensis.leitorweb.com'
