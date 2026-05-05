"""Generic news spider that can be configured for different news sites.

Configure target site(s) by setting the ``start_urls``, ``article_css``
(CSS selector for article links on the index page), and the per-article
CSS selectors via ``-s`` arguments or by subclassing this spider.

Example — run against the built-in test site::

    scrapy crawl news -s START_URLS="https://example.com/news"
"""

from datetime import datetime, timezone

import scrapy

from notimaps_scraper.items import NewsArticle


class NewsSpider(scrapy.Spider):
    name = "news"
    # Override these defaults via ``-s`` command-line settings or subclassing.
    start_urls: list[str] = []

    # CSS selectors — adjust per target site.
    # Selector for <a> tags that link to individual article pages.
    article_link_css: str = "article a::attr(href), h2 a::attr(href), h3 a::attr(href)"
    # Selectors for fields within an article page.
    title_css: str = "h1::text"
    summary_css: str = "p::text"
    published_at_css: str = "time::attr(datetime), time::text"

    custom_settings: dict = {}

    def parse(self, response):
        """Extract links to individual article pages from an index/listing page."""
        links = response.css(self.article_link_css).getall()
        self.logger.info("Found %d article links on %s", len(links), response.url)
        for href in links:
            yield response.follow(href, callback=self.parse_article)

        # Follow pagination
        next_page = response.css("a[rel='next']::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_article(self, response):
        """Extract article data from an individual article page."""
        title = response.css(self.title_css).get("").strip()
        published_at = response.css(self.published_at_css).get("")
        paragraphs = response.css(self.summary_css).getall()
        summary = " ".join(p.strip() for p in paragraphs if p.strip())[:1000]

        if not title:
            self.logger.warning("No title found on %s — skipping.", response.url)
            return

        yield NewsArticle(
            title=title,
            url=response.url,
            published_at=published_at,
            summary=summary,
            source=self.name,
            scraped_at=datetime.now(timezone.utc),
        )
