import json
import random
import numpy as np
from config import (
    ACTIONS, LEARNING_RATE, DISCOUNT_FACTOR,
    EXPLORATION_RATE, EXPLORATION_DECAY, MIN_EXPLORATION, DATA_DIR
)


def discretize(value: float, levels: int = 3) -> int:
    return min(levels - 1, max(0, int(value * levels / 100)))


class BehaviorEngine:
    def __init__(self, personality=None):
        self.q_table: dict[tuple, dict[str, float]] = {}
        self.exploration_rate = EXPLORATION_RATE
        self.personality = personality

    def _state_key(self, hunger: float, energy: float, mood: float, health: float, hour: int) -> tuple:
        period = 0 if hour < 8 else 1 if hour < 18 else 2
        return (
            discretize(hunger),
            discretize(energy),
            discretize(mood),
            discretize(health),
            period,
        )

    def _get_q_values(self, state: tuple) -> dict[str, float]:
        if state not in self.q_table:
            self.q_table[state] = {a: random.uniform(0, 0.1) for a in ACTIONS}
        return self.q_table[state]

    def choose_action(self, hunger: float, energy: float, mood: float, health: float, hour: int) -> str:
        state = self._state_key(hunger, energy, mood, health, hour)
        q_vals = self._get_q_values(state)

        if random.random() < self.exploration_rate:
            return random.choice(ACTIONS)

        return max(q_vals, key=q_vals.get)

    def get_reward(self, action: str, hunger: float, energy: float, mood: float, health: float) -> float:
        reward = 0.0
        personality = self.personality

        if action == "eat":
            reward += 1.0 if hunger > 50 else -0.5
            if personality:
                reward += personality.get("affectionate") * 0.2
        elif action == "play":
            reward += 1.0 if energy > 40 else -1.0
            reward += 0.5 if mood < 50 else 0.2
            if personality:
                reward += personality.get("energetic") * 0.5
                reward += personality.get("curious") * 0.3
        elif action == "sleep":
            reward += 1.0 if energy < 40 else -0.3
            if personality:
                reward -= personality.get("energetic") * 0.3
        elif action == "cuddle":
            reward += 0.5 if mood < 60 else 0.2
            if personality:
                reward += personality.get("affectionate") * 0.5
                reward += personality.get("clingy") * 0.3
        elif action == "explore":
            reward += 0.5 if energy > 50 else -0.5
            if personality:
                reward += personality.get("curious") * 0.6
        elif action == "wander":
            reward += 0.2
            if personality:
                reward += personality.get("curious") * 0.2
                reward += personality.get("energetic") * 0.1
        elif action == "groom":
            reward += 0.3 if health < 50 else 0.1
            if personality:
                reward += personality.get("stubborn") * -0.1

        return reward

    def update(self, hunger: float, energy: float, mood: float, health: float,
               hour: int, action: str, reward: float, next_hunger: float,
               next_energy: float, next_mood: float, next_health: float, next_hour: int):
        state = self._state_key(hunger, energy, mood, health, hour)
        next_state = self._state_key(next_hunger, next_energy, next_mood, next_health, next_hour)

        q_vals = self._get_q_values(state)
        next_q_vals = self._get_q_values(next_state)

        current_q = q_vals[action]
        max_next_q = max(next_q_vals.values())
        new_q = current_q + LEARNING_RATE * (reward + DISCOUNT_FACTOR * max_next_q - current_q)
        q_vals[action] = new_q

        self.exploration_rate = max(MIN_EXPLORATION, self.exploration_rate * EXPLORATION_DECAY)

    def to_dict(self) -> dict:
        serializable = {}
        for state, actions in self.q_table.items():
            key = ",".join(str(s) for s in state)
            serializable[key] = actions
        return {"q_table": serializable, "exploration_rate": self.exploration_rate}

    @classmethod
    def from_dict(cls, data: dict, personality=None) -> "BehaviorEngine":
        b = cls(personality=personality)
        b.exploration_rate = data.get("exploration_rate", EXPLORATION_RATE)
        for key, actions in data.get("q_table", {}).items():
            state = tuple(int(s) for s in key.split(","))
            b.q_table[state] = actions
        return b

    def save(self, path=None):
        if path is None:
            path = DATA_DIR / "q_table.json"
        else:
            path = path / "q_table.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, personality=None, path=None) -> "BehaviorEngine":
        if path is None:
            path = DATA_DIR / "q_table.json"
        else:
            path = path / "q_table.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return cls.from_dict(json.load(f), personality=personality)
        return cls(personality=personality)
