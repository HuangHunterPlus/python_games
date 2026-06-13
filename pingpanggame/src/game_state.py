"""
Game state machine — state flow, scoring, serve rotation
"""

import random
from enum import Enum, auto
from src.config import WIN_SCORE, COUNTDOWN_SECONDS, SCORE_PAUSE_SECONDS


class State(Enum):
    TITLE = auto()
    COUNTDOWN = auto()
    PLAYING = auto()
    SCORED = auto()
    GAME_OVER = auto()


class GameState:
    """Game state machine."""

    def __init__(self):
        self.current: State = State.TITLE
        self.timer: float = 0.0
        self.countdown_num: int = 3
        self.scores: list[int] = [0, 0]
        self.server: int = random.choice([1, 2])
        self.last_scorer: int | None = None
        self.winner: int | None = None
        self.rally_count: int = 0
        self.total_hits: int = 0

    def transition(self, new_state: State) -> None:
        self.current = new_state
        self.timer = 0.0

        if new_state == State.COUNTDOWN:
            self.countdown_num = 3
        elif new_state == State.PLAYING:
            self.countdown_num = 0
        elif new_state == State.GAME_OVER:
            self.winner = 1 if self.scores[0] > self.scores[1] else 2

    def update(self, dt: float) -> None:
        self.timer += dt

        if self.current == State.COUNTDOWN:
            remain = COUNTDOWN_SECONDS - self.timer
            if remain > 0:
                self.countdown_num = int(remain) + 1
            else:
                self.transition(State.PLAYING)

        elif self.current == State.SCORED:
            if self.timer >= SCORE_PAUSE_SECONDS:
                if self._check_winner():
                    self.transition(State.GAME_OVER)
                else:
                    self._update_server()
                    self.transition(State.COUNTDOWN)

    def add_score(self, player: int) -> None:
        idx = player - 1
        self.scores[idx] += 1
        self.last_scorer = player
        self.rally_count = 0

        if self._check_winner():
            self.transition(State.GAME_OVER)
        else:
            self.transition(State.SCORED)

    def _check_winner(self) -> bool:
        """
        Table tennis rules:
        - First to 11 with at least a 2-point lead wins
        - At 10:10, must win by 2
        """
        p1, p2 = self.scores
        if p1 >= WIN_SCORE or p2 >= WIN_SCORE:
            if abs(p1 - p2) >= 2:
                self.winner = 1 if p1 > p2 else 2
                return True
        return False

    def _update_server(self) -> None:
        """Rotate serve every 2 points; at 10:10+, rotate every point."""
        total = sum(self.scores)
        p1, p2 = self.scores
        if p1 >= (WIN_SCORE - 1) and p2 >= (WIN_SCORE - 1):
            self.server = 3 - self.server
        elif total > 0 and total % 2 == 0:
            self.server = 3 - self.server

    def reset(self) -> None:
        self.__init__()
        self.transition(State.TITLE)

    def is_playing(self) -> bool:
        return self.current == State.PLAYING
