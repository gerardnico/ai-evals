from gerardnico.aitm.api import Context, Agent, Session
from datetime import datetime


def build_context(mitm_port = 8080,
                  agent_args = [],
                  default_provider_url = None,
                  agent = Agent.BASH) -> "Context":
    if default_provider_url is None:
        match agent:
            case Agent.BASH:
                default_provider_url = "https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024"

    context = Context(
        agent=agent,
        default_provider_url=default_provider_url,
        session=Session(
            # we replace because we get a problem with : in bash
            id=datetime.now().isoformat(timespec="seconds").replace(":", "-")
        ),
        agent_args=agent_args,
        mitm_port=mitm_port
    )
    # Be sure to have the runtime dir
    context.runtime_dir.mkdir(parents=True, exist_ok=True)
    return context

class ContextBuilder:

    def __init__(self):
        self.mitm_port = 8080
        self.agent_args = []
        self.default_base_url = None
        self.agent = Agent.BASH

    def with_agent(self, agent: Agent) -> "ContextBuilder":
        self.agent = agent
        return self

    def with_default_base_url(self, base_url: str) -> "ContextBuilder":
        self.default_base_url = base_url
        return self

    def with_agent_args(self, agent_args: list[str]) -> "ContextBuilder":
        self.agent_args = agent_args
        return self

    def with_proxy_port(self, port: int):
        self.mitm_port = port
        return self

    def build(self) -> "Context":

        if self.default_base_url is None:
            match self.agent:
                case Agent.BASH:
                    self.default_base_url = "https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024"

        context = Context(
            agent=self.agent,
            default_provider_url=self.default_base_url,
            session=Session(
                # we replace because we get a problem with : in bash
                id=datetime.now().isoformat(timespec="seconds").replace(":", "-")
            ),
            agent_args=self.agent_args,
            mitm_port=self.mitm_port
        )
        # Be sure to have the runtime dir
        context.runtime_dir.mkdir(parents=True, exist_ok=True)
        return context


