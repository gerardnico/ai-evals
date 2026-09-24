"""
Run mitmproxy as an embedded library (no `mitmdump` CLI needed).
"""

import asyncio
import time
from urllib.parse import urlparse

from mitmproxy import http, options
from mitmproxy.tools.dump import DumpMaster

# The actual endpoint to POST to (not the #!/view/ dashboard link)
TARGET_URL = "https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024"

import threading
import socket


# noinspection PyMethodMayBeStatic
class LogAndRedirect:
    def request(self, flow: http.HTTPFlow) -> None:
        original_url = flow.request.pretty_url
        print(f"[intercepted] {flow.request.method} {original_url}")

        # Preserve the original path as a sub-path
        original_path = urlparse(original_url).path or "/"

        flow.request.url = TARGET_URL
        flow.request.path = flow.request.path + original_path

    def response(self, flow: http.HTTPFlow) -> None:
        print(f"[response] {flow.response.status_code} for {flow.request.pretty_url}")


class MitmproxyRunner:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.master = None
        self.thread = None
        self.created = threading.Event()

        # Ensure no listening socket
        try:
            with socket.create_connection((self.host, self.port), timeout=0.2):
                raise Exception("Port is already listening")
        except OSError:
            pass

    def _run_proxy(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        opts = options.Options(listen_host=self.host, listen_port=self.port)
        self.master = DumpMaster(
            opts,
            with_termlog=False,
            with_dumper=False,
            loop=loop
        )
        self.master.addons.add(LogAndRedirect())
        self.created.set()

        try:
            loop.run_until_complete(self.master.run())
        finally:
            loop.close()

    def start(self):
        self.thread = threading.Thread(
            target=self._run_proxy,
            name="mitmproxy",
            daemon=True,
        )
        self.thread.start()
        self.created.wait()

        # Ensure mitmproxy has actually bound its listening socket.
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with socket.create_connection((self.host, self.port), timeout=0.2):
                    print("mitmproxy listening on http://localhost:8080")
                    print("Point clients at it, e.g.: curl -x http://localhost:8080 http://example.com")
                    return
            except OSError:
                time.sleep(0.1)

        self.stop()
        raise TimeoutError("mitmproxy did not start listening")

    def stop(self):
        if self.master is not None:
            self.master.shutdown()

        if self.thread is not None:
            self.thread.join(timeout=5)


class ProxyThread(threading.Thread):
    def __init__(self, host="0.0.0.0", port=8080):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.loop = None
        self.master = None
        self._ready = threading.Event()

    def run(self):
        # each thread needs its own event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        """Must be run in an event loop"""
        opts = options.Options(listen_host=self.host, listen_port=self.port)
        self.master = DumpMaster(opts, with_termlog=True, with_dumper=False, loop=self.loop)

        self._ready.set()
        try:
            print("mitmproxy listening on http://localhost:8080")
            print("Point clients at it, e.g.: curl -x http://localhost:8080 http://example.com")
            self.loop.run_until_complete(self.master.run())
        finally:
            self.loop.close()

    def stop(self):
        if self.master is not None:
            self.master.shutdown()


