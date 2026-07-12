from __future__ import annotations

import random
from pathlib import Path
from typing import Literal

import subprocess
import sys

import streamlit as st

try:
    from .cli import is_valid_feedback, is_valid_guess
    from .data import load_default_word_lists
    from .session import GameSession, apply_turn, create_game_session, suggest_answer
except ImportError:
    from wordle_solver.cli import is_valid_feedback, is_valid_guess
    from wordle_solver.data import load_default_word_lists
    from wordle_solver.session import (
        GameSession,
        apply_turn,
        create_game_session,
        suggest_answer,
    )

APP_TITLE = "Wordle Solver"
DEFAULT_MAX_GUESSES = 6

SESSION_KEY = "wordle_game_session"
HISTORY_KEY = "wordle_turn_history"
SUGGESTION_KEY = "wordle_current_suggestion"
RNG_KEY = "wordle_rng"
MAX_GUESSES_KEY = "wordle_max_guesses"

Status = Literal["playing", "solved", "exhausted", "stalled"]


@st.cache_data(show_spinner=False)
def load_word_lists() -> tuple[list[str], list[str]]:
    return load_default_word_lists()


def reset_game(max_guesses: int) -> None:
    allowed_words, answers = load_word_lists()
    session = create_game_session(
        allowed_words,
        answers,
        allowed_number_of_guesses=max_guesses,
    )
    st.session_state[SESSION_KEY] = session
    st.session_state[HISTORY_KEY] = []
    st.session_state[RNG_KEY] = random.Random()
    st.session_state[MAX_GUESSES_KEY] = max_guesses
    st.session_state[SUGGESTION_KEY] = suggest_answer(
        session.remaining_answers,
        st.session_state[RNG_KEY],
    )


def ensure_game(max_guesses: int) -> GameSession:
    if SESSION_KEY not in st.session_state:
        reset_game(max_guesses)
    elif st.session_state.get(MAX_GUESSES_KEY) != max_guesses:
        reset_game(max_guesses)
    return st.session_state[SESSION_KEY]


def current_status(session: GameSession) -> Status:
    if session.signals == "GGGGG":
        return "solved"
    if session.number_of_guesses >= session.allowed_number_of_guesses:
        return "exhausted"
    if not session.remaining_answers:
        return "stalled"
    return "playing"


def build_board_rows(
    history: list[dict[str, str]],
    max_guesses: int,
) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [
        (turn["guess"].upper(), turn["feedback"].upper()) for turn in history
    ]
    while len(rows) < max_guesses:
        rows.append(("", ""))
    return rows


def validate_turn_inputs(
    session: GameSession,
    guess: str,
    feedback: str,
    suggestion: str | None,
) -> tuple[str, str] | str:
    normalized_guess = guess.strip().lower() or (suggestion or "")
    normalized_feedback = feedback.strip().upper()

    if not normalized_guess:
        return "Enter a guess or wait for a suggestion to load."
    if not is_valid_guess(normalized_guess, session.allowed_words, session.answers):
        return "Word not in the allowed list."
    if not is_valid_feedback(normalized_feedback):
        return "Feedback must be a five-character string using only G, Y, and R."

    return normalized_guess, normalized_feedback


def refresh_suggestion() -> None:
    session = st.session_state[SESSION_KEY]
    st.session_state[SUGGESTION_KEY] = suggest_answer(
        session.remaining_answers,
        st.session_state[RNG_KEY],
    )


def tile_class(signal: str) -> str:
    return {
        "G": "wordle-tile-green",
        "Y": "wordle-tile-yellow",
        "R": "wordle-tile-gray",
    }[signal]


