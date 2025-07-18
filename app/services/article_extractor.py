import requests
from bs4 import BeautifulSoup
from typing import Tuple, Optional


class ArticleExtractor:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def extract_from_url(self, url: str) -> Tuple[Optional[str], str]:
        """
        Extract article title and text from URL.
        Returns: (title, text)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = None
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip()

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text from common article containers
            article_selectors = [
                "article",
                ".article-body",
                ".story-body",
                ".entry-content",
                ".post-content",
                ".content",
            ]

            text = ""
            for selector in article_selectors:
                article_element = soup.select_one(selector)
                if article_element:
                    text = article_element.get_text()
                    break

            # Fallback to body if no article container found
            if not text:
                body = soup.find("body")
                if body:
                    text = body.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            text = "\n".join(line for line in lines if line)

            return title, text

        except Exception as e:
            raise Exception(f"Failed to extract article: {str(e)}")
