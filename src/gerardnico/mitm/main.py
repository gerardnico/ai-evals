from gerardnico.mitm.mitm import MitmproxyRunner

import subprocess
import os
import asyncio

async def run() -> None:
    """Runs master.run() in its own event loop, in a separate thread."""
    proxy = MitmproxyRunner()

    try:
        print("starting mitm...")
        proxy.start()
        # Inherits the current stdin/stdout/stderr, so the user can type
        # commands directly and see output live, just like a normal shell.
        print("Calling bash...")
        subprocess.run(
            ["bash", "--noprofile", "--norc", "-i"],
            check=True,
            env={
                "PATH": os.environ["PATH"],
                "PS1": "mitm-bash> "
            })
    except KeyboardInterrupt:
        print("shutting down...")
        proxy.stop()
    finally:
        print("shutting down finally...")
        proxy.stop()


if __name__ == "__main__":
    asyncio.run(run())
