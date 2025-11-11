"""
Пользовательские исключения для пайплайна обработки документов.
"""

class DocumentProcessingError(Exception):
    """Базовый класс исключений обработки документов."""
    pass


class PandocNotInstalledError(DocumentProcessingError):
    """Исключение, возникающее при отсутствии Pandoc в системе."""
    pass


class InvalidDocumentFormatError(DocumentProcessingError):
    """Исключение для некорректного формата документа."""
    pass


class ParsingError(DocumentProcessingError):
    """Исключение при ошибке парсинга документа."""
    pass
