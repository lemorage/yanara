from typing import List, Tuple, Union

from lingua import Language, LanguageDetectorBuilder


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


def detect_from_text(text: str, detector, confidence_threshold: float = None) -> Union[str, Tuple[str, float]]:
    """
    Detect the language from a single text with optional confidence.

    Args:
        text (str): Input text.
        detector: Prebuilt language detector.
        confidence_threshold (float): Confidence threshold (optional).

    Returns:
        Union[str, Tuple[str, float]]:
            Detected language name or (language, confidence) tuple if threshold is set.
    """
    if not text.strip():
        return "Unknown" if confidence_threshold is None else ("Unknown", 0.0)

    if confidence_threshold is None:
        detected_language = detector.detect_language_of(text)
        return detected_language.name if detected_language else "Unknown"

    confidence_values = detector.compute_language_confidence_values(text)
    if confidence_values:
        # Find the top language by maximum confidence
        top_confidence = max(confidence_values, key=lambda c: c.value)
        return (
            (top_confidence.language.name, top_confidence.value)
            if top_confidence.value >= confidence_threshold
            else ("Unknown", 0.0)
        )
    return "Unknown", 0.0


def detect_from_file(file_path: str, detector, confidence_threshold: float = None) -> Union[str, Tuple[str, float]]:
    """
    Detect the language from text in a file.

    Args:
        file_path (str): Path to the file containing text.
        detector: Prebuilt language detector.
        confidence_threshold (float): Confidence threshold (optional).

    Returns:
        Union[str, Tuple[str, float]]:
            Detected language name or (language, confidence) tuple if threshold is set.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return detect_from_text(text, detector, confidence_threshold)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file: {e}")


def detect_bulk(
    texts: List[str], detector, confidence_threshold: float = None
) -> Union[List[str], List[Tuple[str, float]]]:
    """
    Detect languages for multiple texts in bulk.

    Args:
        texts (list[str]): List of texts.
        detector: Prebuilt language detector.
        confidence_threshold (float): Confidence threshold (optional).

    Returns:
        Union[List[str], List[Tuple[str, float]]]:
            List of detected languages or (language, confidence) tuples if threshold is set.
    """
    return [detect_from_text(text, detector, confidence_threshold) for text in texts]


if __name__ == "__main__":
    languages = [Language.ENGLISH, Language.FRENCH, Language.SPANISH]
    detector = build_detector(languages)

    # Single detection
    text = "Bonjour tout le monde"
    print(detect_from_text(text, detector))  # Output: FRENCH

    # Single detection with confidence
    print(detect_from_text(text, detector, confidence_threshold=0.7))  # Output: ('FRENCH', confidence)

    # Bulk detection
    texts = ["Hello world", "Hola mundo", "Bonjour tout le monde"]
    print(detect_bulk(texts, detector))  # Output: ['ENGLISH', 'SPANISH', 'FRENCH']

    # Bulk detection with confidence
    print(detect_bulk(texts, detector, confidence_threshold=0.7))
    # Output: [('ENGLISH', confidence), ('SPANISH', confidence), ('FRENCH', confidence)]

    # File detection
    try:
        print(detect_from_file("example.txt", detector))  # Output: Detected language
    except Exception as e:
        print(e)
