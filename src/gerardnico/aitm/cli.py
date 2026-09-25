import asyncio
import logging

import typer
from gerardnico.aitm import aitm
from gerardnico.aitm.aitm import Aitm
from gerardnico.aitm.context import ContextBuilder, Context, build_context
from gerardnico.aitm.api import Agent

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
    context: Context = build_context(
        agent=agent,
        agent_args=ctx.args
    )
    Aitm(context).run()


@typerCli.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def bash(
        ctx: typer.Context,
):
    """
        Run Bash
        example: aitm bash -c "curl -x http://localhost:8080 http://example.com"
    """

    context: Context = build_context(
        agent=Agent.BASH,
        agent_args=ctx.args
    )
    Aitm(context).run()


@typerCli.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def pi(
        ctx: typer.Context,
):
    """Run Pi"""
    context: Context = build_context(
        agent=Agent.PI,
        agent_args=ctx.args
    )
    Aitm(context).run()


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
