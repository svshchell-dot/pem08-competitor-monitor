"""
Вкладка анализа текста конкурента.
"""
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.openai_service import openai_service
from services.history_service import history_service
from ui.widgets import ResultBlock, SummaryBlock, Loader


class TextAnalysisWorker(QThread):
    """Фоновый поток для анализа текста."""
    finished_ok = pyqtSignal(object)   # TextAnalysis
    failed = pyqtSignal(str)

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def run(self):
        try:
            result = openai_service.analyze_text(self.text)
            self.finished_ok.emit(result)
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")


class TextTab(QWidget):
    """Вкладка «Анализ текста»."""

    def __init__(self):
        super().__init__()
        self._worker: TextAnalysisWorker | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        label = QLabel("Текст конкурента")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)

        self.text_input = QPlainTextEdit()
        self.text_input.setPlaceholderText(
            "Вставьте текст конкурента (описание продукта, лендинг, реклама)..."
        )
        self.text_input.setMinimumHeight(140)
        layout.addWidget(self.text_input)

        btn_row = QHBoxLayout()
        self.analyze_btn = QPushButton("⚡ Проанализировать")
        self.analyze_btn.clicked.connect(self._on_analyze)
        btn_row.addWidget(self.analyze_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.loader = Loader("Анализирую текст...")
        self.loader.hide()
        layout.addWidget(self.loader)

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

    def _on_analyze(self):
        text = self.text_input.toPlainText().strip()
        if len(text) < 10:
            self._show_error("Введите текст минимум 10 символов.")
            return

        self._clear_results()
        self.analyze_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.loader.show()

        self._worker = TextAnalysisWorker(text)
        self._worker.finished_ok.connect(self._on_success)
        self._worker.failed.connect(self._on_error)
        self._worker.start()

    def _on_success(self, analysis):
        self.loader.hide()
        self.analyze_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)

        try:
            history_service.add_entry(
                request_type="text",
                request_summary=self.text_input.toPlainText().strip()[:100],
                response_summary=analysis.summary or "—",
            )
        except Exception:
            pass

        self._render(analysis)

    def _on_error(self, message: str):
        self.loader.hide()
        self.analyze_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self._show_error(message)

    def _on_clear(self):
        self.text_input.clear()
        self._clear_results()

    def _clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.results_scroll.hide()

    def _render(self, analysis):
        self.results_layout.addWidget(ResultBlock("Сильные стороны", analysis.strengths, "✓"))
        self.results_layout.addWidget(ResultBlock("Слабые стороны", analysis.weaknesses, "✗"))
        self.results_layout.addWidget(ResultBlock("Уникальные предложения", analysis.unique_offers, "★"))
        self.results_layout.addWidget(ResultBlock("Рекомендации", analysis.recommendations, "→"))
        if analysis.summary:
            self.results_layout.addWidget(SummaryBlock("Резюме", analysis.summary))
        self.results_layout.addStretch()
        self.results_scroll.show()

    def _show_error(self, message: str):
        self._clear_results()
        error_block = ResultBlock("Ошибка", [message], "✗")
        self.results_layout.addWidget(error_block)
        self.results_layout.addStretch()
        self.results_scroll.show()
