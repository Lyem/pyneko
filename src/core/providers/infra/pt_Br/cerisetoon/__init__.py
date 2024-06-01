from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class CerisetoonProvider(ScanMadaraClone):
    name = 'cerisetoon'
    icon = 'https://i.imgur.com/ycuyRsy.png'
    icon_hash = 'T3mBA4AkUz9sptRplgCb9VU7iHiQiYc'
    lang = 'pt-Br'
    domain = 'cerisetoon.com'

    def __init__(self):
        self.url = 'https://cerisetoon.com'   