"""
语言检测模块 - 第一版

本模块提供基于文件扩展名的简单语言检测能力。
未来可以扩展为基于内容、shebang 或其它启发式方法的更复杂检测器。
"""

from repoguide.core.language.language_detector import LanguageDetector

__all__ = ["LanguageDetector"]