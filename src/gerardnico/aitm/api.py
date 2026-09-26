from enum import Enum
from pathlib import Path
from subprocess import CompletedProcess

from attr import dataclass


class Agent(str, Enum):
    """The agent/cli that we wrap"""
    PI = ("pi", "pi.dev")
    BASH = ("bash", None)

    def __new__(cls, value: str, host: str | None):
        # noinspection PyTypeChecker
        obj = str.__new__(cls, value)
        # https://docs.python.org/3/library/enum.html#supported-sunder-names
        obj._value_ = value
        # used to see if the agent makes calls to its base
        obj.host = host
        return obj


@dataclass
class Collector:
    # Request count
    count: int = 0
    # Event
    events: list[object] = []


@dataclass
class Session:
    # Session id
    id: str
    # Dump Dir
    http_dump_dir: Path
    # agent result (return code)
    result: CompletedProcess[str] | None
    # collector
    collector: Collector

@dataclass
class Pi:
    # Config model
    conf: Path
