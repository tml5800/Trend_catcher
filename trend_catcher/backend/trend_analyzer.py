from fastapi import FastAPI
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, desc
from sqlalchemy.orm import sessionmaker
import httpx
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./reddit.db"

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

REDDIT_TOP_URL = "https://www.reddit.com/r/popular/top.json?t=month&limit=50"
HEADERS = {"User-Agent": "TrendingFetcherBot/1.0"}

scheduler = AsyncIOScheduler()

class RedditPost(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    subreddit = Column(String)
    url = Column(String)
    score = Column(Integer)
    num_comments = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

async def fetch_and_store_trending():
    async with httpx.AsyncClient() as client:
        response = await client.get(REDDIT_TOP_URL, headers=HEADERS)
        data = response.json()
        posts = data["data"]["children"]

        async with SessionLocal() as session:
            for post in posts:
                p = post["data"]
                reddit_post = RedditPost(
                    id=p["id"],
                    title=p["title"],
                    subreddit=p["subreddit"],
                    url=p["url"],
                    score=p["score"],
                    num_comments=p["num_comments"],
                    created_at=datetime.utcnow()
                )
                await session.merge(reddit_post)
            await session.commit()

async def get_trends():
    async with SessionLocal() as session:
        result = await session.execute(
            RedditPost.__table__.select().order_by(desc(RedditPost.score)).limit(10)
        )
        top_posts = result.fetchall()

        return {
            "top_trending": [
                {
                    "title": post.title,
                    "subreddit": post.subreddit,
                    "url": post.url,
                    "score": post.score,
                    "comments": post.num_comments
                }
                for post in top_posts
            ]
        }

async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await fetch_and_store_trending()
    scheduler.add_job(fetch_and_store_trending, "interval", hours=6)
    scheduler.start()