#!/usr/bin/env python3
"""
Точка входа приложения PEm08 — Мониторинг конкурентов.
"""
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from config import settings
from ui.main_window import MainWindow


def main() -> int:
    # Проверка конфигурации
    errors = settings.validate()
    if errors:
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "Ошибка конфигурации",
            "Не заданы обязательные переменные окружения:\n\n" + "\n".join(errors) + "\n\n"
            "Создайте .env на основе .env.example и заполните ключи.",
        )
        return 1

    # Запуск приложения
    app = QApplication(sys.argv)
    app.setApplicationName("PEm08")
    app.setOrganizationName("Zcoder")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
