from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class WickedwitchScanProvider(ScanMadaraClone):
    name = 'wicked witch scan'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt-Br'
    domain = 'wicked-witch-scan.com'

    def __init__(self):
        self.url = 'https://wicked-witch-scan.com'