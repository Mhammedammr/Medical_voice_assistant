import time
import logging
from .llm_service import LLMService
from ..core.config import Config

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Translate:
    """Module for translating refined text into English using LLMService."""

    @staticmethod
    def translate(refined_text: str) -> str:
        """
        Translate refined text into English.

        Args:
            refined_text (str): The text after refinement.

        Returns:
            str: Translated English text.
        """
        if not refined_text or not isinstance(refined_text, str):
            raise ValueError("Input refined_text must be a non-empty string")

        translation_start = time.time()
        try:
            translated_text = LLMService.translate_to_eng(
                refined_text,
                Config.TRANSLATE_API_KEY,
            )

            translation_time = time.time() - translation_start
            logger.info(f"[Translate] Translation completed in {translation_time:.2f}s")
            logger.debug(f"[Translate] Output: {translated_text[:200]}...")  # log preview

            return translated_text

        except Exception as e:
            logger.error(f"[Translate] Translation failed: {str(e)}")
            raise
