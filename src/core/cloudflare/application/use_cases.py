from core.__seedwork.application.use_cases import UseCase
from core.cloudflare.domain.request_entity import Request
from core.cloudflare.infra.nodriver import Cloudflare


class IsCloudflareBlockingUseCase(UseCase):
    def execute(self, html: str) -> bool:
        return Cloudflare().is_cloudflare_blocking(html)

class IsCloudflareBlockingTimeOutUseCase(UseCase):
    def execute(self, html: str) -> bool:
        return Cloudflare().is_cloudflare_time_out(html)

class IsCloudflareBlockingBadGateway(UseCase):
    def execute(self, html: str) -> bool:
        return Cloudflare().is_cloudflare_bad_gatway(html)

class IsCloudflareAttention(UseCase):
    def execute(self, html: str) -> bool:
        return Cloudflare().is_cloudflare_attention(html)

class IsCloudflareEnableCookies(UseCase):
    def execute(self, html: str) -> bool:
        return Cloudflare().is_cloudflare_enable_cookies(html)

class BypassCloudflareUseCase(UseCase):
    def execute(self, url: str) -> Request:
        return Cloudflare().bypass_cloudflare(url)

class BypassCloudflareNoCapchaUseCase(UseCase):
    def execute(self, url: str) -> str:
        return Cloudflare().bypass_cloudflare_no_capcha(url)

class BypassCloudflareNoCapchaFeachUseCase(UseCase):
    def execute(self, domain: str, url: str, background = False) -> str:
        return Cloudflare().bypass_cloudflare_no_capcha_fetch(domain, url, background)

class BypassCloudflareNoCapchaPostUseCase(UseCase):
    def execute(self, domain: str, url: str, background = False) -> str:
        return Cloudflare().bypass_cloudflare_no_capcha_post(domain, url, background)

