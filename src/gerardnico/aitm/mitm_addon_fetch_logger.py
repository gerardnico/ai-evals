"""
Dump each fetch (request/response) as raw HTTP files
"""
import os

from gerardnico.aitm.api import Context
from mitmproxy import ctx, http
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class FetchLogger:

    def __init__(self, context: Context):
        self.context = context
        self.dir = Path(self.context.runtime_dir, "fetch-logs")

    def get_file_path(self, file_name):
        session_dir = Path(os.path.join(self.dir, self.context.session.id))
        os.makedirs(session_dir, exist_ok=True)
        return session_dir / file_name

    def running(self):
        os.makedirs(self.dir, exist_ok=True)

    def _request_bytes(self, request: http.Request) -> bytes:
        # Request line
        first_line = f"{request.method} {request.path} HTTP/{request.http_version.split('/')[-1]}\r\n"
        lines = [first_line.encode("utf-8", "replace")]

        # Ensure Host header is present even if mitmproxy stripped it internally
        headers = request.headers.copy()
        if "Host" not in headers and request.host:
            headers.insert(0, "Host", request.host)

        for k, v in headers.items(multi=True):
            lines.append(f"{k}: {v}\r\n".encode("utf-8", "replace"))
        lines.append(b"\r\n")

        body = request.raw_content or b""
        return b"".join(lines) + body

    def _response_bytes(self, response: http.Response) -> bytes:
        reason = response.reason or ""
        status_line = f"HTTP/{response.http_version.split('/')[-1]} {response.status_code} {reason}\r\n"
        lines = [status_line.encode("utf-8", "replace")]

        for k, v in response.headers.items(multi=True):
            lines.append(f"{k}: {v}\r\n".encode("utf-8", "replace"))
        lines.append(b"\r\n")

        body = response.raw_content or b""
        return b"".join(lines) + body

    def response(self, flow: http.HTTPFlow):
        # Fires once both request and response are available

        req_path = self.get_file_path(f"{flow.id}_request.http")
        with open(req_path, "wb") as f:
            f.write(self._request_bytes(flow.request))

        if flow.response is not None:
            resp_path = self.get_file_path(f"{flow.id}_response.http")
            with open(resp_path, "wb") as f:
                f.write(self._response_bytes(flow.response))

        logger.info(f"[dump_flows] {flow.request.method} {flow.request.url} -> {flow.id}")

    def error(self, flow: http.HTTPFlow):
        # Handle flows that errored before getting a response (still dump the request)
        if flow.response is None:
            req_path = self.get_file_path(f"{flow.id}_request.http")
            if not os.path.exists(req_path):
                with open(req_path, "wb") as f:
                    f.write(self._request_bytes(flow.request))
