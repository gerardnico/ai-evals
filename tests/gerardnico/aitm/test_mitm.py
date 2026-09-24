from datetime import datetime

from gerardnico.aitm import aitm
from gerardnico.aitm.api import Context, Agent, Session
import asyncio


def test_file_url_request():
    context: Context = Context(
        agent=Agent.BASH,
        api="https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024",
        session=Session(
            # we replace because we get a problem with : in bash
            id=datetime.now().isoformat(timespec="seconds").replace(":", "-")
        ),
        interactive_mode=False
    )
    # Be sure to have the runtime dir
    context.runtime_dir.mkdir(parents=True, exist_ok=True)
    """Run"""
    asyncio.run(aitm.run(context))
