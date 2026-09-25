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
                    print(
                        f"e.g.: curl -x {self.context.mitm_url} https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024")
                    agent_args = ["bash"]
                    agent_env = os.environ.copy()
                    if len(self.context.agent_args) == 0 and self.context.agent_interactive:
                        agent_args += ["--noprofile", "--norc"]
                        agent_env["PS1"] = "mitm-bash> "
                    else:
                        agent_args += self.context.agent_args
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
                    # https://pi.dev/docs/latest/environment-variables#pi-process-configuration
                    agent_env = os.environ.copy()
                    agent_env["OPENROUTER_API_KEY"] = get_secret("gerardnico/openrouter/api-key")
                    agent_env["PI_CODING_AGENT_DIR"] = str(agent_directory)
                    agent_env["PI_CODING_AGENT_SESSION_DIR"] = str(session_directory)
                    agent_env["HTTP_PROXY"] = self.context.mitm_url
                    agent_args = (
                            [
                                "pi",
                                "--session-id",
                                self.context.session.id
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
                # don't throw if any error
                check=False,
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
