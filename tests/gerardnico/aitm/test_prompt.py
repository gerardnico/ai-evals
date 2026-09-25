from gerardnico.aitm.aitm import Aitm
from gerardnico.aitm.api import Agent
from gerardnico.aitm.context import build_context, Context


def test_at_file():
    """
    Test the @ in a prompt
    In the system prompt, there is: <cwd>/home/user/current_dir</cwd>
    """
    file_path="fixtures/file_read.txt"
    context: Context = build_context(
        agent=Agent.PI,
        agent_args=["-p", f"Can you read the file @{file_path}"]
    )
    assert context.agent_interactive == False
    Aitm(context).run()
    assert context.session.count == 2
    assert context.session.result is not None
    assert context.session.result.returncode == 0
    with open(file_path, "r") as f:
        content = f.read()
    # Response example:
    #
    # The contents of `fixtures/file_read.txt`:
    #
    # ```
    # Hello World
    # ```
    #
    assert context.session.result.stdout.__contains__(content)