from gerardnico.aitm.api import Context
from mitmproxy import http
from urllib.parse import urlparse


# https://docs.mitmproxy.org/stable/addons/overview/
# noinspection PyMethodMayBeStatic
class Redirect:
    def __init__(self, context: Context):
        self.context = context

    """Addon """

    def request(self, flow: http.HTTPFlow) -> None:
        original_url = flow.request.pretty_url
        self.context.session.count = self.context.session.count + 1

        original_path = urlparse(original_url).path or "/"

        print(f"[intercepted] {self.context.session.count} - {flow.request.method} {original_path}")

        flow.request.url = self.context.api
        flow.request.path = flow.request.path + original_path

    def response(self, flow: http.HTTPFlow) -> None:
        if flow.response is None:
            print(f"[response] {self.context.session.count} no response")
            return
        print(f"[response] {self.context.session.count} {flow.response.status_code} for {flow.request.pretty_url}")
