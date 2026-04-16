import openai
from app.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

LANGUAGE_MAP = {
    "ta": "tamil",
    "hi": "hindi",
    "en": "english",
}


def transcribe_audio(audio_url: str, language: str = "en") -> dict:
    """
    Transcribe audio from URL using Whisper API.
    Returns transcription text and detected language.
    """
    import httpx, tempfile, os

    with httpx.Client() as http:
        response = http.get(audio_url)
        response.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language if language != "en" else None,
                response_format="verbose_json",
            )
        return {
            "text": transcript.text,
            "language": transcript.language,
            "duration": transcript.duration,
        }
    finally:
        os.unlink(tmp_path)


def translate_to_english(text: str, source_language: str) -> str:
    """Translate symptoms text to English for LLM processing."""
    if source_language == "en":
        return text

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a medical translator. Translate the following patient symptoms "
                    f"from {LANGUAGE_MAP.get(source_language, source_language)} to English. "
                    "Preserve all medical details accurately. Return only the translation."
                ),
            },
            {"role": "user", "content": text},
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()
