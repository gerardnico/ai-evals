from enum import Enum

from attr import dataclass
from pathlib import Path

from platformdirs import user_data_dir


class Agent(str, Enum):
    """The agent/cli that we wrap"""
    PI = "pi"
    BASH = "bash"


@dataclass
class Session:
    # Session id
    id: str
    # Request count
    count: int = 0


@dataclass
class Pi:
    # Config model
    conf: Path


@dataclass
class Context:
    # API URL
    default_provider_url: str | None
    # Session information
    session: Session
    # the web port for mitm
    mitm_web: int|None = 8081
    # the port for mitm
    mitm_port: int = 8080
    # Runtime data (such as log)
    runtime_dir: Path = Path.cwd() / ".aitm"
    # XDG_DATA_HOME
    user_dir: Path = Path(user_data_dir("aitm", "aitm"))
    # the agent to wrap
    agent: Agent = Agent.BASH,
    # the agent arguments
    agent_args: list[str] = []

    @property
    def mitm_host(self) -> str:
        return "localhost"

    @property
    def mitm_url(self) -> str:
        return f"http://{self.mitm_host}:{self.mitm_port}"
