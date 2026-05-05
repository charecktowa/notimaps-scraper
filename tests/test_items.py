"""Tests for the NewsArticle item definition."""

import scrapy

from notimaps_scraper.items import NewsArticle


def test_news_article_fields():
    """NewsArticle must expose the expected fields."""
    expected = {"title", "url", "published_at", "summary", "source", "scraped_at"}
    assert set(NewsArticle.fields.keys()) == expected


def test_news_article_is_scrapy_item():
    item = NewsArticle(title="Test", url="https://example.com")
    assert isinstance(item, scrapy.Item)
    assert item["title"] == "Test"
    assert item["url"] == "https://example.com"
