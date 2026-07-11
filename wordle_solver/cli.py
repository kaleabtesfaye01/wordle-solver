from __future__ import annotations

import argparse
import random
from typing import Sequence

from .data import load_default_word_lists
from .session import apply_turn, create_game_session, suggest_answer

DEFAULT_MAX_GUESSES = 6


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Wordle assistant CLI")
    parser.add_argument(
        "--max-guesses",
        type=int,
        default=DEFAULT_MAX_GUESSES,
        help="Maximum guesses allowed before stopping.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for random suggestions.",
    )
    return parser


def is_valid_guess(
    guess: str, allowed_words: Sequence[str], answers: Sequence[str]
) -> bool:
    return len(guess) == 5 and (guess in allowed_words or guess in answers)


def is_valid_feedback(feedback: str) -> bool:
    return (
        len(feedback) == 5
        and all(letter in "GYR" for letter in feedback)
    )


def run_session(
    max_guesses: int = DEFAULT_MAX_GUESSES,
    rng: random.Random | None = None,
) -> int:
    allowed_words, answers = load_default_word_lists()
    session = create_game_session(
        allowed_words,
        answers,
        allowed_number_of_guesses=max_guesses,
    )

    print("Wordle assistant session started.")
    print(f"Allowed guesses: {session.allowed_number_of_guesses}")

    while session.number_of_guesses < session.allowed_number_of_guesses:
        suggested_guess = suggest_answer(session.remaining_answers, rng)
        if suggested_guess is None:
            print("No remaining answer candidates.")
            return 1

        print(f"Suggested guess: {suggested_guess}")
        guess_prompt = (
            "Enter the guess you used (press Enter to accept "
            "suggestion): "
        )
        guess = input(guess_prompt).strip().lower()
        if not guess:
            guess = suggested_guess
        if not is_valid_guess(guess, session.allowed_words, session.answers):
            print("Word not in the allowed list.")
            continue

        feedback = input("Enter Wordle feedback as G/Y/R: ").strip().upper()
        if not is_valid_feedback(feedback):
            print(
                "Signals must be a five-character string using only G, Y, and "
                "R."
            )
            continue

        apply_turn(session, guess, feedback)

        print(f"Guess: {session.guess}")
        print(f"Signals: {session.signals}")
        print(f"Remaining answers: {len(session.remaining_answers)}")
        print(f"Available letters: {session.available_letters}")

        if feedback == "GGGGG":
            print(f"Solved in {session.number_of_guesses} guesses.")
            return 0

    print("Game over.")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    rng = random.Random(args.seed) if args.seed is not None else None
    return run_session(max_guesses=args.max_guesses, rng=rng)
