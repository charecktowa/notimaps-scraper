# Scrapy settings for notimaps_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os

BOT_NAME = "notimaps_scraper"

SPIDER_MODULES = ["notimaps_scraper.spiders"]
NEWSPIDER_MODULE = "notimaps_scraper.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "notimaps-scraper (+https://github.com/charecktowa/notimaps-scraper)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "notimaps_scraper.middlewares.NotiMapsCrawlerMiddleware": 543,
}

# Configure item pipelines
ITEM_PIPELINES = {
    "notimaps_scraper.pipelines.DatabasePipeline": 300,
}

# Database URL — defaults to a local SQLite file; override via env var for production.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///notimaps.db")

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
