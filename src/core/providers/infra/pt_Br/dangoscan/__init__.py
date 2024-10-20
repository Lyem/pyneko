from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class DangoScanProvider(ScanMadaraClone):
    name = 'Dango scan'
    lang = 'pt-Br'
    domain = ['dangoscan.com.br']

    def __init__(self):
        self.url = 'https://dangoscan.com.br'   