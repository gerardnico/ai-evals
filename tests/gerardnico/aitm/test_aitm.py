from gerardnico.aitm.aitm import Aitm
from gerardnico.aitm.api import Agent
from gerardnico.aitm.context import build_context, Context


def test_aitm_run_bash():
    port = 8080
    context: Context = build_context(
        agent=Agent.BASH,
        mitm_port=port,
        agent_args=["-c", f"curl -x http://localhost:{port} --output /tmp/no-console-output.txt https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024"]
    )
    assert context.agent_interactive == False
    Aitm(context).run()
    assert context.session.result is not None
    assert context.session.result.returncode == 0
    assert context.session.count == 1
