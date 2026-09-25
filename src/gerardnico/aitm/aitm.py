import os
import signal
import subprocess

from gerardnico.aitm import pi
from gerardnico.aitm.api import Agent
from gerardnico.aitm.context import Context
from gerardnico.aitm.mitm import MitmproxyRunner
from gerardnico.aitm.mitm_addon_redirect import Provider
from gerardnico.aitm.pass_cli import get_secret


class Aitm:

    def __init__(self, context: Context):
        super().__init__()
        self.context = context
        self.proxy = MitmproxyRunner(self.context)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle IDE debugging shutdown"""
        print(f"Received signal {signum}, shutting down the proxy")
        self.stop()

    def stop(self):
        print("Shutting down the proxy")
        self.proxy.stop()

    def run(self) -> None:
        """Runs master.run() in its own event loop, in a separate thread."""

        try:
            print("Starting proxy...")
            self.proxy.start()

            agent_args = []
            agent_env = {}
            match self.context.agent:
                case Agent.BASH:
                    print("Starting bash...")
                    print(f"e.g.: curl -x {self.context.mitm_url} http://example.com")
                    agent_args = ["bash"]
                    if len(self.context.agent_args) == 0:
                        agent_args += ["--noprofile", "--norc", "-i"]
                    else:
                        agent_args += self.context.agent_args
                    agent_env = {
                        "PATH": os.environ["PATH"],
                        "PS1": "mitm-bash> "
                    }
                case Agent.PI:
                    # https://pi.dev/docs/latest/configuration#agent-directory
                    agent_directory = self.context.runtime_dir / "pi-agent"
                    agent_directory.mkdir(parents=True, exist_ok=True)
                    session_directory = self.context.runtime_dir / "pi-session"
                    session_directory.mkdir(parents=True, exist_ok=True)
                    pi.update_base_url(
                        # default: ~/.pi/agent/models.json
                        models_path=agent_directory / "models.json",
                        provider="openrouter",
                        base_url=f"{self.context.mitm_url}/{Provider.OPENROUTER.value}/api/v1",
                    )
                    print("Starting pi...")
                    agent_env = os.environ.copy()
                    agent_env["OPENROUTER_API_KEY"] = get_secret("gerardnico/openrouter/api-key")
                    agent_env["PI_CODING_AGENT_DIR"] = str(agent_directory)
                    agent_args = (
                            [
                                "pi",
                                "--session-id",
                                self.context.session.id,
                                "--session-dir",
                                str(session_directory)
                            ]
                            + self.context.agent_args
                    )
                case _:
                    raise ValueError(f"Unknown agent: {self.context.agent}")

            capture_output = False
            if not self.context.agent_interactive:
                capture_output = True
            result = subprocess.run(
                agent_args,
                check=True,
                env=agent_env,
                capture_output=capture_output,
                # decode string instead of bytes
                text=True
            )
            self.context.session.result = result
        except KeyboardInterrupt:
            print("KeyBoard interrupt")
        finally:
            self.stop()
