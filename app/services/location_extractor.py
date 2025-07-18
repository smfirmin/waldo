import google.generativeai as genai
from typing import List
import json
import re


class LocationExtractor:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def extract_locations(self, article_text: str) -> List[str]:
        """
        Extract location names from article text using Gemini.
        Returns list of location names.
        """
        prompt = f"""
        Analyze the following news article and extract ALL geographic locations mentioned. 
        Include cities, states, countries, landmarks, neighborhoods, and any other specific places.
        
        Return ONLY a JSON array of location names, no other text.
        Example format: ["New York City", "Central Park", "Manhattan", "United States"]
        
        Article text:
        {article_text[:4000]}  # Limit text to avoid token limits
        """

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON array from response
            json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if json_match:
                locations_json = json_match.group()
                locations = json.loads(locations_json)
                return [
                    loc for loc in locations if isinstance(loc, str) and loc.strip()
                ]
            else:
                return []

        except Exception as e:
            print(f"Error extracting locations: {e}")
            return []
