from gerardnico.aitm.mitm_addon_redirect import get_redirect_base_url


def test_base_url():
    base_url = get_redirect_base_url("/openrouter/api/v1", "default")
    assert base_url == "https://openrouter.ai/api/v1"
