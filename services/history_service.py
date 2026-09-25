"""
Сервис истории запросов.
Хранит последние N запросов в JSON-файле (по умолчанию — history.json).
"""
import json
import uuid
from datetime import datetime
from pathlib import Path

from config import settings
from models.schemas import HistoryItem


class HistoryService:
    """Управление историей запросов."""

    def __init__(self):
        self.history_file: Path = settings.HISTORY_FILE
        self.max_items: int = settings.MAX_HISTORY_ITEMS
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not self.history_file.exists():
            self.history_file.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        try:
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save(self, items: list[dict]) -> None:
        self.history_file.write_text(
            json.dumps(items, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    def add_entry(
        self,
        request_type: str,
        request_summary: str,
        response_summary: str,
    ) -> HistoryItem:
        """Добавляет запись в начало истории, обрезает до max_items."""
        items = self._load()
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "request_type": request_type,
            "request_summary": request_summary[:200],
            "response_summary": response_summary[:500],
        }
        items.insert(0, entry)
        items = items[: self.max_items]
        self._save(items)
        return HistoryItem(**entry)

    def get_history(self) -> list[HistoryItem]:
        """Возвращает всю историю (последние max_items)."""
        return [HistoryItem(**item) for item in self._load()]

    def clear(self) -> None:
        """Очищает историю."""
        self._save([])


# Синглтон
history_service = HistoryService()
