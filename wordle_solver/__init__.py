"""Wordle solver package."""

from .cli import main as cli_main
from .session import GameSession, create_game_session


def main(*args, **kwargs):
    from .streamlit_app import launch

    return launch(*args, **kwargs)


__all__ = ["GameSession", "create_game_session", "cli_main", "main"]
