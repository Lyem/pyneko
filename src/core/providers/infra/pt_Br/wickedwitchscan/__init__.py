from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class WickedwitchScanProvider(ScanMadaraClone):
    name = 'wicked witch scan'
    lang = 'pt-Br'
    domain = ['wicked-witch-scan.com']

    def __init__(self):
        self.url = 'https://wicked-witch-scan.com'