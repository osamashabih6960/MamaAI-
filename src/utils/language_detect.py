from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    """
    Detect if input is Arabic ('ar') or English ('en').
    Defaults to 'en' if unsure.
    """
    try:
        lang = detect(text)
        if lang == "ar":
            return "ar"
        return "en"
    except LangDetectException:
        return "en"


def get_response_language_instruction(lang: str) -> str:
    """
    Returns a prompt instruction to respond in detected language + always bilingual.
    """
    if lang == "ar":
        return (
            "The user wrote in Arabic. "
            "Respond with BOTH Arabic and English versions clearly labeled. "
            "Arabic must read as native copy, not a translation."
        )
    return (
        "The user wrote in English. "
        "Respond with BOTH English and Arabic versions clearly labeled. "
        "Arabic must read as native copy, not a translation."
    )