"""AWS Lambda entry point for the NotiMaps scraper.

The Lambda function triggers one or more Scrapy spiders, collects the scraped
items, and returns them as JSON.  The ``DATABASE_URL`` environment variable
controls where items are persisted (defaults to an in-memory SQLite database
so that the Lambda invocation stays stateless and quick to test).

Environment variables
---------------------
DATABASE_URL
    SQLAlchemy-compatible connection string.  For production use, set this to
    an RDS/Aurora endpoint, e.g.
    ``postgresql+psycopg2://user:pass@host/dbname``.
    Defaults to ``sqlite:///:memory:``.
SPIDER_NAME
    Name of the Scrapy spider to run.  Defaults to ``"news"``.
START_URLS
    Comma-separated list of seed URLs for the spider.
"""

import json
import logging
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def handler(event: dict, context) -> dict:  # noqa: ANN001
    """Lambda handler — runs the configured spider and returns scraped items.

    Parameters
    ----------
    event:
        Lambda event payload.  Supported keys:

        - ``spider_name`` (str): override the spider to run.
        - ``start_urls`` (list[str]): seed URLs for the spider.
    context:
        Lambda runtime context (unused).
    """
    spider_name = event.get("spider_name") or os.getenv("SPIDER_NAME", "news")
    start_urls = event.get("start_urls") or [
        u.strip()
        for u in os.getenv("START_URLS", "").split(",")
        if u.strip()
    ]

    settings = get_project_settings()
    # Use an in-memory DB by default so Lambda remains stateless; override via env.
    settings.set(
        "DATABASE_URL",
        os.getenv("DATABASE_URL", "sqlite:///:memory:"),
        priority="cmdline",
    )
    # Silence Scrapy's verbose logging inside Lambda.
    settings.set("LOG_LEVEL", os.getenv("SCRAPY_LOG_LEVEL", "WARNING"), priority="cmdline")

    scraped_items: list[dict] = []

    def collect_item(item, response, spider):  # noqa: ANN001, ARG001
        scraped_items.append(dict(item))

    process = CrawlerProcess(settings)
    crawler = process.create_crawler(spider_name)
    crawler.signals.connect(collect_item, signal="item_scraped")
    process.crawl(crawler, start_urls=start_urls)
    process.start()

    logger.info("Spider '%s' finished. Items scraped: %d", spider_name, len(scraped_items))

    return {
        "statusCode": 200,
        "body": json.dumps(
            {"spider": spider_name, "items_scraped": len(scraped_items), "items": scraped_items},
            default=str,
        ),
    }
