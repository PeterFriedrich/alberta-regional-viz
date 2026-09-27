"""Structured (JSON-lines) logging shared by the src/ pipeline steps."""
import json
import logging
import sys


class _JsonFormatter(logging.Formatter):
    def format(self, record):
        out = {"level": record.levelname, "step": record.name, "msg": record.getMessage()}
        out.update(getattr(record, "fields", {}))
        return json.dumps(out, default=str)


def get_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)
    if not log.handlers:
        h = logging.StreamHandler(sys.stderr)
        h.setFormatter(_JsonFormatter())
        log.addHandler(h)
        log.setLevel(logging.INFO)
        log.propagate = False
    return log


def event(log: logging.Logger, msg: str, level: int = logging.INFO, **fields):
    log.log(level, msg, extra={"fields": fields})
