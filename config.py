"""
Конфигурация приложения PEm08.
Загружает переменные из .env и предоставляет их остальному коду.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Загружаем .env из корня проекта
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Настройки приложения."""
    BASE_DIR: Path = BASE_DIR
    # === ProxyAPI ===
    PROXY_API: str = os.getenv("PROXY_API", "")
    PROXY_BASE_URL: str = "https://api.proxyapi.ru/openai/v1"

    # === Модели ===
    OPENAI_TEXT_MODEL: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
    OPENAI_VISION_MODEL: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")

    # === GigaChat ===
    GIGACHAT_CLIENT_ID: str = os.getenv("GIGACHAT_CLIENT_ID", "")
    GIGACHAT_CLIENT_SECRET: str = os.getenv("GIGACHAT_CLIENT_SECRET", "")
    GIGACHAT_OAUTH_URL: str = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    GIGACHAT_API_URL: str = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # === История ===
    HISTORY_FILE: Path = BASE_DIR / os.getenv("HISTORY_FILE", "history.json")
    MAX_HISTORY_ITEMS: int = int(os.getenv("MAX_HISTORY_ITEMS", "10"))

    # === Парсер ===
    PARSER_TIMEOUT: int = int(os.getenv("PARSER_TIMEOUT", "30"))
    PARSER_HEADLESS: bool = os.getenv("PARSER_HEADLESS", "true").lower() in ("1", "true", "yes")

    # === Пути ===
    ASSETS_DIR: Path = BASE_DIR / "assets"

    @classmethod
    def validate(cls) -> list[str]:
        """Проверяет, что обязательные переменные заданы.
        Возвращает список ошибок (пустой, если всё ок)."""
        errors = []
        if not cls.PROXY_API:
            errors.append("PROXY_API не задан в .env")
        if not cls.GIGACHAT_CLIENT_ID:
            errors.append("GIGACHAT_CLIENT_ID не задан в .env")
        if not cls.GIGACHAT_CLIENT_SECRET:
            errors.append("GIGACHAT_CLIENT_SECRET не задан в .env")
        return errors


settings = Settings()
