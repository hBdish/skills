"""Helpers for reading user records from a JSON export."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class User:
    id: int
    name: str


def load_users(path: Path) -> list[User]:
    """Read users from a JSON array of {"id", "name"} objects.

    Raises:
        FileNotFoundError: if the export does not exist.
        ValueError: if the file is not valid JSON.
    """
    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    users = [User(id=int(item["id"]), name=str(item["name"])) for item in raw]
    logger.info("loaded %d users from %s", len(users), path)
    return users
