import asyncio
import json
import logging
import os
import sys

import redis
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from models import Project, Lead, Organization
from database import Base
from services.nlp import score
from config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("worker")

settings = get_settings()

# Sync DB engine for the worker (no async needed here)
DATABASE_URL_SYNC = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
engine = create_engine(DATABASE_URL_SYNC, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

redis_client = redis.from_url(settings.REDIS_URL)

SCRAPE_QUEUE = "queue:scrape"
SCORE_QUEUE = "queue:score"


def process_scrape_job(job_data: dict):
    """Fetch Reddit posts for a project and enqueue scoring."""
    project_id = job_data["project_id"]
    logger.info(f"Scraping for project {project_id}")

    with SessionLocal() as db:
        project = db.get(Project, project_id)
        if not project or not project.is_active:
            logger.warning(f"Project {project_id} not found or inactive")
            return

        keywords = json.loads(project.keywords)
        subreddits = json.loads(project.subreddits) if project.subreddits else None

    # Run async fetch in sync context
    from services.reddit import fetch_reddit
    posts = asyncio.run(fetch_reddit(keywords, subreddits))

    with SessionLocal() as db:
        org = db.execute(
            select(Organization).join(Project).where(Project.id == project_id)
        ).scalar_one_or_none()

        # Count today's leads for rate limiting
        from datetime import datetime, timezone
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        new_count = 0
        for post in posts:
            if not post.get("external_id"):
                continue

            # Skip duplicates
            existing = db.execute(
                select(Lead).where(Lead.external_id == post["external_id"])
            ).scalar_one_or_none()
            if existing:
                continue

            # Check daily limit
            if org and new_count >= org.max_leads_per_day:
                logger.warning(f"Daily lead limit reached for org {org.id}")
                break

            intent_score = score(post["content"])

            lead = Lead(
                platform=post["platform"],
                author_handle=post["author_handle"],
                content=post["content"][:5000],  # Truncate very long content
                url=post["url"],
                intent_score=intent_score,
                external_id=post["external_id"],
                project_id=project_id,
            )
            db.add(lead)
            new_count += 1

        db.commit()
        logger.info(f"Added {new_count} new leads for project {project_id}")


def run_worker():
    """Main worker loop — polls Redis queues for jobs."""
    logger.info("Worker started, listening for jobs...")

    while True:
        try:
            # BRPOP blocks until a job is available (timeout 5s)
            result = redis_client.brpop([SCRAPE_QUEUE], timeout=5)
            if result:
                queue_name, raw_data = result
                job_data = json.loads(raw_data)
                logger.info(f"Got job from {queue_name.decode()}: {job_data}")

                if queue_name.decode() == SCRAPE_QUEUE:
                    process_scrape_job(job_data)

        except redis.ConnectionError:
            logger.error("Redis connection lost, retrying in 5s...")
            import time
            time.sleep(5)
        except Exception:
            logger.exception("Error processing job")


def enqueue_scrape(project_id: str):
    """Helper to push a scrape job onto the queue."""
    redis_client.lpush(SCRAPE_QUEUE, json.dumps({"project_id": project_id}))


if __name__ == "__main__":
    run_worker()