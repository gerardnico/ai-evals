from datetime import datetime

from gerardnico.aitm import aitm
from gerardnico.aitm.api import Context, Agent, Session
import asyncio

from gerardnico.aitm.context_builder import ContextBuilder


def test_file_url_request():
    port = 8080
    context: Context = (
        ContextBuilder()
        .with_agent(Agent.BASH)
        .with_api("https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024")
        .with_port(port)
        .with_args(["-c",f"curl -s -x http://localhost:{port} --output /tmp/no-console-output.txt http://example.com"])
        .build()
    )
    """Run"""
    asyncio.run(aitm.run(context))
