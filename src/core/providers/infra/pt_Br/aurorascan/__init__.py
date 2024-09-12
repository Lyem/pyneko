from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class CerisetoonProvider(ScanMadaraClone):
    name = 'Aurora scan'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt-Br'
    domain = 'aurorascan.net'

    def __init__(self):
        self.url = 'https://aurorascan.net'   