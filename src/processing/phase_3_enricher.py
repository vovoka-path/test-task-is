"""
Фаза 3: Обогащение контекстом.
Добавляет перекрестные ссылки и контекстную информацию в чанки.
"""

from typing import List, Dict
import re
from src.schemas import Chunk
from src.utils.regex_patterns import CROSS_REFERENCE_PATTERN


def enrich_chunks_with_cross_references(chunks: List[Chunk]) -> List[Chunk]:
    """
    Обогащает чанки контекстом из перекрестных ссылок.
    
    Данная функция предназначена для добавления перекрестных ссылок и
    контекстной информации в обработанные чанки. Она анализирует связи
    между различными частями документа и обогащает каждый чанк
    информацией, которая поможет лучше понять контекст.
    
    Args:
        chunks: Список исходных чанков для обогащения
        
    Returns:
        Список обогащенных чанков с добавленными перекрестными ссылками
        и контекстной информацией
    """
    # Проход 1: Создание карты пунктов для последующего поиска перекрестных ссылок
    clause_map: Dict[str, str] = {}
    
    # Итерируем по всем чанкам и создаем словарь соответствий номер пункта -> текст пункта
    for chunk in chunks:
        clause_number = chunk.metadata.clause_number
        clause_text = chunk.page_content
        clause_map[clause_number] = clause_text
    
    # Проход 2: Поиск перекрестных ссылок в каждом чанке
    for chunk in chunks:
        # Ищем все номера пунктов, на которые ссылается текущий чанк
        # CROSS_REFERENCE_PATTERN ищет упоминания вида "пункт 1.2", "пункта 1.2.3" и т.д.
        found_references = re.findall(CROSS_REFERENCE_PATTERN, chunk.page_content)

        # Обрабатываем каждую найденную ссылку
        for reference_number in found_references:
            # reference_number уже является строкой с номером пункта (например, "3.1.9")

            # Проверяем, что чанк не ссылается сам на себя
            if reference_number != chunk.metadata.clause_number:
                # Извлекаем текст ссылки из исходного текста
                link_pattern = re.compile(rf'\b(?:пункт|подпункт)[а-я]{0,2}\s+{re.escape(reference_number)}\b')
                link_match = re.search(link_pattern, chunk.page_content)
                link_text = link_match.group() if link_match else reference_number

                # Добавляем запись в cross_references с текстом ссылки
                chunk.metadata.cross_references[reference_number] = link_text
        
    return chunks
