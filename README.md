# Wordle Solver

A small Wordle assistant packaged as `wordle_solver`.

Quick start

1. Create a virtual environment and install the package:

```bash
./.venv/bin/python -m pip install -e .
```

2. Run the Streamlit app from the project root:

```bash
./.venv/bin/python -m wordle_solver
```

3. Run the CLI directly if you want the terminal workflow:

```bash
./.venv/bin/wordle-solver
```

Options

- Streamlit uses a sidebar slider for the guess limit.
- The CLI still accepts `--max-guesses N` and `--seed N`.

Notes

- Word lists are loaded from the `data/` directory.
- If a word list is missing, the program will raise a `FileNotFoundError` with the file path.
