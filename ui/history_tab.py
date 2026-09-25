"""
Вкладка истории запросов.
Показывает последние N записей из history.json.
"""
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.history_service import history_service
from ui.widgets import HistoryCard


class HistoryTab(QWidget):
    """Вкладка «История»."""

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Последние запросы")
        title.setObjectName("fieldLabel")
        header.addWidget(title)
        header.addStretch()

        self.refresh_btn = QPushButton("↻ Обновить")
        self.refresh_btn.setObjectName("secondary")
        self.refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self.refresh_btn)

        self.clear_btn = QPushButton("🗑 Очистить")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._on_clear)
        header.addWidget(self.clear_btn)

        layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(6)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.refresh()

    def refresh(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        items = history_service.get_history()
        if not items:
            empty = QLabel("История пуста")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("color: #64748b; padding: 40px;")
            self.container_layout.addWidget(empty)
            self.container_layout.addStretch()
            return

        for item in items:
            ts = item.timestamp
            if isinstance(ts, datetime):
                ts_str = ts.strftime("%d.%m %H:%M")
            else:
                ts_str = str(ts)[:16]

            card = HistoryCard(
                item_type=item.request_type,
                summary=item.request_summary,
                timestamp=ts_str,
            )
            self.container_layout.addWidget(card)

        self.container_layout.addStretch()

    def _on_clear(self):
        history_service.clear()
        self.refresh()
