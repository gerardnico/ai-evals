from pathlib import Path

from attr import dataclass
from gerardnico.aitm.api import Agent, Session
from datetime import datetime

from platformdirs import user_data_dir


def build_context(mitm_port=8080,
                  agent_args=[],
                  default_provider_url=None,
                  agent=Agent.BASH) -> "Context":
    if agent_args is None:
        agent_args = []
    if default_provider_url is None:
        match agent:
            case Agent.BASH:
                default_provider_url = "https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024"

    # Interactivity
    agent_interactive: bool = True
    match agent:
        case Agent.BASH:
            if agent_args.__contains__("-c"):
                agent_interactive = False
        case Agent.PI:
            if agent_args.__contains__("-p"):
                agent_interactive = False

    # Building context
    context = Context(
        agent=agent,
        default_provider_url=default_provider_url,
        session=Session(
            # we replace because we get a problem with : in bash
            id=datetime.now().isoformat(timespec="seconds").replace(":", "-"),
            result=None
        ),
        agent_args=agent_args,
        agent_interactive=agent_interactive,
        mitm_port=mitm_port
    )
    # Be sure to have the runtime dir
    context.runtime_dir.mkdir(parents=True, exist_ok=True)
    return context


@dataclass
class Context:
    # API URL
    default_provider_url: str | None
    # Session information
    session: Session
    # the web port for mitm
    mitm_web: int | None = 8081
    # the port for mitm
    mitm_port: int = 8080
    # Runtime data (such as log)
    runtime_dir: Path = Path.cwd() / ".aitm"
    # XDG_DATA_HOME
    user_dir: Path = Path(user_data_dir("aitm", "aitm"))
    # the agent to wrap
    agent: Agent = Agent.BASH,
    # start the agent in interactive mode
    agent_interactive: bool = True,
    # the agent arguments
    agent_args: list[str] = []

    @property
    def mitm_host(self) -> str:
        return "localhost"

    @property
    def mitm_url(self) -> str:
        return f"http://{self.mitm_host}:{self.mitm_port}"
