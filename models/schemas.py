"""
Pydantic-модели для структурированных ответов AI.
Описывают, что мы ожидаем от ProxyAPI (текст, изображение, парсинг).
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# === Анализ текста ===

class TextAnalysis(BaseModel):
    """Структурированный анализ текста конкурента."""
    strengths: list[str] = Field(default_factory=list, description="Сильные стороны")
    weaknesses: list[str] = Field(default_factory=list, description="Слабые стороны")
    unique_offers: list[str] = Field(default_factory=list, description="Уникальные предложения")
    recommendations: list[str] = Field(default_factory=list, description="Рекомендации")
    summary: str = Field("", description="Общее резюме")


# === Анализ изображения ===

class ImageAnalysis(BaseModel):
    """Структурированный анализ изображения (баннер, скриншот, упаковка)."""
    description: str = Field("", description="Описание изображения")
    marketing_insights: list[str] = Field(default_factory=list, description="Маркетинговые инсайты")
    visual_style_score: int = Field(0, ge=0, le=10, description="Оценка стиля 0-10")
    visual_style_analysis: str = Field("", description="Анализ визуального стиля")
    recommendations: list[str] = Field(default_factory=list, description="Рекомендации")


# === Парсинг сайта ===

class ParsedContent(BaseModel):
    """Результат парсинга сайта."""
    url: str
    title: Optional[str] = None
    h1: Optional[str] = None
    first_paragraph: Optional[str] = None
    screenshot_path: Optional[str] = None
    analysis: Optional[TextAnalysis] = None
    error: Optional[str] = None


# === История ===

class HistoryItem(BaseModel):
    """Элемент истории запросов."""
    id: str
    timestamp: datetime
    request_type: str  # "text" | "image" | "parse"
    request_summary: str
    response_summary: str
