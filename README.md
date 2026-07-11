# Wordle Solver

A small Wordle assistant packaged as `wordle_solver`.

Quick start

1. Create a virtual environment and install dependencies (if any).

2. Run the CLI from the project root:

```bash
./.venv/bin/python -m wordle_solver
```

Options

- `--max-guesses N` — maximum allowed guesses (default 6)
- `--seed N` — seed for deterministic suggestions

Notes

- Word lists are loaded from the `data/` directory.
- If a word list is missing, the program will raise a `FileNotFoundError` with the file path.
