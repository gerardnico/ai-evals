from pathlib import Path

from attr import dataclass
from gerardnico.aitm.api import Agent, Session, Collector
from datetime import datetime

from platformdirs import user_data_dir


def datetime_to_fs_name(time:datetime):
    return time.isoformat(timespec="seconds").replace(":", "-")


def build_context(mitm_port=8080,
                  agent_args=[],
                  agent=Agent.BASH) -> "Context":
    if agent_args is None:
        agent_args = []

    # Interactivity
    agent_interactive: bool = True
    match agent:
        case Agent.BASH:
            if agent_args.__contains__("-c"):
                agent_interactive = False
        case Agent.PI:
            if agent_args.__contains__("-p"):
                agent_interactive = False

    # Runtime dir
    runtime_dir: Path = Path.cwd() / ".aitm"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    # Session
    # we replace : because we get a problem in bash as it's a special character
    session_id = datetime_to_fs_name(datetime.now())
    http_dump_dir = runtime_dir / "sessions" / session_id / "http-dump"

    context = Context(
        agent=agent,
        runtime_dir=runtime_dir,
        session=Session(
            id=session_id,
            result=None,
            http_dump_dir=http_dump_dir,
            collector=Collector()
        ),
        agent_args=agent_args,
        agent_interactive=agent_interactive,
        mitm_port=mitm_port
    )
    return context


@dataclass
class Context:
    # Session information
    session: Session
    # the web port for mitm
    mitm_web_port: int | None = 8081
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
