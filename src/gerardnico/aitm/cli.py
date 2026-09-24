import asyncio
import logging

import typer
from gerardnico.aitm import aitm
from gerardnico.aitm.context_builder import ContextBuilder
from gerardnico.aitm.api import Agent, Context

typerCli = typer.Typer()

logger = logging.getLogger(__name__)


@typerCli.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def run(
        ctx: typer.Context,
        agent: Agent = Agent.BASH,
):
    """Run an agent"""
    context: Context = (
        ContextBuilder()
        .with_agent(agent)
        .with_agent_args(ctx.args)
        .build()
    )
    asyncio.run(aitm.run(context))

@typerCli.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def bash(
        ctx: typer.Context,
):
    """Run Bash"""
    # aitm bash -c "curl -x http://localhost:8080 http://example.com"
    context: Context = (
        ContextBuilder()
        .with_agent(Agent.BASH)
        .with_agent_args(ctx.args)
        .build()
    )
    asyncio.run(aitm.run(context))

@typerCli.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def pi(
        ctx: typer.Context,
):
    """Run Pi"""
    context: Context = (
        ContextBuilder()
        .with_agent(Agent.PI)
        .with_agent_args(ctx.args)
        .build()
    )
    asyncio.run(aitm.run(context))


# By default, the callback is only executed before executing a command.
@typerCli.callback()
def callback(
        ctx: typer.Context
):
    """
    Main
    """
    logger.info(f"About to execute command: {ctx.invoked_subcommand}")


def cli():
    """
    Entry point function for the CLI installation used in the pyproject.toml
    """
    typerCli()


if __name__ == '__main__':
    typerCli(["run"])
