import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    logger.remove()
    logger.add(sys.stdout, level=log_level, enqueue=True, backtrace=False, diagnose=False)
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.add(log_dir / "app.log", rotation="10 MB", retention="7 days", level=log_level)

