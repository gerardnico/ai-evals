from gerardnico.aitm.context import build_context
from gerardnico.aitm.mitm_addon_http_logger import HttpDumper
from mitmproxy.test import tflow, taddons

def test__handle_event_stream():
    context = build_context()
    http_dumper = HttpDumper(context.session.http_dump_dir)
    with taddons.context(http_dumper):
        flow = tflow.tflow(resp=True)
        assert flow.response is not None
        flow.response.headers["Content-Type"] = "text/event-stream"

        # stream function
        http_dumper.responseheaders(flow)
        assert callable(flow.response.stream)

        chunk = b'data: {"token": "hello"}\n\n'
        result = http_dumper._handle_event_stream(chunk)

        assert result == chunk, f"return the chunk untouched"



        assert flow.response.headers["X-Frame-Options"] == "DENY"
