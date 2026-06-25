import json
import time
from config import MEMORY_HALF_LIFE_DAYS, MEMORY_CLEAN_THRESHOLD, MEMORY_MIN_COUNT, DATA_DIR


class Memory:
    def __init__(self):
        self.store: dict[str, dict] = {}

    def remember(self, key: str, value=None):
        now = time.time()
        if key in self.store:
            self.store[key]["count"] += 1
            self.store[key]["time"] = now
            if value is not None:
                self.store[key]["value"] = value
        else:
            self.store[key] = {"time": now, "value": value, "count": 1}

    def recall(self, key: str):
        entry = self.store.get(key)
        if entry is None:
            return None
        weight = self._weight(entry["time"])
        if weight < MEMORY_CLEAN_THRESHOLD and entry["count"] < MEMORY_MIN_COUNT:
            del self.store[key]
            return None
        return entry["value"] if weight > MEMORY_CLEAN_THRESHOLD else None

    def _weight(self, timestamp: float) -> float:
        days = (time.time() - timestamp) / 86400
        return 2.0 ** (-days / MEMORY_HALF_LIFE_DAYS)

    def recent_memories(self, limit: int = 5) -> list[tuple[str, str, float]]:
        items = []
        for key, entry in self.store.items():
            w = self._weight(entry["time"])
            if w > MEMORY_CLEAN_THRESHOLD:
                items.append((key, entry.get("value"), w))
        items.sort(key=lambda x: x[2], reverse=True)
        return items[:limit]

    def cleanup(self):
        to_delete = []
        for key, entry in self.store.items():
            if self._weight(entry["time"]) < MEMORY_CLEAN_THRESHOLD and entry["count"] < MEMORY_MIN_COUNT:
                to_delete.append(key)
        for key in to_delete:
            del self.store[key]

    def to_dict(self) -> dict:
        return self.store

    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        m = cls()
        m.store = data
        return m

    def save(self, path=None):
        if path is None:
            path = DATA_DIR / "memory.json"
        else:
            path = path / "memory.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path=None) -> "Memory":
        if path is None:
            path = DATA_DIR / "memory.json"
        else:
            path = path / "memory.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return cls.from_dict(json.load(f))
        return cls()
