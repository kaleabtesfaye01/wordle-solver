from __future__ import annotations

from wordle_solver import session
from wordle_solver.streamlit_app import (
    build_board_rows,
    current_status,
    tile_class,
    validate_turn_inputs,
)


def test_current_status_reports_solved_first():
    game = session.create_game_session(["abcde"], ["abcde"])
    game.number_of_guesses = 2
    game.signals = "GGGGG"
    game.remaining_answers = []

    assert current_status(game) == "solved"


def test_current_status_reports_stalled_when_candidates_run_out():
    game = session.create_game_session(["abcde"], ["abcde"])
    game.remaining_answers = []

    assert current_status(game) == "stalled"


def test_tile_class_maps_feedback_letters():
    assert tile_class("G") == "wordle-tile-green"
    assert tile_class("Y") == "wordle-tile-yellow"
    assert tile_class("R") == "wordle-tile-gray"


def test_build_board_rows_pads_history_to_max_guesses():
    rows = build_board_rows(
        [{"guess": "abcde", "feedback": "gyrrr"}],
        3,
    )

    assert rows == [("ABCDE", "GYRRR"), ("", ""), ("", "")]


def test_validate_turn_inputs_accepts_blank_guess_when_suggestion_exists():
    game = session.create_game_session(["abcde"], ["abcde"])

    assert validate_turn_inputs(game, "", "gyrrr", "abcde") == (
        "abcde",
        "GYRRR",
    )


def test_validate_turn_inputs_returns_clear_error_for_invalid_feedback():
    game = session.create_game_session(["abcde"], ["abcde"])

    assert (
        validate_turn_inputs(game, "abcde", "xxxxx", None)
        == "Feedback must be a five-character string using only G, Y, and R."
    )
