"""
Вспомогательные утилиты для парсинга документов.

Модуль содержит константы с регулярными выражениями для определения
заголовков глав и разделов в .docx документах, а также дополнительные
паттерны для обработки различных вариаций форматов нумерации.
"""

import re
from typing import Pattern


# Паттерны для поиска заголовков глав
# Паттерн для стандартного формата: 'Глава 1', 'Глава 2', 'Глава 10'
CHAPTER_PATTERN_1 = re.compile(r'^\s*Глава\s+\d+', re.IGNORECASE | re.MULTILINE)

# Паттерн для формата с точкой: 'Глава 1.', 'Глава 2.'
CHAPTER_PATTERN_2 = re.compile(r'^\s*Глава\s+\d+\.?', re.IGNORECASE | re.MULTILINE)

# Паттерн для формата 'ГЛАВА 1' (заглавными буквами)
CHAPTER_PATTERN_3 = re.compile(r'^\s*ГЛАВА\s+\d+', re.MULTILINE)

# Паттерн для формата '1. Глава', '2. Глава'
CHAPTER_PATTERN_4 = re.compile(r'^\s*\d+\.\s*Глава', re.IGNORECASE | re.MULTILINE)

# Паттерн для формата с римскими цифрами: 'Глава I', 'Глава II'
CHAPTER_PATTERN_5 = re.compile(r'^\s*Глава\s+[IVX]+', re.IGNORECASE | re.MULTILINE)

# Паттерн для формата 'Раздел 1', 'Раздел 2' (альтернативное название главы)
CHAPTER_PATTERN_6 = re.compile(r'^\s*Раздел\s+\d+', re.IGNORECASE | re.MULTILINE)

CHAPTER_PATTERNS: list[Pattern[str]] = [
    CHAPTER_PATTERN_1,
    CHAPTER_PATTERN_2,
    CHAPTER_PATTERN_3,
    CHAPTER_PATTERN_4,
    CHAPTER_PATTERN_5,
    CHAPTER_PATTERN_6,
]

# Паттерны для поиска заголовков разделов
# Паттерн для стандартного формата: '1.1.', '1.2.', '10.15.'
SECTION_PATTERN_1 = re.compile(r'^\s*\d+\.\d+\.?', re.MULTILINE)

# Паттерн для формата: '1.1', '2.3', '10.15' (без завершающей точки)
SECTION_PATTERN_2 = re.compile(r'^\s*\d+\.\d+', re.MULTILINE)

# Паттерн для трехуровневой нумерации: '1.1.1.', '2.3.5.'
SECTION_PATTERN_3 = re.compile(r'^\s*\d+\.\d+\.\d+\.?', re.MULTILINE)

# Паттерн для формата с буквами: '1.1.a', '2.3.b'
SECTION_PATTERN_4 = re.compile(r'^\s*\d+\.\d+\.[a-z]', re.IGNORECASE | re.MULTILINE)

# Паттерн для формата 'Раздел 1.1', 'Раздел 2.3'
SECTION_PATTERN_5 = re.compile(r'^\s*Раздел\s+\d+\.\d+', re.IGNORECASE | re.MULTILINE)

# Паттерн для формата 'Подраздел 1.1', 'Подраздел 2.3'
SECTION_PATTERN_6 = re.compile(r'^\s*Подраздел\s+\d+\.\d+', re.IGNORECASE | re.MULTILINE)

SECTION_PATTERNS: list[Pattern[str]] = [
    SECTION_PATTERN_1,
    SECTION_PATTERN_2,
    SECTION_PATTERN_3,
    SECTION_PATTERN_4,
    SECTION_PATTERN_5,
    SECTION_PATTERN_6,
]

# Дополнительные паттерны для специальных случаев
# Паттерн для нумерованных списков: '1)', '2)', '10)'
SPECIAL_PATTERN_1 = re.compile(r'^\s*\d+\)\s*$', re.MULTILINE)

# Паттерн для маркированных списков: '- ', '• ', '* '
SPECIAL_PATTERN_2 = re.compile(r'^\s*[-•*]\s+', re.MULTILINE)

# Паттерн для заголовков в верхнем регистре: 'ЗАГОЛОВОК', 'ЗАГЛАВИЕ'
SPECIAL_PATTERN_3 = re.compile(r'^\s*[А-ЯЁ\s]{5,}\s*$', re.MULTILINE)

SPECIAL_PATTERNS: list[Pattern[str]] = [
    SPECIAL_PATTERN_1,
    SPECIAL_PATTERN_2,
    SPECIAL_PATTERN_3,
]

# Основные константы для обратной совместимости
CHAPTER_PATTERN: Pattern[str] = CHAPTER_PATTERNS[0]
"""
Основной паттерн для поиска заголовков глав.
Соответствует формату: 'Глава 1', 'Глава 2', и т.д.
"""

SECTION_PATTERN: Pattern[str] = SECTION_PATTERNS[0]
"""
Основной паттерн для поиска заголовков разделов.
Соответствует формату: '1.1.', '1.2.', и т.д.
"""


def is_chapter(text: str) -> bool:
    """
    Проверяет, является ли текст заголовком главы.
    
    Args:
        text: Текст для проверки
        
    Returns:
        True, если текст соответствует одному из паттернов глав
    """
    text = text.strip()
    return any(pattern.match(text) for pattern in CHAPTER_PATTERNS)


def is_section(text: str) -> bool:
    """
    Проверяет, является ли текст заголовком раздела.
    
    Args:
        text: Текст для проверки
        
    Returns:
        True, если текст соответствует одному из паттернов разделов
    """
    text = text.strip()
    return any(pattern.match(text) for pattern in SECTION_PATTERNS)


def is_special_element(text: str) -> bool:
    """
    Проверяет, является ли текст специальным элементом (списком и т.д.).
    
    Args:
        text: Текст для проверки
        
    Returns:
        True, если текст соответствует одному из специальных паттернов
    """
    text = text.strip()
    return any(pattern.match(text) for pattern in SPECIAL_PATTERNS)


def extract_chapter_number(text: str) -> str | None:
    """
    Извлекает номер главы из текста заголовка.
    
    Args:
        text: Текст заголовка главы
        
    Returns:
        Номер главы как строка или None, если не удалось извлечь
    """
    text = text.strip()
    for pattern in CHAPTER_PATTERNS:
        match = pattern.match(text)
        if match:
            # Извлекаем первое число из совпадения
            numbers = re.findall(r'\d+', text)
            return numbers[0] if numbers else None
    return None


def extract_section_number(text: str) -> str | None:
    """
    Извлекает номер раздела из текста заголовка.
    
    Args:
        text: Текст заголовка раздела
        
    Returns:
        Номер раздела как строка или None, если не удалось извлечь
    """
    text = text.strip()
    for pattern in SECTION_PATTERNS:
        match = pattern.match(text)
        if match:
            # Извлекаем все числа из совпадения
            numbers = re.findall(r'\d+', text)
            return '.'.join(numbers) if numbers else None
    return None