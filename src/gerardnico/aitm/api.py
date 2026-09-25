from enum import Enum

from attr import dataclass
from pathlib import Path
from subprocess import CompletedProcess


class Agent(str, Enum):
    """The agent/cli that we wrap"""
    PI = "pi"
    BASH = "bash"


@dataclass
class Session:
    # Session id
    id: str
    # agent result
    result: CompletedProcess[str]|None
    # Request count
    count: int = 0


@dataclass
class Pi:
    # Config model
    conf: Path
