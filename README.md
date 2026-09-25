# PEm08 — Мониторинг конкурентов

Мультимодальный desktop-ассистент на PyQt6 для анализа конкурентов:
- анализ текста (сильные/слабые стороны, УТП, рекомендации),
- анализ изображений (баннеры, скриншоты, упаковки) через Vision,
- парсинг сайтов через Selenium (Chrome) + анализ скриншота,
- история запросов (JSON).

## Возможности

- **📝 Анализ текста** — вставить текст конкурента → получить структурированный анализ: сильные стороны, слабые, УТП, рекомендации, резюме.
- **🖼️ Анализ изображения** — выбрать PNG/JPG/WEBP → получить описание, оценку визуального стиля (0–10), маркетинговые инсайты, рекомендации.
- **🌐 Парсинг сайта** — ввести URL → Chrome откроет страницу, сделает скриншот, извлечёт title/h1/первый абзац; скриншот уходит в Vision-модель для анализа дизайна и UX.
- **📋 История** — последние 10 запросов, с типом, кратким описанием и временем.

## Стек

- Python 3.11+
- PyQt6 (интерфейс, тёмная тема)
- openai SDK → **ProxyAPI** (OpenAI-совместимый, `gpt-4o-mini` для текста и Vision)
- **GigaChat** (Sber) через `requests` (OAuth + chat/completions)
- Selenium 4 + webdriver-manager (Chrome headless)
- python-dotenv, pydantic, Pillow, beautifulsoup4

## Структура
PEm08/
├── main.py # точка входа
├── config.py # загрузка .env, настройки
├── requirements.txt
├── .env.example # шаблон переменных
├── .env # секреты (chmod 600, не в git)
├── .gitignore
├── README.md
├── models/
│ ├── init.py
│ └── schemas.py # Pydantic-модели (TextAnalysis, ImageAnalysis, ParsedContent, HistoryItem)
├── services/
│ ├── init.py
│ ├── openai_service.py # ProxyAPI: анализ текста + Vision
│ ├── parser_service.py # Selenium: парсинг + скриншот
│ └── history_service.py # история запросов (JSON)
├── ui/
│ ├── init.py
│ ├── main_window.py # главное окно, тёмная тема
│ ├── widgets.py # общие виджеты (ResultBlock, SummaryBlock, Loader, HistoryCard)
│ ├── text_tab.py # вкладка анализа текста
│ ├── image_tab.py # вкладка анализа изображения
│ ├── parse_tab.py # вкладка парсинга сайта
│ └── history_tab.py # вкладка истории
├── screenshots/ # скриншоты парсинга (создаётся автоматически)
├── generated_images/ # (не используется в PEm08, оставлено от adgen)
└── history.json # история запросов (создаётся автоматически)

text

## Установка

### 1. Создать виртуальное окружение

```bash
python3 -m venv venv
source venv/bin/activate     # Linux/Mac
# или: venv\Scripts\activate  # Windows
2. Установить зависимости
bash
pip install -r requirements.txt
3. Настроить .env
Скопировать .env.example в .env и заполнить:

text
PROXY_API=sk-...                       # ключ ProxyAPI (proxyapi.ru)
GIGACHAT_CLIENT_ID=...                 # Client ID из ЛК GigaChat (Base64)
GIGACHAT_CLIENT_SECRET=...             # Client Secret из ЛК GigaChat (Base64)
OPENAI_TEXT_MODEL=gpt-4o-mini
OPENAI_VISION_MODEL=gpt-4o-mini
HISTORY_FILE=history.json
MAX_HISTORY_ITEMS=10
PARSER_TIMEOUT=30
PARSER_HEADLESS=true
Права на файл:

bash
chmod 600 .env
4. Убедиться, что установлен Google Chrome
bash
which google-chrome || which chromium
Если нет — установить:

bash
sudo apt install -y chromium
ChromeDriver устанавливается автоматически через webdriver-manager при первом запуске парсера.

Запуск
bash
python main.py
Откроется окно с четырьмя вкладками.

API (внутренние сервисы)
openai_service
Метод	Что делает
analyze_text(text)	→ TextAnalysis (strengths, weaknesses, unique_offers, recommendations, summary)
analyze_image(path, mime_type)	→ ImageAnalysis (description, marketing_insights, visual_style_score, visual_style_analysis, recommendations)
analyze_parsed_content(title, h1, paragraph)	→ TextAnalysis (для контента парсера)
parser_service
Метод	Что делает
parse(url)	→ ParsedContent (url, title, h1, first_paragraph, screenshot_path, error)
history_service
Метод	Что делает
add_entry(request_type, request_summary, response_summary)	добавляет запись
get_history()	→ list[HistoryItem]
clear()	очищает
Как это работает
Анализ текста
Пользователь вставляет текст.

openai_service.analyze_text отправляет в ProxyAPI (gpt-4o-mini) с system-промптом, требующим строго JSON.

Ответ парсится в TextAnalysis.

Результаты отрисовываются карточками.

Запись добавляется в history.json.

Анализ изображения
Пользователь выбирает файл (PNG/JPG/WEBP).

Файл → base64 → отправляется в Vision (gpt-4o-mini).

System-промпт требует JSON с оценкой стиля, инсайтами, рекомендациями.

Результат → ImageAnalysis → карточки.

Парсинг сайта
Пользователь вводит URL.

parser_service запускает headless Chrome через Selenium.

Открывает страницу, ждёт body, пауза 2 сек.

Извлекает title, h1, первый абзац.

Делает скриншот (1920×1080) → сохраняет в screenshots/.

Скриншот → base64 → Vision-модель.

Результаты: метаданные + первый абзац + анализ скриншота.

История
Файл history.json, последние 10 записей.

Обновляется автоматически при переходе на вкладку «История».

Асинхронность
Все сетевые операции (ProxyAPI, Selenium, GigaChat) выполняются в фоновых потоках (QThread) — интерфейс не зависает.

Известные ограничения
dall-e-3 в ProxyAPI недоступен (используем gpt-image-1/gpt-image-1-mini — в PEm07).

GigaChat требует verify=False (самоподписанный сертификат Sber).

Selenium: Chrome должен быть установлен в системе.

.exe не собирается на Linux; для Windows-сборки — PyInstaller на Windows-машине (см. отчёт).

Лицензия
Учебный проект (Zcoder, PEm08).
