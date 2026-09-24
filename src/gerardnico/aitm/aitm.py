import os
import signal
import subprocess
import sys

from gerardnico.aitm import pi
from gerardnico.aitm.api import Context, Agent, Pi
from gerardnico.aitm.mitm import MitmproxyRunner
from gerardnico.aitm.mitm_addon_redirect import Provider
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

        agent_args = []
        agent_env = {}
        match context.agent:
            case Agent.BASH:
                print("Starting bash...")
                print(f"e.g.: curl -x {context.mitm_url} http://example.com")
                agent_args = ["bash"]
                if len(context.agent_args) == 0:
                    agent_args += ["--noprofile", "--norc", "-i"]
                else:
                    agent_args += context.agent_args
                agent_env = {
                    "PATH": os.environ["PATH"],
                    "PS1": "mitm-bash> "
                }
            case Agent.PI:
                # https://pi.dev/docs/latest/configuration#agent-directory
                agent_directory = context.runtime_dir / "pi-agent"
                agent_directory.mkdir(parents=True, exist_ok=True)
                pi.update_base_url(
                    # default: ~/.pi/agent/models.json
                    models_path=agent_directory / "models.json",
                    provider="openrouter",
                    base_url=f"{context.mitm_url}/{Provider.OPENROUTER.value}/api/v1",
                )
                print("Starting pi...")
                agent_env = os.environ.copy()
                agent_env["OPENROUTER_API_KEY"] = get_secret("gerardnico/openrouter/api-key")
                agent_env["PI_CODING_AGENT_DIR"] = str(agent_directory)
                agent_args = ["pi"] + context.agent_args
            case _:
                raise ValueError(f"Unknown agent: {context.agent}")

        subprocess.run(
            agent_args,
            check=True,
            env=agent_env
        )

    except KeyboardInterrupt:
        print("KeyBoard interrupt")
    finally:
        print("Shutting down the proxy")
        proxy.stop()
