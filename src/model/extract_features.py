import time
import logging
from .llm_service import LLMService
from ..core.config import Config

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtractFeature:
    """Module for extracting structured features from text using LLMService."""

    @staticmethod
    def extract(
        end_text: str,
        features: str,
    ) -> tuple[dict, str]:
        """
        Extract features from final translated text using LLM.

        Args:
            end_text (str): The translated text to process.
            features (str): The features/schema to extract (e.g., JSON schema or keys).

        Returns:
            tuple: (json_data: dict, reasoning: str)
        """
        if not end_text or not isinstance(end_text, str):
            raise ValueError("Input end_text must be a non-empty string")
        if not features or not isinstance(features, str):
            raise ValueError("Features must be a non-empty string")

        extraction_start = time.time()
        try:
            # Call LLMService to extract features
            features_output = LLMService.extract_features(
                translated_text=end_text,
                features=features,
                api_key=Config.EXTRACTION_API_KEY,
            )

            json_data = features_output.get("json_data", {})
            reasoning = features_output.get("reasoning", "")

            extraction_time = time.time() - extraction_start
            logger.info(f"[ExtractFeature] Extraction completed in {extraction_time:.2f}s")
            logger.debug(f"[ExtractFeature] Extracted features: {json_data}")
            logger.debug(f"[ExtractFeature] Reasoning: {reasoning[:200]}...")  # truncate preview

            return json_data, reasoning

        except Exception as e:
            logger.error(f"[ExtractFeature] Extraction failed: {str(e)}")
            raise