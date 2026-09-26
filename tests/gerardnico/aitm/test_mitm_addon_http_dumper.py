from gerardnico.aitm.context import build_context
from gerardnico.aitm.mitm_addon_http_logger import HttpDumper
from mitmproxy.test import tflow, taddons


def test__handle_sse_stream():
    context = build_context()
    collector = context.session.collector
    http_dumper = HttpDumper(
        context.session.http_dump_dir,
        context.agent.host,
        collector
    )
    with taddons.context(http_dumper):
        flow = tflow.tflow(resp=True)
        assert flow.response is not None
        flow.response.headers["Content-Type"] = "text/event-stream"

        http_dumper.responseheaders(flow)
        assert callable(flow.response.stream), "must be a function"

        perfect_chunks = [
            b'data: {"token": "hello"}\n\n',
            # chunk that don't stop at the separator
            b'data: {"token": "hello"}\n\ndata: {"token": ',
            b'"hello"}\n\n'
        ]
        for chunk in perfect_chunks:
            result = http_dumper._handle_sse_stream(chunk)
            assert result == chunk, f"return the chunk untouched"

        assert len(collector.events) == 3
