import os
import signal
import subprocess
import sys

from gerardnico.aitm.api import Context, Agent
from gerardnico.aitm.mitm import MitmproxyRunner
from gerardnico.aitm.pass_cli import get_secret


async def run(context: Context) -> None:
    """Runs master.run() in its own event loop, in a separate thread."""
    proxy = MitmproxyRunner(context)

    """Handle IDE debugging shutdown"""

    def handle_shutdown(signum, frame):
        print(f"Received signal {signum}, shutting down the proxy")
        proxy.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    try:
        print("Starting proxy...")
        proxy.start()

        match context.agent:
            case Agent.BASH:
                print("Starting bash...")
                print(f"e.g.: curl -x http://localhost:{context.mitm_port} http://example.com")
                bash_args = ["bash", "--noprofile", "--norc"]
                if context.interactive_mode:
                    bash_args.append("-i")
                else:
                    bash_args.append("-c")
                    bash_args.append(f"curl -x http://localhost:{context.mitm_port} http://example.com")
                subprocess.run(
                    bash_args,
                    check=True,
                    env={
                        "PATH": os.environ["PATH"],
                        "PS1": "mitm-bash> "
                    })
            case Agent.PI:
                print("Starting pi...")
                env = os.environ.copy()
                env["OPENROUTER_API_KEY"] = get_secret("gerardnico/openrouter/api-key")
                subprocess.run(
                    ["pi"],
                    check=True,
                    env=env)
            case _:
                raise ValueError(f"Unknown agent: {context.agent}")

    except KeyboardInterrupt:
        print("KeyBoard interrupt")
    finally:
        print("Shutting down the proxy")
        proxy.stop()
