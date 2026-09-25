import os
import signal
import subprocess

import sys

from gerardnico.aitm.api import Agent
from gerardnico.aitm.context import Context
from gerardnico.aitm.mitm import MitmproxyRunner
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
            print("Starting Aitm")
            self.proxy.start()

            agent_args = []
            agent_env = os.environ.copy()
            agent_env |= {
                # Pi uses the uppercase env
                "HTTP_PROXY": self.context.mitm_url,
                "HTTPS_PROXY": self.context.mitm_url,
                # Lowercase env
                "http_proxy": self.context.mitm_url,
                "https_proxy": self.context.mitm_url,
                # Aitm env
                "AITM_AGENT": "true",  # lets child agent/processes detect that they run inside aitm
                "AITM_SESSION_ID": self.context.session.id,
                "AITM_SESSION_DIR": self.context.runtime_dir / "fetch-logs" / self.context.session.id,
                # For node app such as pi
                # NODE_OPTIONS does not work does not work
                # "NODE_OPTIONS": "--use-system-ca --use-openssl-ca",
                # Tested with: NODE_OPTIONS="--use-openssl-ca" HTTP_PROXY=http://127.0.0.1:8080 OPENROUTER_API_KEY=$(pass "gerardnico/openrouter/api-key") pi
                "NODE_EXTRA_CA_CERTS": str(self.proxy.ca_cert_path)
            }

            match self.context.agent:
                case Agent.BASH:
                    print("Starting bash... try curl https://httpbin.org/ip")
                    # Curl
                    # --insecure: not needed due to ca-cert and installation and env below
                    # -x {self.context.mitm_url}: not needed due to the HTTP_PROXY env
                    agent_env["CURL_CA_BUNDLE"] = str(self.proxy.ca_cert_path)
                    # Args
                    agent_args = ["bash"]
                    # Aitm Shell
                    # to not start as if it was the user shell
                    # we disable login and interactive script
                    # otherwise you think that you are back in your shell
                    # but, you are not, you need to exit
                    if self.context.agent_interactive:
                        agent_env["PS1"] = "aitm-bash> "
                        agent_args += ["--noprofile", "--norc"]
                case Agent.PI:
                    # https://pi.dev/docs/latest/configuration#agent-directory

                    session_directory = self.context.runtime_dir / "pi-session"
                    session_directory.mkdir(parents=True, exist_ok=True)
                    agent_env |= {
                        "PI_CODING_AGENT_SESSION_DIR": str(session_directory)
                    }
                    # agent_directory = self.context.runtime_dir / "pi-agent"
                    # agent_directory.mkdir(parents=True, exist_ok=True)
                    # pi.update_base_url(
                    #     # default: ~/.pi/agent/models.json
                    #     models_path=agent_directory / "models.json",
                    #     provider="openrouter",
                    #     base_url=f"{self.context.mitm_url}/{Provider.OPENROUTER.value}/api/v1",
                    # )
                    # agent_env |= {
                    #     "PI_CODING_AGENT_DIR": str(agent_directory),
                    # }
                    print("Starting pi...")
                    # https://pi.dev/docs/latest/environment-variables#pi-process-configuration
                    agent_env |= {
                        "OPENROUTER_API_KEY": get_secret("gerardnico/openrouter/api-key"),
                    }
                    agent_args = (
                        [
                            "pi",
                            "--session-id",
                            self.context.session.id
                        ]
                    )
                case _:
                    raise ValueError(f"Unknown agent: {self.context.agent}")

            # Run
            capture_std_output = False
            if not self.context.agent_interactive:
                capture_std_output = True
            agent_args += self.context.agent_args
            result = subprocess.run(
                agent_args,
                # don't throw if any error
                check=False,
                env=agent_env,
                capture_output=capture_std_output,
                # decode string instead of bytes
                text=True
            )
            self.context.session.result = result
        except KeyboardInterrupt:
            print("KeyBoard interrupt")
        finally:
            self.stop()
            session_result = self.context.session.result
            if session_result is not None:
                returncode = session_result.returncode
                if returncode != 0:
                    print(f"Errors where seen", file=sys.stderr)
                    stderr = session_result.stdout + session_result.stderr
                    print(stderr, file=sys.stderr)
                sys.exit(returncode)
