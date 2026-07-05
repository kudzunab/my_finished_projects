"""
Хранение таблицы рекордов (scoreboard) в JSON рядом с файлом сохранения.
Записи нормализуются до строгого вида: gold, outcome, at.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.datalayer.load_manager import return_path

SCOREBOARD_FILE = "scoreboard.json"
_MAX_ENTRIES = 30
_MAX_GOLD = 10**12
_MAX_AT_LEN = 200
_VALID_OUTCOMES = frozenset({"quit", "death", "win"})


def get_scoreboard_path() -> Path:
    """Получает путь к файлу scoreboard.json"""
    return Path(return_path(SCOREBOARD_FILE)).resolve()


def _load_raw() -> dict:
    """Загружает данные из scoreboard.json"""
    path = get_scoreboard_path()
    if not path.exists():
        return {"entries": []}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"entries": []}
    entries = data.get("entries")
    if not isinstance(entries, list):
        return {"entries": []}
    return {"entries": entries}


def _write_atomic(data: dict) -> None:
    """Записывает данные в scoreboard.json"""
    path = get_scoreboard_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _normalize_entry(raw: Any) -> dict[str, Any] | None:
    """
    Нормализованная запись {"gold", "outcome", "at"} или None, если данные не подходят.
    """
    if not isinstance(raw, dict):
        return None
    try:
        gold = int(raw.get("gold", 0))
    except (TypeError, ValueError):
        return None
    if gold < 0:
        return None
    gold = min(gold, _MAX_GOLD)

    oc = raw.get("outcome", "quit")
    if not isinstance(oc, str):
        oc = str(oc) if oc is not None else "quit"
    if oc not in _VALID_OUTCOMES:
        oc = "quit"

    at_val = raw.get("at", "")
    if not isinstance(at_val, str):
        at_val = str(at_val) if at_val is not None else ""
    at_val = at_val.strip()[:_MAX_AT_LEN]

    return {"gold": gold, "outcome": oc, "at": at_val}


def format_scoreboard_datetime(at_iso: str) -> str:
    """
    Строка для UI: дата и время только часы:минуты (без секунд и суффикса +00:00).
    Время в том же поясе, что и в ISO-строке
    """
    s = (at_iso or "").strip()
    if not s:
        return "-"
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return s[:16] if s else "-"


def append_session(gold: int, outcome: str) -> None:
    """
    Добавляет запись о завершённой сессии.
    outcome: 'quit' | 'death' | 'win'
    """
    if outcome not in _VALID_OUTCOMES:
        outcome = "quit"
    try:
        gold = max(0, min(int(gold), _MAX_GOLD))
    except (TypeError, ValueError):
        gold = 0

    new_entry = _normalize_entry(
        {
            "gold": gold,
            "outcome": outcome,
            "at": datetime.now(timezone.utc).isoformat(),
        }
    )
    if new_entry is None:
        return

    data = _load_raw()
    entries: list[dict[str, Any]] = []
    for e in data["entries"]:
        n = _normalize_entry(e)
        if n is not None:
            entries.append(n)

    entries.append(new_entry)
    entries.sort(key=lambda x: int(x["gold"]), reverse=True)
    entries = entries[:_MAX_ENTRIES]
    _write_atomic({"entries": entries})


def record_session_score(gold: int, *, is_dead: bool, is_win: bool = False) -> None:
    """Обертка для вызова из app после выхода с игрового экрана"""
    if is_win:
        outcome = "win"
    elif is_dead:
        outcome = "death"
    else:
        outcome = "quit"
    append_session(gold, outcome)


def get_sorted_entries(limit: int = 30) -> list[dict[str, Any]]:
    """Нормализованные записи, по золоту по убыванию."""
    data = _load_raw()
    entries: list[dict[str, Any]] = []
    for e in data["entries"]:
        n = _normalize_entry(e)
        if n is not None:
            entries.append(n)
    entries.sort(key=lambda x: int(x["gold"]), reverse=True)
    return entries[: max(0, limit)]
