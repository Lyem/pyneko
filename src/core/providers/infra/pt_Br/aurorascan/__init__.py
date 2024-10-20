from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class CerisetoonProvider(ScanMadaraClone):
    name = 'Aurora scan'
    lang = 'pt-Br'
    domain = ['aurorascan.net']

    def __init__(self):
        self.url = 'https://aurorascan.net'   