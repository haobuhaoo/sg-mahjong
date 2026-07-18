# SG Mahjong

## Project state
- **Backend only** — frontend Flutter scaffold exists but is not in active development.
- All game logic lives in the Python backend.

## Commands
    Run app:     python3.13 -m backend.app.main        (from project root)
    Run tests:   python3.13 -m pytest backend/          (from project root)

All imports use `backend.` prefix — commands must run from project root.

## Python environment
- Python 3.13 required
- Venv at `backend\venv\`
- Only dependency is pytest (no requirements.txt)

## Architecture
    backend/
      app/main.py       # CLI test harness (no comments needed)
      domain/           # GameState, Player, Tile types
      engine/           # RoundEngine — core game loop
      rules/            # Win detection, chi/pong/gang, scoring, meld discard rules
      utils/            # helpers, errors, hand_types, serialization
      tests/            # mirrors source structure (no comments needed)

## Code conventions
- **Terminology**: use "gang" (not "kong"), use "self-pick" (not "zimo")
- **Comments**: include docstrings on all methods and classes in source code.
  Tests and `main.py` are exempt.
- **Comments must use English only** — no Chinese terms/names.
- All commands use Python 3.13.

## Known quirks
- `GameState.MAX_PLAYERS = 3` means up to 3 *other* players (host is the 4th).
  AI can sub in to fill seats.

## References
- `Singapore_Mahjong_Rules_en.md` — **authoritative** rules documentation.
  Read this first for game rules.
- `design.md` — high-level game overview only (less detailed than rules doc).
