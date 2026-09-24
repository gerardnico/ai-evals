import logging

import typer
import asyncio

from gerardnico.mitm import main

typerCli = typer.Typer()

logger = logging.getLogger(__name__)


@typerCli.command()
def run(
        ctx: typer.Context
):
    """Run"""
    asyncio.run(main.run())


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
    cli()