def inject_wordle_styles() -> None:
    st.markdown(
        """
        <style>
        .wordle-root {
            max-width: 420px;
            margin: 0 auto;
        }
        .wordle-board {
            display: grid;
            grid-template-rows: repeat(6, 1fr);
            gap: 6px;
            margin: 0 auto 16px auto;
        }
        .wordle-row {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 6px;
        }
        .wordle-tile {
            width: 62px;
            height: 62px;
            border: 2px solid #d3d6da;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 2rem;
            text-transform: uppercase;
            color: #1a1a1b;
            box-sizing: border-box;
        }
        .wordle-tile-empty {
            background: #ffffff;
        }
        .wordle-tile-green {
            background: #6aaa64;
            border-color: #6aaa64;
            color: #ffffff;
        }
        .wordle-tile-yellow {
            background: #c9b458;
            border-color: #c9b458;
            color: #ffffff;
        }
        .wordle-tile-gray {
            background: #787c7e;
            border-color: #787c7e;
            color: #ffffff;
        }
        @media (max-width: 640px) {
            .wordle-tile {
                width: 54px;
                height: 54px;
                font-size: 1.75rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_board() -> None:
    history = st.session_state[HISTORY_KEY]
    max_guesses = st.session_state[MAX_GUESSES_KEY]
    rows = build_board_rows(history, max_guesses)

    board_html = ["<div class='wordle-root'><div class='wordle-board'>"]
    for guess, feedback in rows:
        board_html.append("<div class='wordle-row'>")
        for index in range(5):
            letter = guess[index] if index < len(guess) else ""
            signal = feedback[index] if index < len(feedback) else ""
            css_class = (
                f"wordle-tile {tile_class(signal)}"
                if signal in {"G", "Y", "R"}
                else "wordle-tile wordle-tile-empty"
            )
            board_html.append(f"<div class='{css_class}'>{letter}</div>")
        board_html.append("</div>")
    board_html.append("</div></div>")
    st.markdown("".join(board_html), unsafe_allow_html=True)


def render_summary(session: GameSession) -> None:
    status = current_status(session)
    remaining = len(session.remaining_answers)
    if status == "solved":
        st.success(f"Solved in {session.number_of_guesses} guesses.")
    elif status == "exhausted":
        st.error("Game over. You used all available guesses.")
    elif status == "stalled":
        st.warning("No remaining candidates match the current feedback.")
    else:
        st.info("Keep narrowing the candidate list.")

    left, right = st.columns(2)
    left.metric(
        "Guesses",
        f"{session.number_of_guesses}/{session.allowed_number_of_guesses}",
    )
    right.metric("Candidates", remaining)


def render_controls(session: GameSession) -> None:
    status = current_status(session)
    suggestion = st.session_state[SUGGESTION_KEY]

    if status != "playing":
        return

    with st.form("turn-form", clear_on_submit=False):
        with st.container(border=True):
            st.caption("Suggested guess")
            st.subheader((suggestion or "No suggestion available").upper())
            st.caption("Leave guess empty to use the suggestion.")
        guess = st.text_input("Guess", placeholder=suggestion or "", max_chars=5)
        feedback = st.text_input("Feedback", placeholder="GGYRR", max_chars=5)
        submitted = st.form_submit_button("Apply turn")

    if not submitted:
        return

    validated_turn = validate_turn_inputs(session, guess, feedback, suggestion)
    if isinstance(validated_turn, str):
        st.error(validated_turn)
        return

    normalized_guess, normalized_feedback = validated_turn

    apply_turn(session, normalized_guess, normalized_feedback)
    st.session_state[HISTORY_KEY].append(
        {"guess": normalized_guess, "feedback": normalized_feedback}
    )
    refresh_suggestion()
    st.rerun()


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="W", layout="centered")
    inject_wordle_styles()
    st.title("Wordle solver")
    st.caption("Enter the feedback colors from Wordle to narrow the answer list.")

    with st.sidebar:
        st.header("Game settings")
        max_guesses = st.slider(
            "Maximum guesses",
            min_value=1,
            max_value=12,
            value=DEFAULT_MAX_GUESSES,
        )
        if st.button("Reset game", width="stretch"):
            reset_game(max_guesses)
            st.rerun()

    session = ensure_game(max_guesses)
    render_summary(session)
    render_board()
    render_controls(session)


def launch(argv: list[str] | None = None) -> int:
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(Path(__file__).resolve()),
    ]
    if argv is None:
        argv = sys.argv[1:]
    command.extend(argv)
    return subprocess.call(command)


if __name__ == "__main__":
    main()
