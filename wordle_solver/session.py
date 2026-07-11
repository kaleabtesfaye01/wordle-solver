from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Sequence

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


@dataclass
class GameSession:
    allowed_words: list[str]
    answers: list[str]
    remaining_answers: list[str] = field(default_factory=list)
    available_letters: str = ALPHABET
    guess: str = ""
    signals: str = ""
    number_of_guesses: int = 0
    allowed_number_of_guesses: int = 6


def create_game_session(
    allowed_words: list[str],
    answers: list[str],
    allowed_number_of_guesses: int = 6,
) -> GameSession:
    return GameSession(
        allowed_words=allowed_words,
        answers=answers,
        remaining_answers=answers.copy(),
        allowed_number_of_guesses=allowed_number_of_guesses,
    )


def compute_signals(secret_word: str, guess_word: str) -> str:
    secret_letters = list(secret_word)
    signals = ["R"] * len(guess_word)

    for index, letter in enumerate(guess_word):
        if letter == secret_letters[index]:
            signals[index] = "G"
            secret_letters[index] = None

    for index, letter in enumerate(guess_word):
        if signals[index] == "G":
            continue
        if letter in secret_letters:
            signals[index] = "Y"
            secret_letters[secret_letters.index(letter)] = None

    return "".join(signals)


def filter_answers(
    candidates: Sequence[str],
    guess_word: str,
    feedback: str,
) -> list[str]:
    return [
        candidate
        for candidate in candidates
        if compute_signals(candidate, guess_word) == feedback
    ]


def suggest_answer(
    candidates: Sequence[str],
    rng: random.Random | None = None,
) -> str | None:
    if not candidates:
        return None
    # Use provided RNG for deterministic behavior; otherwise fall back
    # to the module-level random.choice implementation.
    if rng is None:
        return random.choice(list(candidates))
    return rng.choice(list(candidates))


def update_available_letters(
    current_letters: str,
    guess_word: str,
    feedback: str,
) -> str:
    red_letters = {
        guess_word[index]
        for index, signal in enumerate(feedback)
        if signal == "R"
    }

    return "".join(
        [
            letter
            for letter in current_letters
            if letter not in red_letters
        ]
    )


def apply_turn(
    session: GameSession,
    guess_word: str,
    feedback: str,
) -> GameSession:
    session.number_of_guesses += 1
    session.guess = guess_word
    session.signals = feedback
    session.remaining_answers = filter_answers(
        session.remaining_answers, guess_word, feedback
    )
    session.available_letters = update_available_letters(
        session.available_letters, guess_word, feedback
    )
    return session
