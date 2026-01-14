"""
logger.py
Configurable logging helper with optional Rich formatting.

This file provides:
✔ Standard logging setup for files + console
✔ Optional RichHandler for pretty colored logs
✔ Helper print_* wrappers for UI/debug consistency
"""

import logging
import sys
from typing import Optional

try:
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except Exception:
    RICH_AVAILABLE = False


def setup_logging(
    verbose: bool = False,
    use_rich: bool = True,
    log_level: Optional[int] = None,
):
    """
    Configure global logging settings.

    Args:
        verbose: Enable DEBUG logs if True, otherwise INFO level
        use_rich: enable fancy rich formatting if available
        log_level: explicit Python logging level override
    """
    level = (
        log_level
        if log_level is not None
        else (logging.DEBUG if verbose else logging.INFO)
    )

    handlers = []

    if use_rich and RICH_AVAILABLE:
        handlers.append(
            RichHandler(
                rich_tracebacks=True,
                tracebacks_show_locals=False,
                markup=True,
                log_time_format="[%X]",
            )
        )
    else:
        # Standard handler fallback
        stream = logging.StreamHandler(sys.stdout)
        handlers.append(stream)

    logging.basicConfig(
        level=level,
        handlers=handlers,
        format="%(message)s" if (use_rich and RICH_AVAILABLE) else "%(asctime)s %(levelname)s %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.debug("Logging initialized (rich=%s, verbose=%s)", use_rich and RICH_AVAILABLE, verbose)


def print_header(msg: str):
    """Top-level bold header."""
    bar = "─" * max(40, len(msg))
    logging.info(f"\n{bar}\n{msg}\n{bar}\n")


def print_success(msg: str):
    logging.info(f"✅ {msg}")


def print_error(msg: str):
    logging.error(f"❌ {msg}")


def print_warning(msg: str):
    logging.warning(f"⚠️ {msg}")
