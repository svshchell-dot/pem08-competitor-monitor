"""
Сервис парсинга веб-страниц через Selenium (Chrome headless).
Открывает URL, извлекает title/h1/первый абзац, делает скриншот.
"""
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import settings
from models.schemas import ParsedContent


class ParserService:
    """Парсинг сайтов через headless Chrome."""

    def __init__(self):
        self.timeout = settings.PARSER_TIMEOUT
        self.headless = settings.PARSER_HEADLESS
        self.screenshots_dir = settings.BASE_DIR / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)

    def _build_driver(self) -> webdriver.Chrome:
        opts = Options()
        if self.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)

    def parse(self, url: str) -> ParsedContent:
        """Открывает URL, собирает title/h1/абзац и делает скриншот."""
        # Протокол
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        driver = None
        try:
            driver = self._build_driver()
            driver.set_page_load_timeout(self.timeout)
            driver.get(url)

            WebDriverWait(driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)  # динамический контент

            title = driver.title or None

            h1 = None
            try:
                el = driver.find_element(By.TAG_NAME, "h1")
                h1 = (el.text or "").strip() or None
            except Exception:
                pass

            first_paragraph = None
            try:
                for p in driver.find_elements(By.TAG_NAME, "p"):
                    text = (p.text or "").strip()
                    if len(text) > 50:
                        first_paragraph = text[:500]
                        break
            except Exception:
                pass

            # Скриншот
            ts = time.strftime("%Y%m%d_%H%M%S")
            safe = "".join(c for c in url.replace("https://", "").replace("http://", "")[:40]
                           if c.isalnum() or c in ("-", "_", "."))
            filename = f"{ts}_{safe or 'site'}.png"
            shot_path = self.screenshots_dir / filename
            driver.save_screenshot(str(shot_path))

            return ParsedContent(
                url=url,
                title=title,
                h1=h1,
                first_paragraph=first_paragraph,
                screenshot_path=str(shot_path),
            )

        except Exception as e:
            return ParsedContent(url=url, error=f"{type(e).__name__}: {e}")

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass


# Синглтон
parser_service = ParserService()
