# notimaps-scraper

A web scraper for news sites built with [Scrapy](https://scrapy.org/), managed with [uv](https://github.com/astral-sh/uv), and deployable to **Docker** (local) or **AWS Lambda** (production).

## Features

- Generic `NewsSpider` that extracts article titles, URLs, publication dates, and summaries via configurable CSS selectors.
- Stores scraped articles in a SQL database (SQLite by default; any SQLAlchemy-compatible engine in production) with upsert support.
- Multi-stage `Dockerfile` using uv for fast, reproducible builds.
- `docker-compose.yml` for one-command local deployment.
- `lambda_handler.py` entry point for serverless execution on AWS Lambda.

## Project structure

```
notimaps-scraper/
├── notimaps_scraper/
│   ├── spiders/
│   │   └── news_spider.py   # Generic news spider
│   ├── items.py             # NewsArticle item
│   ├── middlewares.py       # Custom downloader middleware
│   ├── pipelines.py         # SQLAlchemy database pipeline
│   └── settings.py          # Scrapy settings
├── tests/                   # pytest test suite
├── lambda_handler.py        # AWS Lambda entry point
├── Dockerfile               # Multi-stage Docker build (uv)
├── docker-compose.yml       # Local deployment
├── scrapy.cfg
└── pyproject.toml
```

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (or Docker)

## Local development

```bash
# Install dependencies
uv sync

# Run the spider (prints scraped items to stdout)
uv run scrapy crawl news -s START_URLS="https://news.ycombinator.com"

# Run tests
uv run pytest
```

## Docker (local deployment)

```bash
# Build and run with docker compose
docker compose up --build

# Run against custom URLs
docker compose run scraper scrapy crawl news \
  -s START_URLS="https://news.ycombinator.com"
```

Scraped articles are persisted to a named Docker volume (`scraper-data`) at `/data/notimaps.db`.

## Configuration

| Environment variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///notimaps.db` | SQLAlchemy connection string |
| `SPIDER_NAME` | `news` | Spider to run in Lambda |
| `START_URLS` | _(empty)_ | Comma-separated seed URLs |
| `SCRAPY_LOG_LEVEL` | `WARNING` | Log verbosity in Lambda |

## AWS Lambda

Package the project and deploy `lambda_handler.handler` as the Lambda function handler.
Set `DATABASE_URL` to your RDS/Aurora endpoint and `START_URLS` to the news site(s) you want to scrape.

```json
{
  "spider_name": "news",
  "start_urls": ["https://news.ycombinator.com"]
}
```

The handler returns a JSON response with the number of items scraped and the items themselves.
