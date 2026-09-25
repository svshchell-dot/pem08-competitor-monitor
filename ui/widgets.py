"""
Общие виджеты PyQt6 для PEm08.
- ResultBlock: карточка с заголовком и списком
- Loader: индикатор загрузки
"""
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QWidget,
)
from PyQt6.QtCore import Qt


class ResultBlock(QFrame):
    """Карточка с заголовком и списком пунктов."""

    def __init__(self, title: str, items: list[str], icon: str = "•"):
        super().__init__()
        self.setObjectName("resultBlock")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setObjectName("resultBlockTitle")
        layout.addWidget(title_label)

        if not items:
            empty = QLabel("— пусто —")
            empty.setStyleSheet("color: #64748b; font-style: italic;")
            layout.addWidget(empty)
            return

        for item in items:
            row = QLabel(f"{icon} {item}")
            row.setWordWrap(True)
            row.setStyleSheet("color: #cbd5e1;")
            layout.addWidget(row)


class SummaryBlock(QFrame):
    """Карточка с текстовым резюме."""

    def __init__(self, title: str, text: str):
        super().__init__()
        self.setObjectName("summaryBlock")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_label = QLabel(f"<b>{title}</b>")
        title_label.setObjectName("summaryBlockTitle")
        layout.addWidget(title_label)

        body = QLabel(text or "— нет данных —")
        body.setWordWrap(True)
        body.setStyleSheet("color: #e2e8f0; line-height: 1.5;")
        layout.addWidget(body)


class Loader(QWidget):
    """Индикатор загрузки с сообщением."""

    def __init__(self, message: str = "Обработка..."):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("color: #94a3b8; font-size: 13px;")

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setFixedWidth(240)

        layout.addWidget(self.message_label)
        layout.addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_message(self, message: str) -> None:
        self.message_label.setText(message)


class HistoryCard(QFrame):
    """Карточка записи истории."""

    def __init__(self, item_type: str, summary: str, timestamp: str):
        super().__init__()
        self.setObjectName("historyCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        icons = {"text": "📝", "image": "🖼️", "parse": "🌐"}
        type_labels = {"text": "Анализ текста", "image": "Анализ изображения", "parse": "Парсинг сайта"}

        icon = QLabel(icons.get(item_type, "📄"))
        icon.setStyleSheet("font-size: 22px;")
        icon.setFixedWidth(30)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)

        type_label = QLabel(type_labels.get(item_type, item_type))
        type_label.setStyleSheet("color: #22d3ee; font-weight: bold; font-size: 12px;")

        summary_label = QLabel(summary or "—")
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("color: #cbd5e1; font-size: 12px;")

        content_layout.addWidget(type_label)
        content_layout.addWidget(summary_label)

        time_label = QLabel(timestamp)
        time_label.setStyleSheet("color: #64748b; font-size: 11px;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(icon)
        layout.addWidget(content, stretch=1)
        layout.addWidget(time_label)
