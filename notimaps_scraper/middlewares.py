from scrapy import signals


class NotiMapsCrawlerMiddleware:
    """Downloader middleware for the NotiMaps scraper.

    Logs each request and response for debugging purposes and can be extended
    to add custom headers, handle retries, or rotate proxies.
    """

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        spider.logger.debug("Requesting: %s", request.url)
        return None

    def process_response(self, request, response, spider):
        spider.logger.debug("Response %s for: %s", response.status, request.url)
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.error("Exception on %s: %s", request.url, exception)

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s", spider.name)
