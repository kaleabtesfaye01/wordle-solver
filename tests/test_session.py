from __future__ import annotations

import random

from wordle_solver import session


def test_compute_signals_green_and_yellow():
    # a few greens and yellows
    assert session.compute_signals("abcde", "abced") == "GGGYY"


def test_compute_signals_all_red():
    assert session.compute_signals("abcde", "zzzzz") == "RRRRR"


def test_filter_answers_matches_expected_secret():
    candidates = ["abcde", "abced", "zzzzz"]
    # Suppose the true secret is "abcde" and player guessed "abced"
    feedback = session.compute_signals("abcde", "abced")
    # Only candidates that would produce the same feedback remain
    remaining = session.filter_answers(candidates, "abced", feedback)
    assert remaining == ["abcde"]


def test_suggest_answer_with_rng_and_empty():
    candidates = ["one", "two", "three"]
    rng1 = random.Random(0)
    rng2 = random.Random(0)
    choice1 = session.suggest_answer(candidates, rng1)
    choice2 = session.suggest_answer(candidates, rng2)
    assert choice1 == choice2
    assert session.suggest_answer([], rng1) is None


def test_update_available_letters_removes_reds():
    letters = session.ALPHABET
    guess = "abcde"
    feedback = "RRRRR"
    updated = session.update_available_letters(letters, guess, feedback)
    for ch in "abcde":
        assert ch not in updated
