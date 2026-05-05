"""
Sentinel-Poly | Logger
Structured, coloured console + rotating file logger.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from bot.config import LOG_LEVEL

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

RESET   = "\033[0m"
COLOURS = {
    "DEBUG":    "\033[36m",  # Cyan
    "INFO":     "\033[32m",  # Green
    "WARNING":  "\033[33m",  # Yellow
    "ERROR":    "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
}


class ColourFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        colour = COLOURS.get(record.levelname, RESET)
        record.levelname = f"{colour}{record.levelname:<8}{RESET}"
        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    # Console handler (coloured)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(
        ColourFormatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    logger.addHandler(ch)

    # File handler (rotating, 5 MB × 3 backups)
    fh = RotatingFileHandler(
        LOG_DIR / "sentinel.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(fh)

    return logger
