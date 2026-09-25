from gerardnico.aitm.api import Context
from mitmproxy import http
from urllib.parse import urlparse
from enum import Enum

class Provider(str, Enum):
    """The model provider"""
    OPENROUTER = "openrouter"

# noinspection PyMethodMayBeStatic
def get_redirect_base_url(original_path: str, default: str|None):
    url_paths = original_path.split("/")
    url_paths.pop(0) # first one is empty string
    if len(url_paths) == 0:
        return default
    prefix = url_paths.pop(0)
    match prefix:
        case Provider.OPENROUTER:
            return f"https://openrouter.ai/{str.join("/", url_paths)}"
        case _:
            return default


# https://docs.mitmproxy.org/stable/addons/overview/
class Redirect:
    """Addon """

    def __init__(self, context: Context):
        self.context = context

    def request(self, flow: http.HTTPFlow) -> None:
        original_url = flow.request.pretty_url
        self.context.session.count = self.context.session.count + 1

        original_path = urlparse(original_url).path or "/"

        print(f"[intercepted] {self.context.session.count} - {flow.request.method} {original_path}")
        base_url: str|None = get_redirect_base_url(original_path, self.context.default_provider_url)
        if base_url is None:
            raise Exception(f"No base url could be found for the path {original_path}")
        flow.request.url = base_url

    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response is None:
            print(f"[response] {self.context.session.count} no response")
            return
        print(f"[response] {self.context.session.count} {flow.response.status_code} for {flow.request.pretty_url}")
