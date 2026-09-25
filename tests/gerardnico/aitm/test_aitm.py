from gerardnico.aitm.aitm import Aitm
from gerardnico.aitm.api import Context, Agent
from gerardnico.aitm.context_builder import ContextBuilder, build_context



def test_aitm_run_bash():
    port = 8080
    context: Context = build_context(
        agent=Agent.BASH,
        default_provider_url="https://webhook.site/ddb009b6-d74c-4cf7-9491-fb8472828024",
        mitm_port=port,
        agent_args=["-c", f"curl -s -x http://localhost:{port} --output /tmp/no-console-output.txt http://example.com"]
    )
    Aitm(context).run()
    assert context.session.count == 1
