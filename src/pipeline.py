"""
Главный оркестратор пайплайна обработки документов.
Объединяет все фазы обработки в единый процесс.
"""

from typing import List
from src.schemas import Chunk
from src.processing.phase_1_converter import convert_docx_to_markdown
from src.processing.phase_2_parser import parse_markdown_to_chunks
from src.processing.phase_3_enricher import enrich_chunks_with_cross_references


def run_pipeline(docx_path: str) -> List[Chunk]:
    """
    Запускает полный пайплайн обработки документа.
    
    Эта функция является главным оркестратором, который последовательно
    вызывает все фазы обработки документа:
    1. Конвертация DOCX в Markdown
    2. Парсинг Markdown и структурный чанкинг
    3. Обогащение чанков перекрестными ссылками
    
    Args:
        docx_path: Путь к исходному DOCX файлу
        
    Returns:
        Список обработанных чанков с обогащенным контекстом и метаданными
    """
    # Шаг 1: Конвертация DOCX в Markdown
    doc_title, markdown_content = convert_docx_to_markdown(docx_path)
    
    # Шаг 2: Парсинг Markdown и создание структурированных чанков
    initial_chunks: List[Chunk] = parse_markdown_to_chunks(markdown_content, doc_title)
    
    # Шаг 3: Обогащение чанков перекрестными ссылками
    enriched_chunks: List[Chunk] = enrich_chunks_with_cross_references(initial_chunks)
    
    # Возврат финального результата
    return enriched_chunks


if __name__ == "__main__":
    # Базовая логика для тестирования
    print("Пайплайн обработки документов готов к запуску")
