"""Tests for the DatabasePipeline."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from notimaps_scraper.items import NewsArticle
from notimaps_scraper.pipelines import ArticleModel, DatabasePipeline


@pytest.fixture()
def pipeline():
    """Return a DatabasePipeline wired to an in-memory SQLite database."""
    p = DatabasePipeline(database_url="sqlite:///:memory:")
    spider = MagicMock()
    p.open_spider(spider)
    return p


def test_pipeline_creates_table(pipeline):
    """The pipeline should create the articles table on open."""
    from sqlalchemy import inspect

    inspector = inspect(pipeline.engine)
    assert "articles" in inspector.get_table_names()


def test_pipeline_stores_item(pipeline):
    """process_item should persist a NewsArticle to the database."""
    from sqlalchemy.orm import Session

    item = NewsArticle(
        title="Breaking News",
        url="https://example.com/breaking",
        published_at="2024-01-01T00:00:00Z",
        summary="Something happened.",
        source="news",
        scraped_at=datetime.now(timezone.utc),
    )

    spider = MagicMock()
    returned = pipeline.process_item(item, spider)

    assert returned is item  # pipeline must return the item

    with Session(pipeline.engine) as session:
        article = session.get(ArticleModel, "https://example.com/breaking")
        assert article is not None
        assert article.title == "Breaking News"
        assert article.summary == "Something happened."


def test_pipeline_upserts_item(pipeline):
    """Storing an item with the same URL twice should not raise and should update."""
    from sqlalchemy.orm import Session

    spider = MagicMock()
    item = NewsArticle(
        title="Old Title",
        url="https://example.com/article",
        source="news",
        scraped_at=datetime.now(timezone.utc),
    )
    pipeline.process_item(item, spider)

    item["title"] = "Updated Title"
    pipeline.process_item(item, spider)

    with Session(pipeline.engine) as session:
        articles = session.query(ArticleModel).filter_by(url="https://example.com/article").all()
        assert len(articles) == 1
        assert articles[0].title == "Updated Title"


def test_pipeline_close_spider(pipeline):
    """close_spider should not raise."""
    spider = MagicMock()
    pipeline.close_spider(spider)  # should not raise
