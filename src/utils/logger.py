import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Safer rotating handler for threaded & multiprocessed environments
from concurrent_log_handler import ConcurrentRotatingFileHandler
# For optional structured (JSON) logs
try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False

load_dotenv()

def setup_logger(
    name: str = None,
    log_file: str = None,
    log_level: str = None,
    max_bytes: int = None,
    backup_count: int = None,
    use_json: bool = None,
):
    """
    Returns a logger configured with:
      - Dynamic log level via LOG_LEVEL
      - Console output
      - ConcurrentRotatingFileHandler for safety
      - Optional JSON formatting via JSON_LOGS
      - Configurable rotation size & backups via env
    """

    # —— Configuration from environment with sensible defaults ——
    name        = name        or os.getenv("APP_NAME", __name__)
    log_file    = log_file    or os.getenv("LOG_FILE", "app.log")
    log_level   = (log_level  or os.getenv("LOG_LEVEL", "INFO")).upper()
    max_bytes   = max_bytes   or int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10 MB
    backup_count= backup_count or int(os.getenv("LOG_BACKUP_COUNT", 5))
    use_json    = use_json    if use_json is not None else os.getenv("JSON_LOGS", "false").lower() == "true"

    # —— Build paths ——
    project_root = Path(__file__).resolve().parent.parent.parent
    log_path     = project_root / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # —— Create or retrieve logger ——
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Avoid duplicate handlers if re‑calling setup
    if logger.hasHandlers():
        logger.handlers.clear()

    # —— Formatter(s) ——
    if use_json and HAS_JSON_LOGGER:
        fmt = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s'
        )
    else:
        fmt = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )

    # —— Console Handler ——
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(getattr(logging, os.getenv("CONSOLE_LOG_LEVEL", log_level), logging.INFO))
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # —— File Handler ——
    fh = ConcurrentRotatingFileHandler(
        filename=str(log_path),
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    fh.setLevel(getattr(logging, os.getenv("FILE_LOG_LEVEL", "DEBUG"), logging.DEBUG))
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

# Single, shared logger instance
configured_logger = setup_logger()
