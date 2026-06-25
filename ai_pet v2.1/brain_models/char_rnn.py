import numpy as np
from config import VOCAB, VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM, RNN_TEMPERATURE


class CharRNN:
    def __init__(self):
        self.vocab = VOCAB
        self.vocab_size = VOCAB_SIZE
        self.embed_dim = EMBED_DIM
        self.hidden_dim = HIDDEN_DIM

        scale = 0.01
        self.W_embed = np.random.randn(self.vocab_size, self.embed_dim) * scale
        self.W_xh = np.random.randn(self.embed_dim, self.hidden_dim) * scale
        self.W_hh = np.random.randn(self.hidden_dim, self.hidden_dim) * scale
        self.b_h = np.zeros((1, self.hidden_dim))
        self.W_hy = np.random.randn(self.hidden_dim, self.vocab_size) * scale
        self.b_y = np.zeros((1, self.vocab_size))

        self._char_to_idx = {c: i for i, c in enumerate(self.vocab)}
        self._idx_to_char = {i: c for c, i in self._char_to_idx.items()}

    def char_to_idx(self, c: str) -> int:
        return self._char_to_idx.get(c, 0)

    def idx_to_char(self, i: int) -> str:
        return self._idx_to_char.get(i, " ")

    def forward(self, inputs: list[int], h_prev: np.ndarray | None = None):
        if h_prev is None:
            h_prev = np.zeros((1, self.hidden_dim))
        T = len(inputs)
        xs = np.zeros((T, self.embed_dim))
        hs = np.zeros((T + 1, self.hidden_dim))
        hs[0] = h_prev
        for t in range(T):
            xs[t] = self.W_embed[inputs[t]]
            hs[t + 1] = np.tanh(xs[t] @ self.W_xh + hs[t] @ self.W_hh + self.b_h)
        ys = hs[1:] @ self.W_hy + self.b_y
        return xs, hs, ys

    def sample(self, seed: str, length: int = 30, temperature: float = None) -> str:
        if temperature is None:
            temperature = RNN_TEMPERATURE
        h = np.zeros((1, self.hidden_dim))
        seed_indices = [self.char_to_idx(c) for c in seed if c in self.vocab]
        if not seed_indices:
            seed_indices = [self.char_to_idx(" ")]

        for idx in seed_indices:
            emb = self.W_embed[idx].reshape(1, -1)
            h = np.tanh(emb @ self.W_xh + h @ self.W_hh + self.b_h)

        result = seed
        for _ in range(length):
            emb = self.W_embed[seed_indices[-1]].reshape(1, -1)
            h = np.tanh(emb @ self.W_xh + h @ self.W_hh + self.b_h)
            y = (h @ self.W_hy + self.b_y).reshape(-1) / temperature
            exp_y = np.exp(y - np.max(y))
            probs = exp_y / np.sum(exp_y)
            next_idx = np.random.choice(self.vocab_size, p=probs)
            next_char = self.idx_to_char(next_idx)
            if next_char == "\n":
                break
            result += next_char
            seed_indices.append(next_idx)
        return result

    def train_step(self, inputs: list[int], targets: list[int], lr: float) -> float:
        T = len(inputs)
        xs = np.zeros((T, self.embed_dim))
        hs = np.zeros((T + 1, self.hidden_dim))

        h_prev = np.zeros((1, self.hidden_dim))
        hs[0] = h_prev
        for t in range(T):
            xs[t] = self.W_embed[inputs[t]]
            hs[t + 1] = np.tanh(xs[t] @ self.W_xh + hs[t] @ self.W_hh + self.b_h)

        ys = hs[1:] @ self.W_hy + self.b_y
        probs = np.exp(ys - np.max(ys, axis=1, keepdims=True))
        probs /= np.sum(probs, axis=1, keepdims=True)

        loss = -np.sum(np.log(probs[np.arange(T), targets] + 1e-8)) / T

        dW_hy = np.zeros_like(self.W_hy)
        db_y = np.zeros_like(self.b_y)
        dW_hh = np.zeros_like(self.W_hh)
        dW_xh = np.zeros_like(self.W_xh)
        db_h = np.zeros_like(self.b_h)
        dW_embed = np.zeros_like(self.W_embed)
        dh_next = np.zeros((1, self.hidden_dim))

        for t in reversed(range(T)):
            dy = probs[t:t+1].copy()
            dy[0, targets[t]] -= 1
            ht_2d = hs[t+1:t+2]
            h_2d = hs[t:t+1]
            dW_hy += ht_2d.T @ dy
            db_y += dy
            dh = dy @ self.W_hy.T + dh_next
            dh_raw = (1 - ht_2d ** 2) * dh
            db_h += dh_raw
            dW_hh += h_2d.T @ dh_raw
            dW_xh += xs[t:t+1].T @ dh_raw
            dW_embed[inputs[t]] += (dh_raw @ self.W_xh.T).reshape(-1)
            dh_next = dh_raw @ self.W_hh.T

        for param, grad in [("W_embed", dW_embed), ("W_xh", dW_xh), ("W_hh", dW_hh),
                            ("b_h", db_h), ("W_hy", dW_hy), ("b_y", db_y)]:
            np.clip(grad, -5, 5, out=grad)
            setattr(self, param, getattr(self, param) - lr * grad)

        return loss

    def save_weights(self, path: str):
        np.savez_compressed(path,
            W_embed=self.W_embed, W_xh=self.W_xh, W_hh=self.W_hh,
            b_h=self.b_h, W_hy=self.W_hy, b_y=self.b_y)

    def load_weights(self, path: str):
        data = np.load(path)
        self.W_embed = data["W_embed"]
        self.W_xh = data["W_xh"]
        self.W_hh = data["W_hh"]
        self.b_h = data["b_h"]
        self.W_hy = data["W_hy"]
        self.b_y = data["b_y"]
