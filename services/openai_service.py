"""
Сервис анализа через ProxyAPI (OpenAI-совместимый).
Три задачи:
- анализ текста (структурированный JSON),
- анализ изображения (Vision, структурированный JSON),
- анализ распарсенного контента сайта (текст из парсера).
"""
import base64
import json
import re
import time

from openai import OpenAI

from config import settings
from models.schemas import TextAnalysis, ImageAnalysis


class OpenAIService:
    """Обёртка над ProxyAPI для анализа."""

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.PROXY_API,
            base_url=settings.PROXY_BASE_URL,
        )
        self.text_model = settings.OPENAI_TEXT_MODEL
        self.vision_model = settings.OPENAI_VISION_MODEL

    def _parse_json_response(self, content: str) -> dict:
        """Извлекает JSON из ответа модели (учитывает ```json ... ```)."""
        if not content:
            return {}
        # Markdown-блок
        m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
        if m:
            content = m.group(1)
        # Просто JSON-объект
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            content = m.group(0)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}

    def analyze_text(self, text: str) -> TextAnalysis:
        """Анализ текста конкурента → структурированный ответ."""
        system = (
            "Ты — эксперт по конкурентному анализу. Проанализируй текст конкурента "
            "и верни строго JSON без пояснений.\n\n"
            "Формат:\n"
            "{\n"
            '  "strengths": ["..."],\n'
            '  "weaknesses": ["..."],\n'
            '  "unique_offers": ["..."],\n'
            '  "recommendations": ["..."],\n'
            '  "summary": "..."\n'
            "}\n\n"
            "Правила: 3-5 пунктов в каждом массиве, русский язык, конкретно и практично."
        )
        user = f"Проанализируй текст конкурента:\n\n{text}"

        start = time.time()
        resp = self.client.chat.completions.create(
            model=self.text_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        content = resp.choices[0].message.content
        data = self._parse_json_response(content)

        return TextAnalysis(
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", []),
            unique_offers=data.get("unique_offers", []),
            recommendations=data.get("recommendations", []),
            summary=data.get("summary", ""),
        )

    def analyze_image(self, image_path: str, mime_type: str = "image/jpeg") -> ImageAnalysis:
        """Анализ изображения (баннер, скриншот, упаковка)."""
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        system = (
            "Ты — эксперт по визуальному маркетингу и дизайну. Проанализируй изображение "
            "конкурента и верни строго JSON без пояснений.\n\n"
            "Формат:\n"
            "{\n"
            '  "description": "детальное описание",\n'
            '  "marketing_insights": ["..."],\n'
            '  "visual_style_score": 7,\n'
            '  "visual_style_analysis": "анализ стиля",\n'
            '  "recommendations": ["..."]\n'
            "}\n\n"
            "Правила: visual_style_score от 0 до 10, 3-5 пунктов в массивах, русский язык."
        )

        resp = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Проанализируй это изображение конкурента:"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                        },
                    ],
                },
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        content = resp.choices[0].message.content
        data = self._parse_json_response(content)

        return ImageAnalysis(
            description=data.get("description", ""),
            marketing_insights=data.get("marketing_insights", []),
            visual_style_score=int(data.get("visual_style_score", 5)),
            visual_style_analysis=data.get("visual_style_analysis", ""),
            recommendations=data.get("recommendations", []),
        )

    def analyze_parsed_content(
        self,
        title: str | None,
        h1: str | None,
        paragraph: str | None,
    ) -> TextAnalysis:
        """Анализ контента, извлечённого парсером (title + h1 + абзац)."""
        parts = []
        if title:
            parts.append(f"Title: {title}")
        if h1:
            parts.append(f"H1: {h1}")
        if paragraph:
            parts.append(f"Первый абзац: {paragraph}")
        combined = "\n\n".join(parts)

        if not combined.strip():
            return TextAnalysis(summary="Не удалось извлечь контент для анализа")

        return self.analyze_text(combined)


# Синглтон — создаётся один раз
openai_service = OpenAIService()
