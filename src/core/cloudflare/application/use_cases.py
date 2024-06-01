from core.__seedwork.application.use_cases import UseCase
from core.cloudflare.domain.request_entity import Request
from core.cloudflare.infra.nodriver import Cloudflare


class IsCloudflareBlockingUseCase(UseCase):
    def execute(self, html: str) -> bool:
        return Cloudflare().is_cloudflare_blocking(html)


class BypassCloudflareUseCase(UseCase):
    def execute(self, url: str) -> Request:
        return Cloudflare().bypass_cloudflare(url)

class BypassCloudflareNoCapchaUseCase(UseCase):
    def execute(self, url: str) -> str:
        return Cloudflare().bypass_cloudflare_no_capcha(url)

