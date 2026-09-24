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
class Context:
    # API URL
    api: str
    # Session information
    session: Session
    # For test
    interactive_mode: bool = True
    # Runtime data (such as log)
    runtime_dir: Path = Path.cwd() / ".aitm"
    # XDG_DATA_HOME
    user_dir: Path = Path(user_data_dir("aitm", "aitm"))
    # the agent to wrap
    agent: Agent = Agent.BASH,
    # the port for mitm
    mitm_port: int = 8080
