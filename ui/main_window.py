"""
Главное окно приложения PEm08.
Тёмная тема, вкладки: Текст / Изображение / Сайт / История.
"""
from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from config import settings


DARK_THEME = """
QMainWindow, QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'DejaVu Sans', sans-serif;
}
QTabWidget::pane {
    border: 1px solid #1e293b;
    border-radius: 6px;
    background-color: #111827;
    top: -1px;
}
QTabBar::tab {
    background-color: #1e293b;
    color: #94a3b8;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #06b6d4;
    color: #0f172a;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background-color: #334155;
    color: #e2e8f0;
}
QPushButton {
    background-color: #06b6d4;
    color: #0f172a;
    border: none;
    border-radius: 6px;
    padding: 10px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #22d3ee;
}
QPushButton:disabled {
    background-color: #334155;
    color: #64748b;
}
QPushButton#secondary {
    background-color: #334155;
    color: #e2e8f0;
}
QPushButton#secondary:hover {
    background-color: #475569;
}
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #0b1220;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 8px 10px;
    color: #e2e8f0;
    font-size: 13px;
    selection-background-color: #06b6d4;
    selection-color: #0f172a;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #06b6d4;
}
QLabel {
    color: #cbd5e1;
}
QLabel#heading {
    color: #f1f5f9;
    font-size: 20px;
    font-weight: bold;
}
QLabel#subheading {
    color: #94a3b8;
    font-size: 13px;
}
QLabel#fieldLabel {
    color: #94a3b8;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QFrame#resultBlock {
    background-color: #0b1220;
    border: 1px solid #1e293b;
    border-left: 3px solid #06b6d4;
    border-radius: 6px;
}
QLabel#resultBlockTitle {
    color: #22d3ee;
    font-size: 13px;
}
QFrame#summaryBlock {
    background-color: #0b1220;
    border: 1px solid #1e293b;
    border-left: 3px solid #a855f7;
    border-radius: 6px;
}
QLabel#summaryBlockTitle {
    color: #c084fc;
    font-size: 13px;
}
QFrame#historyCard {
    background-color: #0b1220;
    border: 1px solid #1e293b;
    border-radius: 6px;
}
QProgressBar {
    background-color: #1e293b;
    border: none;
    border-radius: 3px;
}
QProgressBar::chunk {
    background-color: #06b6d4;
    border-radius: 3px;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background-color: #0f172a;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #334155;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QStatusBar {
    background-color: #0b1220;
    color: #94a3b8;
    border-top: 1px solid #1e293b;
}
"""


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PEm08 — Мониторинг конкурентов")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        self.setStyleSheet(DARK_THEME)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        heading = QLabel("Мониторинг конкурентов")
        heading.setObjectName("heading")

        subheading = QLabel("AI-ассистент для анализа текста, изображений и сайтов")
        subheading.setObjectName("subheading")

        layout.addWidget(heading)
        layout.addWidget(subheading)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        layout.addWidget(self.tabs)

        from ui.text_tab import TextTab
        from ui.image_tab import ImageTab
        from ui.parse_tab import ParseTab
        from ui.history_tab import HistoryTab

        self.text_tab = TextTab()
        self.tabs.addTab(self.text_tab, "📝 Текст")

        self.image_tab = ImageTab()
        self.tabs.addTab(self.image_tab, "🖼️ Изображение")

        self.parse_tab = ParseTab()
        self.tabs.addTab(self.parse_tab, "🌐 Сайт")

        self.history_tab = HistoryTab()
        self.tabs.addTab(self.history_tab, "📋 История")

        # Обновляем историю при переключении на вкладку
        self.tabs.currentChanged.connect(self._on_tab_changed)

        status = QStatusBar()
        status.showMessage(
            f"Модели: текст={settings.OPENAI_TEXT_MODEL}, vision={settings.OPENAI_VISION_MODEL} | "
            f"История: {settings.MAX_HISTORY_ITEMS} записей"
        )
        self.setStatusBar(status)

    def _on_tab_changed(self, index: int):
        widget = self.tabs.widget(index)
        if widget is self.history_tab:
            self.history_tab.refresh()
