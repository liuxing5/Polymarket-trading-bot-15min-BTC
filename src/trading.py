"""
trading.py
Utility functions wrapping Polymarket trading endpoints
Used by the arbitrage bot
"""

import time
from typing import Any, List, Dict

import httpx

import logging
from .utils import retry
from .config import load_settings

logger = logging.getLogger(__name__)


def get_client(settings=None):
    """Return an initialized HTTPX client with API key auth."""
    if settings is None:
        settings = load_settings()

    headers = {
        "X-API-Key": settings.api_key,
        "Content-Type": "application/json",
    }

    return httpx.Client(
        headers={
            "X-API-Key": settings.api_key,
            "X-API-Secret": settings.api_secret,
            "X-API-Passphrase": settings.api_passphrase,
        },
        base_url="https://clob.polymarket.com",
        timeout=10,
    )


def extract_order_id(resp: Dict[str, Any]) -> str:
    """Safely pull order_id from any polymarket order response shape."""
    if isinstance(resp, dict):
        return resp.get("order_id") or resp.get("id") or ""
    return ""


def place_order(settings, side: str, token_id: str, price: float, size: float, tif="GTC"):
    """
    Place a single order
    """
    client = get_client(settings)
    payload = {
        "side": side.upper(),
        "token_id": token_id,
        "price": float(price),
        "size": float(size),
        "time_in_force": tif,
    }
    return client.post("/orders", json=payload).json()


def place_orders_fast(settings, orders: List[Dict[str, Any]], order_type="GTC"):
    """
    Place 2+ orders in parallel using a bulk endpoint (if supported)
    else fallback to sequential submission.
    """
    client = get_client(settings)

    payloads = []
    for o in orders:
        payloads.append({
            "side": o["side"].upper(),
            "token_id": o["token_id"],
            "price": float(o["price"]),
            "size": float(o["size"]),
            "time_in_force": order_type,
        })

    try:
        resp = client.post("/orders/bulk", json={"orders": payloads})
        if resp.is_success:
            return resp.json()
        else:
            logger.warning("Bulk order failed, falling back to sequential.")
    except Exception:
        logger.warning("Bulk order unavailable, falling back to sequential.")

    # Fallback single submit
    out = []
    for o in payloads:
        out.append(client.post("/orders", json=o).json())
    return out


def wait_for_terminal_order(settings, order_id: str, requested_size: float, poll_delay=0.5, timeout=15):
    """
    Poll order status until:
    ✔ filled
    ✔ canceled/rejected
    ✔ timeout reached
    """
    client = get_client(settings)

    start = time.time()
    last_seen = None

    while time.time() - start < timeout:
        try:
            res = client.get(f"/orders/{order_id}").json()
            last_seen = res

            filled = float(res.get("filled_size", 0.0))
            status = res.get("status", "").lower()

            if filled >= requested_size:
                return res

            if status in ("canceled", "rejected", "expired"):
                return res

        except Exception as e:
            logger.error(f"[wait_for_terminal] {e}")

        time.sleep(poll_delay)

    return last_seen or {"status": "timeout", "filled_size": 0.0}


def cancel_orders(settings, order_ids: List[str]):
    client = get_client(settings)
    for oid in order_ids:
        try:
            client.post(f"/orders/{oid}/cancel")
        except Exception as e:
            logger.error(f"[cancel_orders] {e}")


def get_positions(settings):
    client = get_client(settings)
    try:
        return client.get("/positions").json()
    except Exception as e:
        logger.error(f"[get_positions] {e}")
        return []


# ===================================================================
#                 AUTO REDEEM SECTION
# ===================================================================

def has_redeemable(settings) -> bool:
    """
    Scan positions and see if any have redeemable=true
    Returns True/False
    """
    client = get_client(settings)
    try:
        res = client.get("/positions").json()
    except Exception:
        return False

    for pos in res:
        if pos.get("redeemable", False):
            return True
    return False


def redeem_all(settings):
    """
    Triggers redemption of all redeemable shares into USDC.
    Uses Polymarket '/positions/redeem-all' endpoint.
    """
    client = get_client(settings)

    try:
        resp = client.post("/positions/redeem-all", json={})
        if resp.is_success:
            try:
                return resp.json()
            except Exception:
                return {"status": "ok"}
        else:
            return {"error": f"HTTP {resp.status_code}", "body": resp.text}

    except Exception as e:
        logger.error(f"[redeem_all] {e}")
        return {"error": str(e)}
