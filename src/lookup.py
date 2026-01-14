"""
lookup.py
Auto-market discovery with keyword matching & retry loop
"""

import time
import logging
import httpx

logger = logging.getLogger(__name__)

CLOB_MARKETS_URL = "https://clob.polymarket.com/markets"


def fetch_all_markets() -> list:
    """Fetch all markets from CLOB; return [] if error."""
    try:
        resp = httpx.get(CLOB_MARKETS_URL, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        return []


def find_market_by_keyword(keyword: str):
    """
    Match market on keyword:
    - Accepts list of strings or dicts
    - Only binary markets returned
    - Keyword matched in question
    """
    keyword = (keyword or "").lower()

    markets = fetch_all_markets()
    if not markets:
        return None

    matches = []

    for m in markets:
        # m 可能是字符串 slug，也可能是字典
        if isinstance(m, dict):
            q = str(m.get("question", "")).lower()
            tokens = m.get("tokens", [])
            slug = m.get("slug")
        else:
            # m 是字符串 slug
            q = m.lower()
            tokens = []   # 没有 token 信息，自动填空
            slug = m

        if keyword in q:
            matches.append({"slug": slug, "question": q, "tokens": tokens})

    if not matches:
        return None

    # pick the first
    return matches[0]



def auto_wait_market(keyword: str, retry_seconds=30, max_wait=None):
    """
    Keep checking until we find a matching Yes/No market.
    - retry_seconds: wait time between attempts
    - max_wait: None = infinite
    """
    start = time.time()

    while True:
        mkt = find_market_by_keyword(keyword)
        if mkt:
            logger.info(f"🎯 Found target market: {mkt.get('question')}")
            return mkt

        logger.warning(f"⏳ No market found for keyword '{keyword}' – retrying in {retry_seconds}s")

        if max_wait and (time.time() - start) > max_wait:
            raise TimeoutError(f"❌ No market found for '{keyword}' within max wait time")

        time.sleep(retry_seconds)
