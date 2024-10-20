from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class LScanProvider(ScanMadaraClone):
    name = 'L Scan'
    lang = 'pt_Br'
    domain = ['lscans.com']

    def __init__(self):
        self.url = 'https://lscans.com'   