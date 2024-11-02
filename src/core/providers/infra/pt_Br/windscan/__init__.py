from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class WindScanProvider(ScanMadaraClone):
    name = 'Wind Scan'
    lang = 'pt_Br'
    domain = ['windscan.xyz']

    def __init__(self):
        self.url = 'https://windscan.xyz/'   