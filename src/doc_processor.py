"""
Основной класс для обработки и парсинга .docx документов.

Модуль содержит класс DocumentProcessor, который отвечает за загрузку,
анализ и разбиение документов на структурированные фрагменты (chunks).
Класс реализует конечный автомат состояний для отслеживания текущего
контекста документа (главы и разделы).
"""

import os
from typing import Optional, List, Any, Dict
from docx import Document

from .chunk import Chunk


class DocumentProcessor:
    """Основной парсер документов для извлечения структурированных фрагментов.
    
    Класс DocumentProcessor предназначен для обработки .docx файлов и их
    разбиения на логические фрагменты (chunks) с сохранением иерархической
    структуры документа.
    
    Класс реализует конечный автомат состояний для отслеживания текущего
    контекста (главы и разделы) во время обработки документа.
    
    Attributes:
        file_path (str): Путь к обрабатываемому .docx файлу
        _document (Optional[Document]): Загруженный документ или None, если не загружен
        current_chapter (Optional[str]): Номер текущей главы
        current_section (Optional[str]): Номер текущего раздела
    """
    
    def __init__(self, file_path: str) -> None:
        """Инициализирует процессор документов.
        
        Args:
            file_path: Путь к .docx файлу для обработки
        """
        self.file_path = file_path
        self._document: Optional[Any] = None
        self.current_chapter: Optional[str] = None
        self.current_section: Optional[str] = None
    
    def process(self) -> List[Chunk]:
        """Основной метод обработки документа.
        
        Метод оркестрирует весь процесс парсинга документа, включая:
        - Загрузку .docx файла
        - Итерацию по элементам документа
        - Определение типа каждого элемента
        - Создание структурированных фрагментов (chunks)
        
        Returns:
            Список объектов Chunk, представляющих фрагменты документа
        """
        # Загружаем документ
        self._load_document()
        
        # Проверяем, что документ успешно загружен
        if self._document is None:
            raise Exception("Не удалось загрузить документ")
        
        # Создаем список для хранения результатов
        chunks: List[Chunk] = []
        
        # Получаем имя файла без расширения для метаданных
        source_document = os.path.splitext(os.path.basename(self.file_path))[0]
        
        try:
            # Итерируемся по элементам документа в правильном порядке
            # Используем iter_inner_content() для получения Paragraph и Table объектов
            for element in self._document.iter_inner_content():
                # Проверяем тип элемента для корректной обработки
                from docx.text.paragraph import Paragraph
                from docx.table import Table
                
                if isinstance(element, Paragraph):
                    # Обрабатываем параграф - извлекаем текст
                    text = element.text.strip()
                    
                    # Пропускаем пустые параграфы
                    if not text:
                        continue
                    
                    # Проверяем, является ли текст заголовком главы
                    if self._is_chapter(text):
                        # Обновляем состояние текущей главы
                        chapter_number = self._extract_chapter_number(text)
                        if chapter_number:
                            self.current_chapter = chapter_number
                            continue  # Заголовки глав не создают чанки
                    
                    # Проверяем, является ли текст заголовком раздела
                    if self._is_section(text):
                        # Обновляем состояние текущего раздела
                        section_number = self._extract_section_number(text)
                        if section_number:
                            self.current_section = section_number
                            continue  # Заголовки разделов не создают чанки
                    
                    # Если текст не является заголовком и не пустой, создаем чанк
                    if text:
                        # Создаем метаданные для чанка
                        metadata: Dict[str, Any] = {
                            "source_document": source_document,
                            "chapter": self.current_chapter,
                            "section": self.current_section
                        }
                        
                        # Создаем объект Chunk
                        chunk = Chunk(content=text, metadata=metadata)
                        chunks.append(chunk)
                
                elif isinstance(element, Table):
                    # Выводим предупреждение для таблиц согласно ТЗ
                    print(f"WARNING: Table found and ignored in document {source_document}")
                    continue  # Пропускаем таблицы
                
                else:
                    # Для других типов элементов выводим предупреждение
                    element_type = type(element).__name__
                    print(f"WARNING: Unsupported element type '{element_type}' found and ignored in document {source_document}")
                    continue
                    
        except Exception as e:
            raise Exception(f"Ошибка при обработке документа: {e}")
        
        # Возвращаем список созданных чанков
        return chunks
    
    def _is_chapter(self, text: str) -> bool:
        """Проверяет, является ли текст заголовком главы.
        
        Args:
            text: Текст для проверки
            
        Returns:
            True, если текст является заголовком главы
        """
        from . import utils
        return utils.is_chapter(text)
    
    def _is_section(self, text: str) -> bool:
        """Проверяет, является ли текст заголовком раздела.
        
        Args:
            text: Текст для проверки
            
        Returns:
            True, если текст является заголовком раздела
        """
        from . import utils
        return utils.is_section(text)
    
    def _extract_chapter_number(self, text: str) -> str | None:
        """Извлекает номер главы из текста заголовка.
        
        Args:
            text: Текст заголовка главы
            
        Returns:
            Номер главы как строка или None, если не удалось извлечь
        """
        from . import utils
        return utils.extract_chapter_number(text)
    
    def _extract_section_number(self, text: str) -> str | None:
        """Извлекает номер раздела из текста заголовка.
        
        Args:
            text: Текст заголовка раздела
            
        Returns:
            Номер раздела как строка или None, если не удалось извлечь
        """
        from . import utils
        return utils.extract_section_number(text)
    
    def _load_document(self) -> None:
        """Загружает .docx файл в память.
        
        Метод проверяет существование файла и загружает его
        с помощью библиотеки python-docx.
        
        Raises:
            FileNotFoundError: Если указанный файл не существует
            Exception: При ошибках загрузки документа
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Документ не найден: {self.file_path}")
        
        try:
            self._document = Document(self.file_path)
        except Exception as e:
            raise Exception(f"Ошибка при загрузке документа {self.file_path}: {e}")