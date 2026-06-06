"""
summarizer.py — AI-Powered Document Summarization
Powered by: Google Gemini API
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional document analyst. 
When given document text, produce a clear, well-structured summary.

Your summary MUST:
- Be 5–10 sentences long
- Capture the main purpose, key points, and any conclusions
- Be written in plain, professional English
- Avoid bullet points — use flowing prose paragraphs
- NOT mention that you are an AI or that you received a document
- NO asterisks, NO markdown, NO draft markers
- NO internal thoughts, planning, or "Drafting Sentence X:" labels
- Just provide the summary text directly

Return ONLY the final summary. Nothing else."""


class Summarizer:
    """
    Summarizes document text using Google Gemini API.
    """

    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")
        self.model_gemini = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        self.max_tokens = int(os.environ.get("SUMMARY_MAX_TOKENS", "600"))

    # ────────────────────────────────────────────
    # Public interface
    # ────────────────────────────────────────────

    def summarize(self, text: str, filename: str = "") -> str:
        """
        Generate a 5–10 sentence summary of the given text using Gemini API.
        """
        user_msg = self._build_prompt(text, filename)

        try:
            raw_response = self._call_gemini(user_msg)
            cleaned_response = self._clean_response(raw_response)
            
            # Check if response ends properly (detection of truncation)
            if cleaned_response and not cleaned_response.rstrip().endswith(('.', '!', '?')):
                logger.warning(f"Summary for '{filename}' may be truncated: {len(cleaned_response)} chars, no period at end")
            
            logger.info(f"Summary for '{filename}': {len(cleaned_response)} chars")
            return cleaned_response
        except Exception as err:
            logger.error("Gemini API failed: %s", err)
            return (
                f"Summary unavailable — AI service error. "
                f"Details: {str(err)}"
            )

    # ────────────────────────────────────────────
    # Gemini API implementation
    # ────────────────────────────────────────────

    def _clean_response(self, response: str) -> str:
        """Remove markdown formatting and drafting markers from API response."""
        import re
        
        # Remove "*Drafting Sentence X:*" markers
        response = re.sub(r'\*\s*Drafting Sentence \d+:\s*\*', '', response)
        
        # Remove other common drafting markers
        response = re.sub(r'\*\*.*?Sentence \d+.*?\*\*', '', response)
        response = re.sub(r'^\*\*.*?\*\*\s*', '', response, flags=re.MULTILINE)
        
        # Remove markdown bold/italic that shouldn't be there
        response = re.sub(r'\*\*', '', response)
        response = re.sub(r'(?<!\*)\*(?!\*)', '', response)  # Single asterisks only if not part of **
        
        # Clean up extra whitespace
        response = re.sub(r'\n\n+', '\n\n', response)
        response = response.strip()
        
        return response

    def _call_gemini(self, user_msg: str) -> str:
        """Call Google Gemini API."""
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Run: pip install google-generativeai")

        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY not set in environment.")

        genai.configure(api_key=self.gemini_key)
        model = genai.GenerativeModel(
            model_name=self.model_gemini,
        )

        # SDK type stubs may not expose `system_instruction`.
        # To keep behavior, prepend our system prompt to the user message.
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_msg}"

        response = model.generate_content(
            full_prompt,

            generation_config=genai.types.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=0.7,  # Balanced: creative but coherent
            ),
        )
        
        # Check for valid response
        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")
        
        # Log raw response for debugging
        raw_text = response.text.strip()
        logger.debug(f"RAW API RESPONSE: {raw_text[:200]}...")
        
        # Check for incomplete generation (most reliable indicator)
        finish_reason = getattr(response, 'finish_reason', None)
        if finish_reason == 'MAX_TOKENS':
            logger.error(
                f"CRITICAL: Response hit max tokens limit ({self.max_tokens}). "
                f"Got {len(raw_text)} chars before being cut off. "
                f"Increase SUMMARY_MAX_TOKENS in .env immediately!"
            )
        elif finish_reason and finish_reason != 'STOP':
            logger.warning(f"API finish reason: {finish_reason} (expected STOP)")
        
        # Check for safety-blocked content
        prompt_feedback = getattr(response, 'prompt_feedback', None)
        if prompt_feedback and hasattr(prompt_feedback, 'block_reason'):
            if prompt_feedback.block_reason:
                logger.warning(f"Content safety filter triggered: {prompt_feedback.block_reason}")
        
        return raw_text

    # ────────────────────────────────────────────
    # Prompt construction
    # ────────────────────────────────────────────

    def _build_prompt(self, text: str, filename: str) -> str:
        header = f'Document: "{filename}"\n\n' if filename else ""
        # Truncate very long texts to keep within token limits
        safe_text = text[:12_000]
        if len(text) > 12_000:
            safe_text += "\n\n[... document truncated for summarization ...]"
        return f"{header}---\n{safe_text}\n---"
