
from core.providers.infra.template.blogger_cms import BloggerCms

class StrellaScanProvider(BloggerCms):
    name = 'Strella Scans'
    lang = 'pt_Br'
    domain = ['www.strellascan.xyz']

    def __init__(self) -> None:
        self.get_title = 'header h1'
        self.API_domain = 'www.strellascan.xyz'
        self.get_pages = 'div.separator a img'


 
