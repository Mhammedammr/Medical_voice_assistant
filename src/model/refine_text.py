import time
import logging
from .llm_service import LLMService
from ..core.config import Config

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RefineText:
    """Module for refining transcribed text using LLMService."""

    @staticmethod
    def refining_transcription(raw_text: str, language: str) -> str:
        """
        Refine a transcribed text depending on the language.

        Args:
            raw_text (str): The raw transcribed text.
            language (str): "ar" for Arabic, "en" for English, others fallback to English.

        Returns:
            str: Refined text.
        """
        if not raw_text or not isinstance(raw_text, str):
            raise ValueError("Input raw_text must be a non-empty string")

        refine_start = time.time()
        try:
            if language.lower() == "ar":
                refined_text = LLMService.refine_ar_transcription(
                    raw_text,
                    Config.REFINE_API_KEY                
                )
            else:
                refined_text = LLMService.refine_en_transcription(
                    raw_text,
                    Config.REFINE_API_KEY,
                )

            refine_time = time.time() - refine_start
            logger.info(f"[RefineText] Refinement completed in {refine_time:.2f}s")
            logger.debug(f"[RefineText] Output: {refined_text[:200]}...")  # truncate log preview

            return refined_text

        except Exception as e:
            logger.error(f"[RefineText] Refinement failed: {str(e)}")
            raise
