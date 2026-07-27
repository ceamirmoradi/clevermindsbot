import json
import os
from pathlib import Path
from typing import Any

DATA_FILE = Path(os.getenv("DATA_FILE", "data/games.json"))

def _load() -> dict[str, dict[str, Any]]:
    try:
        if DATA_FILE.exists():
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

games: dict[str, dict[str, Any]] = _load()
user_states: dict[int, str] = {}

def save_games() -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(games, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(DATA_FILE)
