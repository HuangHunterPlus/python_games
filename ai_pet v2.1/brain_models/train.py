import numpy as np
from pathlib import Path
from config import VOCAB, RNN_TRAIN_EPOCHS, RNN_LEARNING_RATE, DATA_DIR, bundled_path
from brain_models.char_rnn import CharRNN


def load_corpus(path: str | Path) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def prepare_batch(model: CharRNN, lines: list[str]):
    indices = []
    for line in lines:
        tagged = f"<start> {line} <end>"
        converted = [model.char_to_idx(c) for c in tagged if c in model.vocab]
        if len(converted) >= 5:
            indices.append(converted)
    return indices


def train(model: CharRNN = None, epochs: int = None, lr: float = None, verbose: bool = True):
    if model is None:
        model = CharRNN()
    if epochs is None:
        epochs = RNN_TRAIN_EPOCHS
    if lr is None:
        lr = RNN_LEARNING_RATE

    corpus_path = bundled_path("corpus.txt")
    if not corpus_path.exists():
        return model

    lines = load_corpus(corpus_path)
    batches = prepare_batch(model, lines)
    if verbose:
        print(f"[train] {len(batches)} sentences")

    for epoch in range(epochs):
        np.random.shuffle(batches)
        total_loss = 0.0
        decay_lr = lr * (1 - epoch / max(epochs, 1))
        for batch in batches:
            inputs = batch[:-1]
            targets = batch[1:]
            loss = model.train_step(inputs, targets, decay_lr)
            total_loss += loss * len(inputs)
        avg_loss = total_loss / sum(len(b) - 1 for b in batches)

        if verbose and ((epoch + 1) % max(1, epochs // 3) == 0 or epoch == 0):
            sample = model.sample("", length=15)
            print(f"[train] {epoch+1}/{epochs} loss={avg_loss:.2f} {sample[:20]}")

    model.save_weights(str(DATA_DIR / "weights.npz"))
    if verbose:
        print(f"[train] Done")
    return model


if __name__ == "__main__":
    train()
