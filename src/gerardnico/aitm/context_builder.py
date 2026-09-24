from gerardnico.aitm.api import Context, Agent, Session
from datetime import datetime


class ContextBuilder:

    def __init__(self):
        self.port = 8080
        self.agent_args = []
        self.api = None
        self.agent = Agent.BASH

    def with_agent(self, agent: Agent) -> "ContextBuilder":
        self.agent = agent
        return self

    def with_api(self, api: str) -> "ContextBuilder":
        self.api = api
        return self

    def with_args(self, agent_args: list[str]) -> "ContextBuilder":
        self.agent_args = agent_args
        return self

    def build(self) -> "Context":

        if self.api is None:
            match self.agent:
                case Agent.BASH:
                    self.api = "https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024"
        if self.api is None:
            raise Exception("Model Api should be defined")

        context = Context(
            agent=self.agent,
            api=self.api,
            session=Session(
                # we replace because we get a problem with : in bash
                id=datetime.now().isoformat(timespec="seconds").replace(":", "-")
            ),
            agent_args=self.agent_args,
            mitm_port=self.port
        )
        # Be sure to have the runtime dir
        context.runtime_dir.mkdir(parents=True, exist_ok=True)
        return context

    def with_port(self, port: int):
        self.port = port
        return self
