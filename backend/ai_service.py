"""
EchoAid AI service — Groq (OpenAI-compatible API).

Accepts a list of word fragments and returns a small number of candidate
sentences suitable for text-to-speech communication.

The AI provider is entirely optional.  If AI_API_KEY is not configured,
the service returns an informative error without crashing the application.
Keyword-based communication is unaffected.
"""

import httpx

from backend.config import settings

SYSTEM_PROMPT = """\
You are a compassionate communication assistant helping a person with speech \
difficulties express themselves clearly.

The user will give you a small number of words or short fragments separated \
by commas or plus signs. Your job is to formulate 3 natural, polite, \
first-person sentences the person might want to say.

Rules:
- Write exactly 3 candidate sentences, each on its own line.
- Begin each sentence with a number and a period: "1. ", "2. ", "3. "
- Each sentence should be distinct in wording but convey the same core meaning.
- Write in the first person ("I", "I would like", "Could you please...").
- Keep sentences short, clear, and appropriate for everyday communication.
- Do NOT invent facts, medical symptoms, names, or events not implied by the fragments.
- Do NOT add commentary, explanations, or anything other than the 3 numbered sentences.
- If the fragments are too ambiguous, ask for clarification in one of the sentences.
"""


class AIServiceError(Exception):
    """Raised when the AI service fails for any reason."""


class AINotConfiguredError(AIServiceError):
    """Raised when no AI provider is configured."""


async def generate_suggestions(fragments: str) -> list[str]:
    """
    Call the Groq API and return up to 3 candidate sentences.

    Parameters
    ----------
    fragments : str
        Short words/fragments entered by the user, e.g. "cold + window + close"

    Returns
    -------
    list[str]
        A list of 1–3 candidate sentences.

    Raises
    ------
    AINotConfiguredError
        When AI_API_KEY is not set.
    AIServiceError
        On network, timeout, or API errors.
    """
    if not settings.ai_configured:
        raise AINotConfiguredError(
            "AI provider is not configured. "
            "Set AI_API_KEY in your .env file to enable this feature."
        )

    user_message = f"Word fragments: {fragments.strip()}"

    payload = {
        "model": settings.ai_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": settings.ai_max_tokens,
        "temperature": 0.4,
        "n": 1,
    }

    headers = {
        "Authorization": f"Bearer {settings.ai_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post(
                f"{settings.ai_provider_url}/chat/completions",
                json=payload,
                headers=headers,
            )
    except httpx.TimeoutException:
        raise AIServiceError(
            "The AI request timed out. Please try again or use your saved phrases."
        )
    except httpx.RequestError as exc:
        raise AIServiceError(
            f"Could not reach the AI provider: {exc}"
        )

    if response.status_code == 401:
        raise AIServiceError("AI API key is invalid or expired. Check your .env configuration.")
    if response.status_code == 429:
        raise AIServiceError("AI rate limit reached. Please wait a moment and try again.")
    if not response.is_success:
        raise AIServiceError(
            f"AI provider returned an error ({response.status_code}). "
            "Please try again or use your saved phrases."
        )

    try:
        data = response.json()
        raw_text: str = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError) as exc:
        raise AIServiceError(f"Unexpected AI response format: {exc}")

    return _parse_suggestions(raw_text)


def _parse_suggestions(text: str) -> list[str]:
    """
    Extract numbered sentences from the model's output.
    Falls back to splitting by newline if no numbers are found.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    suggestions = []

    for line in lines:
        # Strip leading "1. ", "2. " etc.
        for prefix in ("1. ", "2. ", "3. ", "1) ", "2) ", "3) "):
            if line.startswith(prefix):
                line = line[len(prefix):]
                break
        if line:
            suggestions.append(line)

    # Return at most 3, at least 1
    result = suggestions[:3]
    return result if result else [text[:500]]  # fallback: return raw truncated
