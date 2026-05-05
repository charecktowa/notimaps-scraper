"""Tests for the NewsSpider."""

import pytest
from scrapy.http import HtmlResponse, Request

from notimaps_scraper.items import NewsArticle
from notimaps_scraper.spiders.news_spider import NewsSpider


def _fake_response(url: str, body: str) -> HtmlResponse:
    """Build a fake HtmlResponse for testing."""
    request = Request(url=url)
    return HtmlResponse(url=url, body=body.encode(), request=request)


def test_parse_extracts_article_links():
    """parse() should yield Follow requests for article links found on the page."""
    spider = NewsSpider()
    html = """
    <html><body>
        <h2><a href="/article/1">Article One</a></h2>
        <h3><a href="/article/2">Article Two</a></h3>
    </body></html>
    """
    response = _fake_response("https://example.com/news", html)
    results = list(spider.parse(response))
    urls = [r.url for r in results]
    assert "https://example.com/article/1" in urls
    assert "https://example.com/article/2" in urls


def test_parse_article_yields_item():
    """parse_article() should yield a NewsArticle with the correct fields."""
    spider = NewsSpider()
    html = """
    <html><body>
        <h1>Local Mayor Wins Election</h1>
        <time datetime="2024-11-05T12:00:00Z">November 5, 2024</time>
        <p>The mayor won by a landslide.</p>
    </body></html>
    """
    response = _fake_response("https://example.com/article/1", html)
    results = list(spider.parse_article(response))

    assert len(results) == 1
    item = results[0]
    assert isinstance(item, NewsArticle)
    assert item["title"] == "Local Mayor Wins Election"
    assert item["url"] == "https://example.com/article/1"
    assert "2024-11-05" in item["published_at"]
    assert "landslide" in item["summary"]


def test_parse_article_skips_missing_title():
    """parse_article() should not yield an item when the title selector returns nothing."""
    spider = NewsSpider()
    html = "<html><body><p>No title here.</p></body></html>"
    response = _fake_response("https://example.com/article/2", html)
    results = list(spider.parse_article(response))
    assert results == []


def test_parse_follows_pagination():
    """parse() should follow a rel=next link when present."""
    spider = NewsSpider()
    html = """
    <html><body>
        <h2><a href="/article/1">Article One</a></h2>
        <a rel="next" href="/news?page=2">Next</a>
    </body></html>
    """
    response = _fake_response("https://example.com/news", html)
    results = list(spider.parse(response))
    urls = [r.url for r in results]
    assert "https://example.com/news?page=2" in urls
