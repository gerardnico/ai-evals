"""
Dump each fetch (request/response) as raw HTTP files
"""
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from gerardnico.aitm.context import datetime_to_fs_name
from mitmproxy import http

SSE_EVENT_SEPARATOR = "\n\n"

logger = logging.getLogger(__name__)


# noinspection PyMethodMayBeStatic
class HttpDumper:

    def __init__(self, dump_dir: Path):

        self.dir = dump_dir
        os.makedirs(self.dir, exist_ok=True)

        # The buffer for sse parsing
        self.sse_chunk_buffer = ""

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
        """
        Response bytes because
        :param response:
        :return:
        """
        reason = response.reason or ""
        status_line = f"HTTP/{response.http_version.split('/')[-1]} {response.status_code} {reason}\r\n"
        lines = [status_line.encode("utf-8", "replace")]

        for k, v in response.headers.items(multi=True):
            lines.append(f"{k}: {v}\r\n".encode("utf-8", "replace"))
        lines.append(b"\r\n")

        body = response.raw_content or b""
        return b"".join(lines) + body

    def _response_sse(self, response: http.Response):

        response_content = response.content
        if response.headers.get("content-type", "").startswith("text/event-stream") and response_content:
            body = response_content.decode("utf-8", errors="replace")
            for block in body.split(SSE_EVENT_SEPARATOR):
                if not block.strip():
                    continue
                event = {}
                for line in block.splitlines():
                    if line.startswith("data:"):
                        event.setdefault("data", []).append(line[5:].strip())
                    elif line.startswith("event:"):
                        event["event"] = line[6:].strip()
                    elif line.startswith("id:"):
                        event["id"] = line[3:].strip()
        return

    def responseheaders(self, flow: http.HTTPFlow):
        """
        Hook up to the event stream
        https://docs.mitmproxy.org/stable/api/events.html#HTTPEvents.responseheaders
        """
        response = flow.response
        if response is None:
            return

        if response.headers.get("content-type", "").startswith("text/event-stream"):
            response.stream = self._handle_event_stream

    def _handle_event_stream(self, chunk: bytes) -> bytes:
        """
        A "chunk" (is a TCP packet/read from the socket)
        An SSE "event" is a logical unit text ending in \n\n, per the SSE spec
        They don't line up, a chunk may a half event
        """
        self.sse_chunk_buffer += chunk.decode("utf-8", errors="replace")
        while "\n\n" in self.sse_chunk_buffer:
            block, self.sse_chunk_buffer = self.sse_chunk_buffer.split("\n\n", 1)
            event = {}
            for line in block.splitlines():
                if line.startswith("data:"):
                    event.setdefault("data", []).append(line[5:].strip())
                elif line.startswith("event:"):
                    event["event"] = line[6:].strip()
            if event:
                print(event, flush=True)
        # pass unmodified
        return chunk

    def response(self, flow: http.HTTPFlow):
        """
        https://docs.mitmproxy.org/stable/api/events.html#HTTPEvents.response
        This event fires after the entire body has been streamed
        """
        req_path = self._get_file_path(flow, "request.http")
        flow.request.headers.get("date")
        with open(req_path, "wb") as f:
            f.write(self._request_bytes(flow.request))

        if flow.response is not None:
            resp_path = self._get_file_path(flow, "response.http")
            with open(resp_path, "wb") as f:
                f.write(self._response_bytes(flow.response))

        logger.info(f"[dump_flows] {flow.request.method} {flow.request.url} -> {flow.id}")

    def error(self, flow: http.HTTPFlow):
        """
        Handle flows that errored before getting a response (still dump the request)
        """
        if flow.response is None:
            req_path = self._get_file_path(flow, "request.http")
            if not os.path.exists(req_path):
                with open(req_path, "wb") as f:
                    f.write(self._request_bytes(flow.request))

    def _get_file_path(self, flow: http.HTTPFlow, suffix: str):
        """
        Return the file path to dump the request or response
        """
        dt = datetime.fromtimestamp(flow.timestamp_start, tz=timezone.utc)
        return self.dir / f"{datetime_to_fs_name(dt)}_{suffix}"
