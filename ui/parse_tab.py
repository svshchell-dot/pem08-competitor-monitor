"""
Вкладка парсинга сайта конкурента (Selenium + Vision).
"""
from pathlib import Path

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.parser_service import parser_service
from services.openai_service import openai_service
from services.history_service import history_service
from ui.widgets import ResultBlock, SummaryBlock, Loader


class ParseWorker(QThread):
    """Парсит сайт и анализирует контент (текст + скриншот)."""
    finished_ok = pyqtSignal(object, object)   # (ParsedContent, ImageAnalysis | None)
    failed = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            parsed = parser_service.parse(self.url)
            if parsed.error:
                self.failed.emit(parsed.error)
                return

            image_analysis = None
            if parsed.screenshot_path and Path(parsed.screenshot_path).exists():
                try:
                    image_analysis = openai_service.analyze_image(parsed.screenshot_path)
                except Exception:
                    image_analysis = None

            self.finished_ok.emit(parsed, image_analysis)
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")


class ParseTab(QWidget):
    """Вкладка «Парсинг сайта»."""

    def __init__(self):
        super().__init__()
        self._worker: ParseWorker | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        label = QLabel("URL сайта конкурента")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)

        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("example.com или https://example.com")
        self.url_input.returnPressed.connect(self._on_parse)
        url_row.addWidget(self.url_input, stretch=1)

        self.parse_btn = QPushButton("⚡ Парсить и анализировать")
        self.parse_btn.clicked.connect(self._on_parse)
        url_row.addWidget(self.parse_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._on_clear)
        url_row.addWidget(self.clear_btn)

        layout.addLayout(url_row)

        # Превью скриншота
        self.preview_label = QLabel("Скриншот появится после парсинга")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(160)
        self.preview_label.setStyleSheet(
            "background-color: #0b1220; border: 1px dashed #334155; "
            "border-radius: 6px; color: #64748b;"
        )
        layout.addWidget(self.preview_label)

        # Лоадер
        self.loader = Loader("Открываю сайт в Chrome...")
        self.loader.hide()
        layout.addWidget(self.loader)

        # Результаты
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(8)
        self.results_scroll.setWidget(self.results_container)
        self.results_scroll.hide()
        layout.addWidget(self.results_scroll)

        layout.addStretch()

    def _on_parse(self):
        url = self.url_input.text().strip()
        if not url:
            self._show_error("Введите URL.")
            return

        self._clear_results()
        self.parse_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.preview_label.setText("Загружаю...")
        self.loader.show()

        self._worker = ParseWorker(url)
        self._worker.finished_ok.connect(self._on_success)
        self._worker.failed.connect(self._on_error)
        self._worker.start()

    def _on_success(self, parsed, image_analysis):
        self.loader.hide()
        self.parse_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)

        # Превью
        if parsed.screenshot_path and Path(parsed.screenshot_path).exists():
            pixmap = QPixmap(parsed.screenshot_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    600, 250,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.preview_label.setPixmap(scaled)
                self.preview_label.setStyleSheet("background-color: #0b1220; border-radius: 6px;")

        # История
        try:
            history_service.add_entry(
                request_type="parse",
                request_summary=f"URL: {parsed.url}",
                response_summary=(parsed.title or parsed.h1 or "—")[:500],
            )
        except Exception:
            pass

        self._render(parsed, image_analysis)

    def _on_error(self, message: str):
        self.loader.hide()
        self.parse_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.preview_label.setText("Скриншот появится после парсинга")
        self._show_error(message)

    def _on_clear(self):
        self.url_input.clear()
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Скриншот появится после парсинга")
        self.preview_label.setStyleSheet(
            "background-color: #0b1220; border: 1px dashed #334155; "
            "border-radius: 6px; color: #64748b;"
        )
        self._clear_results()

    def _clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.results_scroll.hide()

    def _render(self, parsed, image_analysis):
        # Мета
        meta_items = []
        if parsed.title:
            meta_items.append(f"Title: {parsed.title}")
        if parsed.h1:
            meta_items.append(f"H1: {parsed.h1}")
        if parsed.url:
            meta_items.append(f"URL: {parsed.url}")
        if meta_items:
            self.results_layout.addWidget(ResultBlock("Метаданные страницы", meta_items, "•"))

        if parsed.first_paragraph:
            self.results_layout.addWidget(SummaryBlock("Первый абзац", parsed.first_paragraph))

        # Анализ скриншота
        if image_analysis:
            if image_analysis.description:
                self.results_layout.addWidget(SummaryBlock("Описание (Vision)", image_analysis.description))
            self.results_layout.addWidget(
                ResultBlock("Оценка стиля", [f"{image_analysis.visual_style_score} / 10"], "★")
            )
            self.results_layout.addWidget(
                ResultBlock("Маркетинговые инсайты", image_analysis.marketing_insights, "•")
            )
            self.results_layout.addWidget(
                ResultBlock("Рекомендации", image_analysis.recommendations, "→")
            )

        self.results_layout.addStretch()
        self.results_scroll.show()

    def _show_error(self, message: str):
        self._clear_results()
        error_block = ResultBlock("Ошибка", [message], "✗")
        self.results_layout.addWidget(error_block)
        self.results_layout.addStretch()
        self.results_scroll.show()
