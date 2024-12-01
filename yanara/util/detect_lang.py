from typing import List, Tuple, Union

from lingua import Language, LanguageDetectorBuilder

# Current languages supported by the agents
LANGUAGES: List[Language] = [Language.ENGLISH, Language.CHINESE, Language.JAPANESE]


def build_detector(languages: List[Language]):
    """
    Build and return a language detector instance.

    Args:
        languages (list[Language]): List of supported languages.

    Returns:
        LanguageDetector: A configured language detector instance.
    """
    if not languages:
        raise ValueError("Languages list cannot be empty.")
    return LanguageDetectorBuilder.from_languages(*languages).build()


def detect_from_text(
    text: str, languages: List[Language], confidence_threshold: float = None
) -> Union[str, Tuple[str, float]]:
    """
    Detect the language from a single text with optional confidence.

    Args:
        text (str): Input text.
        languages (list[Language]): List of supported languages.
        confidence_threshold (float): Confidence threshold (optional).

    Returns:
        Union[str, Tuple[str, float]]:
            Detected language name or (language, confidence) tuple if threshold is set.
    """
    detector = build_detector(languages)

    if not text.strip():
        return "Unknown" if confidence_threshold is None else ("Unknown", 0.0)

    if confidence_threshold is None:
        detected_language = detector.detect_language_of(text)
        return detected_language.name if detected_language else "Unknown"

    # Compute language confidence values (guaranteed to be non-empty)
    confidence_values = detector.compute_language_confidence_values(text)
    top_confidence = max(confidence_values, key=lambda c: c.value)
    return (
        (top_confidence.language.name, top_confidence.value)
        if top_confidence.value >= confidence_threshold
        else ("Unknown", 0.0)
    )


def detect_from_file(
    file_path: str, languages: List[Language], confidence_threshold: float = None
) -> Union[str, Tuple[str, float]]:
    """
    Detect the language from text in a file.

    Args:
        file_path (str): Path to the file containing text.
        languages (list[Language]): List of supported languages.
        confidence_threshold (float): Confidence threshold (optional).

    Returns:
        Union[str, Tuple[str, float]]:
            Detected language name or (language, confidence) tuple if threshold is set.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return detect_from_text(text, languages, confidence_threshold)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file: {e}")


def detect_bulk(
    texts: List[str], languages: List[Language], confidence_threshold: float = None
) -> Union[List[str], List[Tuple[str, float]]]:
    """
    Detect languages for multiple texts in bulk.

    Args:
        texts (list[str]): List of texts.
        languages (list[Language]): List of supported languages.
        confidence_threshold (float): Confidence threshold (optional).

    Returns:
        Union[List[str], List[Tuple[str, float]]]:
            List of detected languages or (language, confidence) tuples if threshold is set.
    """
    return [detect_from_text(text, languages, confidence_threshold) for text in texts]
