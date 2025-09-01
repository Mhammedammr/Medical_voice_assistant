import fireworks.client
import logging
import json
from typing import Optional, Type
from pydantic import BaseModel, ValidationError

from .utils import prompt as prompt_utils

# ---------------- Logger ---------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- Pydantic Models ---------------- #
class ExtractedFeatures(BaseModel):
    json_data: dict
    reasoning: str

# ---------------- LLM Service ---------------- #
class LLMService:
    """Service wrapper around Fireworks LLM API for refinement, translation, and extraction."""

    # --- Public APIs --- #
    @staticmethod
    def refine_en_transcription(raw_text: str, api_key: str):
        return LLMService.process_text(
            text=raw_text, api_key=api_key, model="deepseek",
            prompt_type="refine_english"
        )

    @staticmethod
    def refine_ar_transcription(raw_text: str, api_key: str):
        return LLMService.process_text(
            text=raw_text, api_key=api_key, model="deepseek",
            prompt_type="refine_arabic"
        )

    @staticmethod
    def translate_to_eng(refined_text: str, api_key: str):
        return LLMService.process_text(
            text=refined_text, api_key=api_key, model="deepseek",
            prompt_type="translate"
        )

    @staticmethod
    def extract_features(translated_text: str, features: list, api_key: str):
        return LLMService.process_text(
            text=translated_text, api_key=api_key, model="llama",
            prompt_type="extract_dynamic", features=features, pydantic_model=ExtractedFeatures
        )

    # --- Core Logic --- #
    @staticmethod
    def process_text(
        text: str,
        api_key: str,
        model: str,
        prompt_type: str,
        features: Optional[list] = None,
        pydantic_model: Optional[Type[BaseModel]] = None,
    ):
        """Generic method to process text with LLM (refine, translate, extract)."""
        fireworks.client.api_key = api_key
        if model == "deepseek":
            model_account = "accounts/fireworks/models/deepseek-v3"
        else:
            model_account = "accounts/fireworks/models/llama4-maverick-instruct-basic"


        # Final prompt
        prompt = LLMService._get_prompt(
            prompt_type, text, features
        )
        logger.debug(f"Generated prompt: {prompt}")

        # Call LLM
        result = LLMService._call_llm_api(
            model_account=model_account,
            prompt=prompt,
            pydantic_model=pydantic_model,
        )

        return result if result else text

    # --- Private Helpers --- #
    @staticmethod
    def _get_prompt(prompt_type: str, text: str, features: Optional[list]):
        """Select prompt dynamically from utils.prompt."""
        mapping = {
            # --- English Refinement ---
            ("refine_english"): prompt_utils.get_refine_english_prompt_deepseek,

            # --- Arabic Refinement ---
            ("refine_arabic"): prompt_utils.get_refine_arabic_prompt_deepseek,

            # --- Translation ---
            ("translate"): prompt_utils.get_translation_prompt_deepseek,

            # --- Extraction ---
            ("extract"): prompt_utils.get_extraction_prompt_llama,
            ("extract_dynamic"): lambda t: prompt_utils.get_dynamic_extraction_prompt_llama(t, features),
        }

        key = (prompt_type)
        func = mapping.get(key)

        if func is None:
            raise ValueError(f"Unsupported prompt type={prompt_type}")

        return func(text)

    @staticmethod
    def _call_llm_api(model_account: str, prompt: str, pydantic_model: Optional[Type[BaseModel]] = None, temperature: float = 0.3):
        """Fireworks API call wrapper with optional structured output parsing."""
        try:
            logger.info(f"Calling LLM API -> model: {model_account}")

            params = {
                "model": model_account,
                "prompt": prompt,
                "max_tokens": 2000,
                "temperature": temperature,
            }

            # Structured output
            if pydantic_model:
                params["response_format"] = {"type": "json_object", "schema": pydantic_model.schema()}

            response = fireworks.client.Completion.create(**params)

            if not response.choices or not response.choices[0].text.strip():
                logger.warning("LLM returned empty response")
                return None

            raw_output = response.choices[0].text.strip()

            # Parse JSON if structured
            if pydantic_model:
                try:
                    parsed_output = json.loads(raw_output)
                    validated_output = pydantic_model(**parsed_output)
                    return validated_output.dict()
                except (json.JSONDecodeError, ValidationError) as e:
                    logger.error(f"Structured output validation failed: {e}")
                    return None

            return raw_output

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return None
