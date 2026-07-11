from __future__ import annotations

from wordle_solver import data


def test_load_word_list_from_custom_dir(tmp_path, monkeypatch):
    file = tmp_path / "mywords.txt"
    file.write_text("one\ntwo\n", encoding="utf-8")
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    assert data.load_word_list("mywords.txt") == ["one", "two"]


def test_load_word_list_missing_file_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    try:
        data.load_word_list("nope.txt")
    except FileNotFoundError:
        # expected
        return
    raise AssertionError("Expected FileNotFoundError for missing word list")
