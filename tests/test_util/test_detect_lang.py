from lingua import Language
import pytest

from yanara.util.detect_lang import build_detector, detect_bulk, detect_from_file, detect_from_text


@pytest.fixture
def languages():
    """Fixture for supported languages."""
    return [Language.ENGLISH, Language.FRENCH, Language.SPANISH, Language.KOREAN, Language.JAPANESE]


@pytest.mark.unit
def test_detect_from_text_without_confidence(languages):
    """Test detection from a single text without confidence."""
    text = "Bonjour tout le monde"
    assert detect_from_text(text, languages) == "FRENCH"

    text = "Hello world"
    assert detect_from_text(text, languages) == "ENGLISH"

    text = "Hola mundo"
    assert detect_from_text(text, languages) == "SPANISH"

    text = "안녕하세요"
    assert detect_from_text(text, languages) == "KOREAN"

    text = "こんにちは"
    assert detect_from_text(text, languages) == "JAPANESE"

    text = ""
    assert detect_from_text(text, languages) == "Unknown"


@pytest.mark.unit
def test_detect_from_text_with_confidence(languages):
    """Test detection from a single text with confidence."""
    text = "Bonjour tout le monde"
    lang, confidence = detect_from_text(text, languages, confidence_threshold=0.7)
    assert lang == "FRENCH"
    assert confidence > 0.7

    text = ""
    lang, confidence = detect_from_text(text, languages, confidence_threshold=0.5)
    assert lang == "Unknown"
    assert confidence == 0.0


@pytest.mark.unit
def test_detect_bulk_without_confidence(languages):
    """Test bulk detection without confidence."""
    texts = [
        "Bonjour",
        "Hey",
        "Hola",
        "はじめまして",
        "",
    ]
    expected = ["FRENCH", "ENGLISH", "SPANISH", "JAPANESE", "Unknown"]
    assert detect_bulk(texts, languages) == expected


@pytest.mark.unit
def test_detect_bulk_with_confidence(languages):
    """Test bulk detection with confidence."""
    texts = ["Bonjour", "Hey", "Buenos días", "はじめまして", ""]
    results = detect_bulk(texts, languages, confidence_threshold=0.7)
    assert results[0][0] == "FRENCH" and results[0][1] > 0.7
    assert results[1][0] == "ENGLISH" and results[1][1] > 0.7
    assert results[2][0] == "SPANISH" and results[2][1] > 0.7
    assert results[3][0] == "JAPANESE" and results[3][1] > 0.7
    assert results[4] == ("Unknown", 0.0)


@pytest.mark.unit
def test_detect_from_file(tmp_path, languages):
    """Test detection from a file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("여러분, 안녕하세요", encoding="utf-8")

    assert detect_from_file(str(test_file), languages) == "KOREAN"

    # Test with confidence
    lang, confidence = detect_from_file(str(test_file), languages, confidence_threshold=0.5)
    assert lang == "KOREAN"
    assert confidence > 0.5


@pytest.mark.unit
def test_detect_from_file_not_found(languages):
    """Test detection with a non-existent file."""
    with pytest.raises(FileNotFoundError):
        detect_from_file("non_existent_file.txt", languages)


@pytest.mark.unit
def test_build_detector(languages):
    """Test building a detector."""
    detector = build_detector(languages)
    assert detector is not None

    with pytest.raises(ValueError):
        build_detector([])
