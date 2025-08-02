import requests

from src import scraper


class DummyResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if not (200 <= self.status_code < 300):
            raise requests.HTTPError()


def test_fetch_uses_cache(tmp_path, monkeypatch):
    html = '<h1>Paint</h1><div class="price">$5</div>'
    session = requests.Session()
    calls = {"count": 0}

    def fake_get(url, headers, timeout):
        calls["count"] += 1
        return DummyResponse(html)

    monkeypatch.setattr(session, "get", fake_get)
    monkeypatch.setattr(scraper.time, "sleep", lambda x: None)

    info1 = scraper.fetch_paint_price(
        "abc", session=session, use_cache=True, cache_dir=tmp_path
    )
    assert calls["count"] == 1

    info2 = scraper.fetch_paint_price(
        "abc", session=session, use_cache=True, cache_dir=tmp_path
    )
    assert calls["count"] == 1
    assert info1 == info2


def test_fetch_respects_delay(monkeypatch):
    html = '<h1>Paint</h1><div class="price">$5</div>'
    session = requests.Session()
    monkeypatch.setattr(session, "get", lambda url, headers, timeout: DummyResponse(html))

    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(scraper.time, "sleep", fake_sleep)
    scraper.fetch_paint_price("abc", session=session, delay=0.5)
    assert sleep_calls and sleep_calls[0] == 0.5
