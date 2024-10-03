from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class LScanProvider(ScanMadaraClone):
    name = 'L Scan'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt_Br'
    domain = 'lscans.com'

    def __init__(self):
        self.url = 'https://lscans.com'   