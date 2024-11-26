from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class CeriseScanProvider(ScanMadaraClone):
    name = 'Cerise Scan'
    lang = 'pt-Br'
    domain = ['cerise.leitorweb.com']

    def __init__(self):
        self.url = 'https://cerise.leitorweb.com'   