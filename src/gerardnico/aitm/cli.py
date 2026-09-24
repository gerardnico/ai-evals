import asyncio
import logging
from datetime import datetime

import typer
from gerardnico.aitm import aitm
from gerardnico.aitm.api import Agent, Context, Session

typerCli = typer.Typer()

logger = logging.getLogger(__name__)


@typerCli.command()
def run(
        ctx: typer.Context,
        agent: Agent = Agent.BASH,
):
    context: Context = Context(
        agent=agent,
        api="https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024",
        session=Session(
            # we replace because we get a problem with : in bash
            id=datetime.now().isoformat(timespec="seconds").replace(":","-")
        )
    )
    # Be sure to have the runtime dir
    context.runtime_dir.mkdir(parents=True, exist_ok=True)
    """Run"""
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
