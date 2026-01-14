"""
wss_market.py
Websocket client for Polymarket CLOB streaming

Features:
✔ automatic reconnect with backoff
✔ safe parsing of incremental updates
✔ maintains full bid/ask state per asset
✔ lightweight & resilient for arbitrage bot
"""

import asyncio
import json
import logging
import random
from typing import Dict, List, Tuple, Optional

import websockets

logger = logging.getLogger(__name__)


class OrderBookSide:
    """Holder for incremental bid/ask updates"""
    def __init__(self):
        self.bids: List[Tuple[float, float]] = []
        self.asks: List[Tuple[float, float]] = []

    def to_levels(self) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        return list(self.bids), list(self.asks)


class MarketWssClient:
    """
    Polymarket CLOB Market Streaming Client

    Emits:
       async for (asset_id, update_type) in client.run():
            # Use client.get_book(asset_id) to read local state
    """

    def __init__(self, ws_base_url: str, asset_ids: List[str]):
        self.ws_base_url = ws_base_url.rstrip("/")
        self.asset_ids = asset_ids
        self.order_books: Dict[str, OrderBookSide] = {a: OrderBookSide() for a in asset_ids}

        # Reconnect & throttle
        self._min_reconnect = 1.0
        self._max_reconnect = 10.0

    def get_book(self, asset_id: str) -> Optional[OrderBookSide]:
        return self.order_books.get(asset_id)

    async def _connect(self):
        url = f"{self.ws_base_url}/ws"
        logger.info(f"[WSS] Connecting to {url} ...")
        return await websockets.connect(url, ping_interval=20, ping_timeout=20)

    async def run(self):
        """
        Runs forever until caller cancels.
        On every message: yields (asset_id, event_type)
        """
        backoff = self._min_reconnect

        while True:
            try:
                async with await self._connect() as ws:
                    # subscribe once per connection
                    await ws.send(json.dumps({"type": "subscribe", "assetIds": self.asset_ids}))
                    logger.info(f"[WSS] Subscribed to {len(self.asset_ids)} assets")

                    backoff = self._min_reconnect  # reset on success

                    async for msg in ws:
                        try:
                            data = json.loads(msg)
                        except Exception:
                            continue

                        if data.get("type") != "orderbookUpdate":
                            continue

                        asset_id = data.get("assetId")
                        if not asset_id or asset_id not in self.order_books:
                            continue

                        book = self.order_books[asset_id]

                        # Update local cache
                        bids = data.get("bids")
                        asks = data.get("asks")
                        if bids is not None:
                            try:
                                book.bids = [(float(p), float(s)) for p, s in bids if float(s) > 0]
                            except Exception:
                                pass
                        if asks is not None:
                            try:
                                book.asks = [(float(p), float(s)) for p, s in asks if float(s) > 0]
                            except Exception:
                                pass

                        yield asset_id, "book"

            except (asyncio.CancelledError, KeyboardInterrupt):
                logger.info("[WSS] Cancelled; exiting")
                return
            except Exception as e:
                logger.warning(f"[WSS] Error: {e}; reconnecting in {backoff:.1f}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 1.5 + random.uniform(0, 1), self._max_reconnect)
