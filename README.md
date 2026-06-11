### SG Mahjong

Folder structure (backend):
```
backend/
  app/ (frontend and backend integration)
    main.py
    api.py
  domain/ (models)
    game_state.py
    player.py
    tiles.py
  engine/ (round flow)
    round_engine.py
  rules/ (validations)
    chi.py
    pong.py
    gang.py
    scoring.py
  ai/ (opponents)
    base_ai.py
    simple_ai.py
  utils/
    helper.py
    serialization.py
  tests/
    unit/
    integration/
```