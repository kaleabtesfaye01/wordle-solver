from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def load_word_list(filename: str) -> list[str]:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Word list not found: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def load_default_word_lists() -> tuple[list[str], list[str]]:
    allowed_words = load_word_list("wordle-allowed-guesses.txt")
    answers = load_word_list("wordle-answers-alphabetical.txt")
    return allowed_words, answers
