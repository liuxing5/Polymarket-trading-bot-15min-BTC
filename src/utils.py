"""
utils.py
Shared helper utilities for the arbitrage bot.

Includes:
✔ GracefulShutdown (CTRL+C or SIGTERM safe exit flag)
✔ retry decorator (optional for network wrapping)
"""

import signal
import functools
import time
import logging

logger = logging.getLogger(__name__)


# =========================================================
# Graceful Shutdown — used by main monitor loop
# =========================================================
class GracefulShutdown:
    """
    Sets a global shutdown flag when receiving CTRL+C or SIGTERM
    Usage:
        while not GracefulShutdown.SHUTDOWN:
            ...
    """
    SHUTDOWN = False
    _registered = False

    @classmethod
    def _set_flag(cls, *args):
        cls.SHUTDOWN = True
        logger.warning("👋 Termination requested — stopping loops...")

    @classmethod
    def ensure_registered(cls):
        """Install signal handlers only once"""
        if cls._registered:
            return
        cls._registered = True

        try:
            signal.signal(signal.SIGINT, cls._set_flag)
        except Exception:
            pass
        try:
            signal.signal(signal.SIGTERM, cls._set_flag)
        except Exception:
            pass


# Register on import
GracefulShutdown.ensure_registered()


# =========================================================
# Retry decorator (network resilience)
# =========================================================
def retry(max_attempts=3, delay=0.5, backoff=1.2):
    """
    Decorator for API calls:
    - retry on exceptions
    - exponential backoff (optional)
    Example:
        @retry(3, delay=0.2)
        def fetch():
            ...
    """
    def wrapper(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            attempts = 0
            wait = delay
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    logger.warning(f"[retry] {fn.__name__} failed: {e}; retry in {wait:.2f}s")
                    time.sleep(wait)
                    wait *= backoff
        return inner
    return wrapper
