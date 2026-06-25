import json
import copy
from datetime import datetime, timedelta
from config import (
    PERSONALITY_DIMS, INITIAL_PERSONALITY,
    PERSONALITY_CHANGE_RATE, PERSONALITY_MAX_DAILY, DATA_DIR
)


class Personality:
    def __init__(self):
        self.dims = {name: val for name, val in zip(PERSONALITY_DIMS, INITIAL_PERSONALITY)}
        self.daily_deltas = {name: 0.0 for name in PERSONALITY_DIMS}
        self.last_date = datetime.now().date()

    def get(self, name: str) -> float:
        return self.dims.get(name, 0.5)

    def modify(self, deltas: dict):
        today = datetime.now().date()
        if today != self.last_date:
            self.daily_deltas = {name: 0.0 for name in PERSONALITY_DIMS}
            self.last_date = today

        for name, delta in deltas.items():
            if name not in self.dims:
                continue
            new_daily = self.daily_deltas[name] + abs(delta)
            if new_daily > PERSONALITY_MAX_DAILY:
                continue
            self.daily_deltas[name] = new_daily
            self.dims[name] = max(0.0, min(1.0, self.dims[name] + delta))

    def to_dict(self) -> dict:
        return {
            "dims": self.dims,
            "daily_deltas": self.daily_deltas,
            "last_date": self.last_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Personality":
        p = cls()
        p.dims = data["dims"]
        p.daily_deltas = data["daily_deltas"]
        p.last_date = datetime.fromisoformat(data["last_date"]).date()
        return p

    def save(self, path=None):
        if path is None:
            path = DATA_DIR / "personality.json"
        else:
            path = path / "personality.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path=None) -> "Personality":
        if path is None:
            path = DATA_DIR / "personality.json"
        else:
            path = path / "personality.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return cls.from_dict(json.load(f))
        return cls()
