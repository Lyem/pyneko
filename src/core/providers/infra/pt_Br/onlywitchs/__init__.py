from core.providers.infra.template.scan_madara_clone import ScanMadaraClone

class OnlyWitchsProvider(ScanMadaraClone):
    name = 'OnlyWitchs'
    lang = 'pt_Br'
    domain = ['onlywitchs.com']

    def __init__(self):
        self.url = 'https://onlywitchs.com/'