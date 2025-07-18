import google.generativeai as genai


class EventSummarizer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def summarize_events_at_location(
        self, article_text: str, location_name: str
    ) -> str:
        """
        Generate a brief summary of events that happened at a specific location.
        Returns: 1-2 sentence summary
        """
        prompt = f"""
        Based on the following news article, provide a brief 1-2 sentence summary of what happened at "{location_name}".
        If the location is only mentioned in passing or no specific events are described there, return "Mentioned in article."
        
        Focus only on events, actions, or incidents that occurred at this specific location.
        
        Article text:
        {article_text[:3000]}  # Limit to avoid token limits
        
        Location: {location_name}
        
        Summary:
        """

        try:
            response = self.model.generate_content(prompt)
            summary = response.text.strip()

            # Ensure summary is concise
            if len(summary) > 200:
                summary = summary[:197] + "..."

            return summary if summary else "Mentioned in article."

        except Exception as e:
            print(f"Error generating summary for {location_name}: {e}")
            return "Mentioned in article."
