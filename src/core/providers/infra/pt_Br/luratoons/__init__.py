from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class LuratoonsProvider(ScanMadaraClone):
    name = 'Lura toons'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt-Br'
    domain = 'luratoons.com'

    def __init__(self):
        self.url = 'https://luratoons.com'   