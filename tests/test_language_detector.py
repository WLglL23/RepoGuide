from repoguide.core.language.language_detector import LanguageDetector


def test_detect_python_file():
    assert LanguageDetector.detect("src/main.py") == "python"


def test_detect_java_file():
    assert LanguageDetector.detect("src/main/java/App.java") == "java"


def test_detect_unknown_file():
    assert LanguageDetector.detect("Dockerfile") == "unknown"


def test_detect_by_extension_without_dot():
    assert LanguageDetector.detect_by_extension("py") == "python"


def test_supported_extensions_contains_py():
    assert ".py" in LanguageDetector.supported_extensions()