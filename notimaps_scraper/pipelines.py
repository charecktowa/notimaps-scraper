from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


class ArticleModel(Base):
    __tablename__ = "articles"

    url = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    published_at = Column(String)
    summary = Column(Text)
    source = Column(String)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DatabasePipeline:
    """Stores scraped news articles into a SQL database via SQLAlchemy."""

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.engine = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(database_url=crawler.settings.get("DATABASE_URL"))

    def open_spider(self, spider):
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        spider.logger.info("Database connection opened: %s", self.database_url)

    def close_spider(self, spider):
        if self.engine:
            self.engine.dispose()
            spider.logger.info("Database connection closed.")

    def process_item(self, item, spider):
        with Session(self.engine) as session:
            article = ArticleModel(
                url=item.get("url"),
                title=item.get("title"),
                published_at=item.get("published_at"),
                summary=item.get("summary"),
                source=item.get("source"),
                scraped_at=item.get("scraped_at", datetime.now(timezone.utc)),
            )
            session.merge(article)  # upsert by primary key (url)
            session.commit()
        return item
