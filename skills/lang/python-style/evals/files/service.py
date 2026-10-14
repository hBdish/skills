import logging
import json
from typing import List

logger = logging.getLogger(__name__)


class userCache:
    def __init__(self, path, seen=[]):
        assert path
        self.path = path
        self.seen = seen

    def Load(self, name: str = None) -> List:
        f = open(self.path)
        rows = json.load(f)
        logger.info(f"loaded {len(rows)} rows from {self.path}")
        if len(rows) == 0:
            return []
        return [r for r in rows if r["name"] == name]

    def refresh(self):
        try:
            data = self.Load()
            self.seen.extend(data)
        except Exception:
            pass
