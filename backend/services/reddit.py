import httpx
import logging
from urllib.parse import quote

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

REDDIT_SEARCH_URL = "https://oauth.reddit.com/search.json"
REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"


async def _get_reddit_token(client: httpx.AsyncClient) -> str:
    """Get OAuth2 token using client credentials."""
    response = await client.post(
        REDDIT_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET),
        headers={"User-Agent": settings.REDDIT_USER_AGENT},
    )
    response.raise_for_status()
    return response.json()["access_token"]


async def fetch_reddit(
    keywords: list[str],
    subreddits: list[str] | None = None,
    limit: int = 25,
) -> list[dict]:
    """Fetch Reddit posts matching keywords, optionally scoped to subreddits."""
    query = " OR ".join(keywords)

    if subreddits:
        subreddit_filter = " OR ".join(f"subreddit:{s}" for s in subreddits)
        query = f"({query}) ({subreddit_filter})"

    safe_query = quote(query)
    posts = []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Use OAuth if credentials are available, else fall back to public API
            if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
                token = await _get_reddit_token(client)
                headers = {
                    "Authorization": f"Bearer {token}",
                    "User-Agent": settings.REDDIT_USER_AGENT,
                }
                url = REDDIT_SEARCH_URL
            else:
                headers = {"User-Agent": settings.REDDIT_USER_AGENT}
                url = "https://www.reddit.com/search.json"

            response = await client.get(
                url,
                params={"q": query, "limit": min(limit, 100), "sort": "new", "t": "week"},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                posts.append({
                    "platform": "reddit",
                    "author_handle": post.get("author", "[deleted]"),
                    "content": f"{post.get('title', '')} {post.get('selftext', '')}".strip(),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "external_id": post.get("id", ""),
                    "subreddit": post.get("subreddit", ""),
                })

    except httpx.HTTPStatusError as e:
        logger.error(f"Reddit API error: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"Reddit connection error: {e}")

    return posts
