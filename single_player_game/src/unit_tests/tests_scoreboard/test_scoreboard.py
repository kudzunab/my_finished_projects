"""
Тесты для src/datalayer/scoreboard_store.py

Запуск из корня репозитория:
    PYTHONPATH=. pytest src/unit_tests/tests_scoreboard -v

"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.datalayer.scoreboard_store import (
    append_session,
    format_scoreboard_datetime,
    get_sorted_entries,
    record_session_score,
)
from src.datalayer import scoreboard_store as sb



@pytest.fixture
def isolated_scoreboard_file(tmp_path: Path) -> Path:
    """Путь к временному scoreboard.json (файл может ещё не существовать)."""
    return tmp_path / "scoreboard.json"


@pytest.fixture(name="scoreboard_path")
def patch_scoreboard_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """
    Подменяет get_scoreboard_path() на временный файл.
    Возвращает тот же Path
    """
    sb_path = tmp_path / "scoreboard.json"
    monkeypatch.setattr(
        "src.datalayer.scoreboard_store.get_scoreboard_path",
        lambda: sb_path,
    )
    return sb_path


class TestFormatScoreboardDatetime:
    """Класс для тестов format_scoreboard_datetime"""

    def test_empty_string_returns_dash(self) -> None:
        """Тест на возврат тире для пустой строки"""
        assert format_scoreboard_datetime("") == "-"
        assert format_scoreboard_datetime("   ") == "-"

    def test_iso_with_z_suffix(self) -> None:
        """Тест на форматирование ISO даты с суффиксом Z"""
        s = "2024-03-15T14:30:00Z"
        out = format_scoreboard_datetime(s)
        assert out == "2024-03-15 14:30"

    def test_invalid_iso_returns_truncated_or_dash(self) -> None:
        """Тест на возврат первых 16 символов невалидной даты"""
        assert format_scoreboard_datetime("not-a-date") == "not-a-date"[:16]


class TestAppendAndSortedEntries:
    """Класс для тестов append_session и get_sorted_entries"""

    @pytest.mark.usefixtures("scoreboard_path")
    def test_sorts_by_gold_desc(self) -> None:
        """Тест на сортировку записей по золоту по убыванию"""
        append_session(10, "quit")
        append_session(100, "win")
        append_session(50, "death")

        rows = get_sorted_entries(limit=30)
        assert [r["gold"] for r in rows] == [100, 50, 10]
        assert rows[0]["outcome"] == "win"

    @pytest.mark.usefixtures("scoreboard_path")
    def test_record_session_score_maps_flags(self) -> None:
        """Тест на запись сессии и соответствие флагов"""
        record_session_score(42, is_dead=False, is_win=False)
        record_session_score(1, is_dead=True, is_win=False)
        record_session_score(999, is_dead=False, is_win=True)

        rows = get_sorted_entries()
        by_gold = {r["gold"]: r["outcome"] for r in rows}
        assert by_gold[999] == "win"
        assert by_gold[1] == "death"
        assert by_gold[42] == "quit"


class TestLoadNormalizesEntries:
    """Класс для тестов _normalize_entry"""

    def test_skips_invalid_entries_keeps_valid(self, scoreboard_path: Path) -> None:
        """Тест на игнорирование битых и сохранение валидных записей"""
        path = scoreboard_path
        path.write_text(
            json.dumps(
                {
                    "entries": [
                        "not-a-dict",
                        {"gold": 7, "outcome": "win", "at": "2020-01-01T00:00:00+00:00"},
                        {"gold": "oops", "outcome": "quit", "at": ""},
                    ]
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        rows = get_sorted_entries()
        assert len(rows) == 1
        assert rows[0]["gold"] == 7
        assert rows[0]["outcome"] == "win"

    def test_corrupt_json_returns_empty(self, scoreboard_path: Path) -> None:
        """Битый JSON на диске — как пустой scoreboard."""
        scoreboard_path.write_text("{broken", encoding="utf-8")
        assert get_sorted_entries() == []


class TestNormalizeEntry:
    """Класс для тестов _normalize_entry"""

    def test_unknown_outcome_becomes_quit(self) -> None:
        """Тест на преобразование неизвестного флага в quit"""
        raw = {"gold": 5, "outcome": "cheat", "at": "x"}
        out = sb._normalize_entry(raw) # pylint: disable=protected-access
        assert out is not None
        assert out["outcome"] == "quit"

    def test_gold_clamped_to_max(self) -> None:
        """Тест на ограничение золота максимальным значением"""
        max_gold = 10**12  # как _MAX_GOLD в scoreboard_store
        raw = {"gold": max_gold + 999, "outcome": "quit", "at": ""}
        out = sb._normalize_entry(raw) # pylint: disable=protected-access
        assert out is not None
        assert out["gold"] == max_gold

    def test_negative_gold_rejected(self) -> None:
        """Неподходящий gold (< 0) = None"""
        assert (
            sb._normalize_entry({"gold": -1, "outcome": "quit", "at": ""})  # pylint: disable=protected-access
            is None
        )


class TestAppendTruncation:
    """Лимит записей на диске (_MAX_ENTRIES = 30)."""

    @pytest.mark.usefixtures("scoreboard_path")
    def test_append_truncates_to_30_entries(self) -> None:
        """После 35 добавлений в файле остаётся только топ-30 по золоту."""
        for gold in range(35):
            append_session(gold, "quit")
        rows = get_sorted_entries(limit=100)
        assert len(rows) == 30
        assert [r["gold"] for r in rows] == list(range(34, 4, -1))
