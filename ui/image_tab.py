"""
Вкладка анализа изображения конкурента.
"""
from pathlib import Path

from PyQt6.QtCore import QThread, Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.openai_service import openai_service
from services.history_service import history_service
from ui.widgets import ResultBlock, SummaryBlock, Loader


class ImageAnalysisWorker(QThread):
    finished_ok = pyqtSignal(object)   # ImageAnalysis
    failed = pyqtSignal(str)

    def __init__(self, image_path: str):
        super().__init__()
        self.image_path = image_path

    def run(self):
        try:
            mime = "image/png" if self.image_path.lower().endswith(".png") else "image/jpeg"
            result = openai_service.analyze_image(self.image_path, mime_type=mime)
            self.finished_ok.emit(result)
        except Exception as e:
            self.failed.emit(f"{type(e).__name__}: {e}")


class ImageTab(QWidget):
    """Вкладка «Анализ изображения»."""

    def __init__(self):
        super().__init__()
        self._worker: ImageAnalysisWorker | None = None
        self._selected_path: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        label = QLabel("Изображение конкурента")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)

        btn_row = QHBoxLayout()
        self.select_btn = QPushButton("📁 Выбрать изображение")
        self.select_btn.clicked.connect(self._on_select)
        btn_row.addWidget(self.select_btn)

        self.analyze_btn = QPushButton("⚡ Проанализировать")
        self.analyze_btn.clicked.connect(self._on_analyze)
        self.analyze_btn.setEnabled(False)
        btn_row.addWidget(self.analyze_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._on_clear)
        btn_row.addWidget(self.clear_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.preview_label = QLabel("Изображение не выбрано")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet(
            "background-color: #0b1220; border: 1px dashed #334155; "
            "border-radius: 6px; color: #64748b;"
        )
        layout.addWidget(self.preview_label)

        self.loader = Loader("Анализирую изображение...")
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

    def _on_select(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.webp *.gif)",
        )
        if not path:
            return

        self._selected_path = path
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.preview_label.setText("Не удалось загрузить изображение")
            self.analyze_btn.setEnabled(False)
            return

        scaled = pixmap.scaled(
            500, 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)
        self.preview_label.setStyleSheet("background-color: #0b1220; border-radius: 6px;")
        self.analyze_btn.setEnabled(True)
        self._clear_results()

    def _on_analyze(self):
        if not self._selected_path:
            return

        self._clear_results()
        self.analyze_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.loader.show()

        self._worker = ImageAnalysisWorker(self._selected_path)
        self._worker.finished_ok.connect(self._on_success)
        self._worker.failed.connect(self._on_error)
        self._worker.start()

    def _on_success(self, analysis):
        self.loader.hide()
        self.analyze_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)

        try:
            history_service.add_entry(
                request_type="image",
                request_summary=f"Изображение: {Path(self._selected_path).name}",
                response_summary=(analysis.description or "—")[:500],
            )
        except Exception:
            pass

        self._render(analysis)

    def _on_error(self, message: str):
        self.loader.hide()
        self.analyze_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self._show_error(message)

    def _on_clear(self):
        self._selected_path = None
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Изображение не выбрано")
        self.preview_label.setStyleSheet(
            "background-color: #0b1220; border: 1px dashed #334155; "
            "border-radius: 6px; color: #64748b;"
        )
        self.analyze_btn.setEnabled(False)
        self._clear_results()

    def _clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.results_scroll.hide()

    def _render(self, analysis):
        if analysis.description:
            self.results_layout.addWidget(SummaryBlock("Описание", analysis.description))

        score_text = f"{analysis.visual_style_score} / 10"
        self.results_layout.addWidget(ResultBlock("Оценка стиля", [score_text], "★"))

        if analysis.visual_style_analysis:
            self.results_layout.addWidget(SummaryBlock("Анализ визуального стиля", analysis.visual_style_analysis))

        self.results_layout.addWidget(ResultBlock("Маркетинговые инсайты", analysis.marketing_insights, "•"))
        self.results_layout.addWidget(ResultBlock("Рекомендации", analysis.recommendations, "→"))
        self.results_layout.addStretch()
        self.results_scroll.show()

    def _show_error(self, message: str):
        self._clear_results()
        error_block = ResultBlock("Ошибка", [message], "✗")
        self.results_layout.addWidget(error_block)
        self.results_layout.addStretch()
        self.results_scroll.show()
