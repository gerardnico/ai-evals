"""
Run mitmproxy as an embedded library
"""

import asyncio
import socket
import threading
import time

from gerardnico.aitm.context import Context
from gerardnico.aitm.mitm_addon_fetch_logger import FetchLogger
from gerardnico.aitm.mitm_addon_redirect import Redirect
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.tools.web.master import WebMaster


class MitmproxyRunner:
    def __init__(self, context: Context):
        self.host = context.mitm_host
        self.port = context.mitm_port
        self.master = None
        self.thread = None
        self.created = threading.Event()
        self.context = context

        # Ensure no listening socket
        try:
            with socket.create_connection((self.host, self.port), timeout=0.2):
                raise Exception("Proxy port is already taken")
        except OSError:
            pass

    async def _run_proxy(self):
        """
        Async so that there is a loop
        It's mandatory
        """

        opts = options.Options(
            listen_host=self.host,
            listen_port=self.port,
        )
        # In non-interactive mode, no webui is needed
        if self.context.mitm_web is not None and self.context.agent_interactive == False:
            self.master = WebMaster(
                opts,
                # don't keep mitmproxy's own startup/log messages
                with_termlog=False
            )
            self.master.options.update(
                web_open_browser=False,
                web_port=self.context.mitm_web,
                # Values starting with `$` are interpreted as an argon2 hash
                web_password="welcome",
            )
        else:
            self.master = DumpMaster(
                opts,
                # don't keep mitmproxy's own startup/log messages
                with_termlog=False,
                # skips adding the dumper addon that prints request/response info to stdout
                with_dumper=False,
            )

        # self.master.addons.add(Redirect(self.context))
        self.master.addons.add(FetchLogger(self.context))
        self.created.set()

        await self.master.run()

    def _thread_target(self):
        asyncio.run(self._run_proxy())

    def start(self):
        self.thread = threading.Thread(
            target=self._thread_target,
            name="aitm-proxy",
            daemon=True,
        )
        self.thread.start()
        self.created.wait()

        # Ensure mitmproxy has actually bound its listening socket.
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with socket.create_connection((self.host, self.port), timeout=0.2):
                    print(f"Aitm Proxy listening on http://{self.host}:{self.port}")
                    return
            except OSError:
                time.sleep(0.1)

        self.stop()
        raise TimeoutError("Aitm proxy did not start listening")

    def stop(self):

        if self.master is not None:
            self.master.shutdown()

        if self.thread is not None:
            self.thread.join(timeout=5)
