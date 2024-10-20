from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class LuratoonsProvider(ScanMadaraClone):
    name = 'Lura toons'
    lang = 'pt-Br'
    domain = ['luratoons.com']

    def __init__(self):
        self.url = 'https://luratoons.com'   