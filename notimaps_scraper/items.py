import scrapy


class NewsArticle(scrapy.Item):
    """Represents a scraped news article."""

    title = scrapy.Field()
    url = scrapy.Field()
    published_at = scrapy.Field()
    summary = scrapy.Field()
    source = scrapy.Field()
    scraped_at = scrapy.Field()
