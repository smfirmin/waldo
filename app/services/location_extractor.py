import google.generativeai as genai
from typing import List
import json
import re
import os
import logging
from app.models.data_models import ExtractedLocation

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when API rate limits are exceeded"""

    pass


class LocationExtractor:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model_name = "gemini-2.0-flash"
        self.model = genai.GenerativeModel(self.model_name)
        self.prompt_template = self._load_prompt_template()
        self.correction_template = self._load_correction_template()
        self.max_tokens = self._get_model_max_tokens()

    def _load_prompt_template(self) -> str:
        """Load the location extraction prompt from file."""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts",
            "location_extraction.txt",
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_correction_template(self) -> str:
        """Load the location correction prompt from file."""
        prompt_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "prompts",
            "location_correction.txt",
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _get_model_max_tokens(self) -> int:
        """
        Get the maximum token limit for the current model from Gemini API.
        Returns a safe default if the API call fails.
        """
        try:
            # List all available models
            models = genai.list_models()

            for model in models:
                # Check if this is our model (handle both short and full names)
                if model.name.endswith(self.model_name) or model.name.endswith(
                    f"models/{self.model_name}"
                ):
                    # Get input token limit
                    if hasattr(model, "input_token_limit"):
                        max_tokens = model.input_token_limit
                        logger.info(f"Model {self.model_name} max tokens: {max_tokens}")
                        return max_tokens

                    # Fallback to supported_generation_methods info
                    if hasattr(model, "supported_generation_methods"):
                        logger.info(
                            f"Found model {model.name} but no token limit info available"
                        )
                        break

            logger.warning(
                f"Could not find token limit for {self.model_name}, using default"
            )

        except Exception as e:
            logger.error(f"Error getting model info: {e}")

        # Safe default for Gemini 2.5 Flash (as of 2024)
        return 1000000  # 1M tokens

    def _calculate_safe_text_limit(self, prompt_size: int) -> int:
        """
        Calculate safe text limit based on model token limit and prompt size.
        Leaves buffer for response tokens and safety margin.
        """
        # Reserve tokens for:
        # - Prompt template: estimated from prompt_size
        # - Response: ~2000 tokens for JSON response
        # - Safety buffer: 10% of total

        response_tokens = 2000
        safety_buffer = int(self.max_tokens * 0.1)
        # divide tokens by 4 for english chars
        max_chars = self.max_tokens / 4 - prompt_size - response_tokens - safety_buffer

        # Ensure minimum viable size
        min_chars = 1000
        safe_limit = max(min_chars, max_chars)

        logger.info(
            f"Calculated safe text limit: {safe_limit} chars (max_tokens: {self.max_tokens})"
        )
        return safe_limit

    def extract_locations(self, article_text: str) -> List[ExtractedLocation]:
        """
        Extract locations with context from article text using Gemini.
        Returns list of ExtractedLocation objects with rich metadata.
        """
        # Calculate dynamic text limit based on model capabilities
        prompt_size = len(self.prompt_template) // 4  # Rough token estimate
        safe_text_limit = self._calculate_safe_text_limit(prompt_size)

        # Truncate text if necessary
        if len(article_text) > safe_text_limit:
            truncated_text = article_text[:safe_text_limit]
            logger.info(
                f"Truncated article text from {len(article_text)} to {len(truncated_text)} chars"
            )
        else:
            truncated_text = article_text

        prompt = self.prompt_template.format(article_text=truncated_text)

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            logger.info(f"LLM response: {response_text[:200]}...")

            # Extract JSON array from response
            json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if json_match:
                locations_json = json_match.group()
                locations_data = json.loads(locations_json)

                extracted_locations = []
                for loc_data in locations_data:
                    try:
                        if isinstance(loc_data, dict):
                            extracted_locations.append(ExtractedLocation(**loc_data))
                        else:
                            logger.warning(
                                f"Expected dict, got {type(loc_data)}: {loc_data}"
                            )
                            continue
                    except Exception as e:
                        logger.error(f"Failed to parse location data {loc_data}: {e}")
                        continue

                # If we got some valid locations, return them
                if extracted_locations:
                    logger.info(f"Extracted {len(extracted_locations)} locations")
                    return extracted_locations

                # If no valid locations but we had JSON, try self-correction
                logger.warning("No valid locations parsed, attempting self-correction")
                return self._attempt_self_correction(response_text)
            else:
                logger.warning("No JSON array found in LLM response")
                return []

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                logger.error(f"Rate limit exceeded: {e}")
                raise RateLimitError(
                    "API rate limit exceeded. Please try again in a few moments."
                )
            else:
                logger.error(f"Error extracting locations: {e}")
                return []

    def _attempt_self_correction(
        self, original_response: str
    ) -> List[ExtractedLocation]:
        """
        Attempt to fix malformed LLM responses by asking the model to correct itself.
        """
        correction_prompt = self.correction_template.format(
            original_response=original_response
        )

        try:
            response = self.model.generate_content(correction_prompt)
            corrected_response = response.text.strip()

            logger.info(f"Self-correction attempt: {corrected_response[:200]}...")

            # Try to parse the corrected response
            json_match = re.search(r"\[.*\]", corrected_response, re.DOTALL)
            if json_match:
                locations_json = json_match.group()
                locations_data = json.loads(locations_json)

                extracted_locations = []
                for loc_data in locations_data:
                    try:
                        if isinstance(loc_data, dict):
                            extracted_locations.append(ExtractedLocation(**loc_data))
                    except Exception as e:
                        logger.error(
                            f"Self-correction still failed for {loc_data}: {e}"
                        )
                        continue

                if extracted_locations:
                    logger.info(
                        f"Self-correction successful: {len(extracted_locations)} locations"
                    )
                    return extracted_locations

            logger.warning("Self-correction failed to produce valid JSON")
            return []

        except Exception as e:
            logger.error(f"Self-correction attempt failed: {e}")
            return []
