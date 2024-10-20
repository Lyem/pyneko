from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class RfDragonScanProvider(ScanMadaraClone):
    name = 'Rf Dragon Scan'
    lang = 'pt-Br'
    domain = ['rfdragonscan.com']

    def __init__(self):
        self.url = 'https://rfdragonscan.com'   