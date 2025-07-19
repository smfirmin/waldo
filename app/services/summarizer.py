import google.generativeai as genai
import os


class EventSummarizer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Load the event summarization prompt from file."""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts",
            "event_summarization.txt",
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def summarize_events_at_location(
        self, article_text: str, location_name: str
    ) -> str:
        """
        Generate a brief summary of events that happened at a specific location.
        Returns: 1-2 sentence summary
        """
        # Limit text to avoid token limits
        truncated_text = article_text[:3000]
        prompt = self.prompt_template.format(
            article_text=truncated_text, location_name=location_name
        )

        try:
            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            # Ensure summary is concise
            if len(summary) > 200:
                summary = summary[:197] + "..."

            return summary if summary else "Mentioned in article."

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                print(f"Rate limit exceeded in summarizer for {location_name}: {e}")
                return "Summary temporarily unavailable due to rate limits"
            else:
                print(f"Error generating summary for {location_name}: {e}")
                return "Mentioned in article."
