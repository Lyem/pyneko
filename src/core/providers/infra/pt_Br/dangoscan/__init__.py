from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class DangoScanProvider(ScanMadaraClone):
    name = 'Dango scan'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt-Br'
    domain = 'dangoscan.com.br'

    def __init__(self):
        self.url = 'https://dangoscan.com.br'   