"""
Structured logging configuration for the CUIA platform.

Provides a consistent logging format across all modules.
All log entries include timestamp, module name, and log level.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured logging for the entire CUIA application.
    Call once at startup.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-25s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Configure root logger for cuia namespace
    root_logger = logging.getLogger("cuia")
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)
    root_logger.propagate = False
    
    # Also configure uvicorn access log to use same format
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(handler)
