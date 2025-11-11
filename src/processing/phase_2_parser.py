"""
Фаза 2: Парсинг Markdown и структурный чанкинг (новая версия).
Разделяет текст на логические чанки согласно структуре документа.
"""

import re
from typing import List, Tuple
from src.schemas import Chunk, ChunkMetadata

def extract_document_titles(markdown_text: str) -> Tuple[str, str]:
    """
    Извлекает общее и короткое название документа из начала текста.
    
    Args:
        markdown_text: Исходный Markdown текст документа
        
    Returns:
        Кортеж из двух строк: (общее_название, короткое_название)
        Если паттерн не найден, возвращает ("", "")
    """
    lines = markdown_text.strip().split('\n')
    
    # Ищем название документа в специальном формате
    # Обычно это строки типа "ПРАВИЛА № X" или "ПОЛОЖЕНИЕ О..."
    for i, line in enumerate(lines):
        line = line.strip()
        # Ищем строки с номером правил
        if re.match(r'ПРАВИЛА\s+№\s+\d+', line, re.IGNORECASE):
            # Берем эту строку и следующие строки для полного названия
            full_title_parts = [line]
            
            # Проверяем следующие строки - до 3 строк или до служебной строки
            for j in range(i + 1, min(i + 4, len(lines))):
                next_line = lines[j].strip()
                # Проверяем, что строка не начинается с #, не является номером пункта
                if (not next_line.startswith('#') and
                    not re.match(r'^\d+\.', next_line) and
                    not re.match(r'^\(', next_line) and  # не комментарий в скобках
                    not re.match(r'^Правила в редакции', next_line) and  # не служебная строка
                    not re.match(r'^Согласованы', next_line) and  # не служебная строка
                    not re.match(r'^Глава', next_line) and  # не начало главы
                    len(next_line) > 3):  # минимальная длина
                    full_title_parts.append(next_line)
                elif (next_line.startswith('#') or
                      re.match(r'^\d+\.', next_line) or
                      re.match(r'^\(', next_line) or
                      re.match(r'^Правила в редакции', next_line) or
                      re.match(r'^Согласованы', next_line) or
                      re.match(r'^Глава', next_line)):
                    # Служебная строка - останавливаемся
                    break
                # Пропускаем пустые строки и продолжаем
            
            full_title = ' '.join(full_title_parts)
            # Создаем короткое название (первые 50 символов)
            short_title = full_title[:50] + "..." if len(full_title) > 50 else full_title
            return (full_title, short_title)
    
    # Если специальный формат не найден, ищем общие паттерны
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # Проверяем, может ли это быть названием документа
            if any(keyword in line.upper() for keyword in ['ПРАВИЛА', 'ПОЛОЖЕНИЕ', 'ПРИКАЗ', 'УКАЗ']):
                full_title = line
                # Создаем короткое название (первые 50 символов)
                short_title = full_title[:50] + "..." if len(full_title) > 50 else full_title
                return (full_title, short_title)
            break
    
    return ("", "")

def parse_markdown_to_chunks(markdown_text: str, document_title: str = "") -> List[Chunk]:
    """
    Парсит Markdown текст и создает структурированные чанки.
    
    Args:
        markdown_text: Текст в формате Markdown
        document_title: Название документа (если не передано, будет извлечено из текста)
        
    Returns:
        Список чанков с извлеченными метаданными
    """
    # 1. Извлечение метаданных документа
    if document_title:
        full_title = document_title
        # Создаем короткое название из полного
        if "ПРАВИЛА №" in full_title:
            # Извлекаем только номер правил
            match = re.search(r'ПРАВИЛА №\s*\d+', full_title, re.IGNORECASE)
            short_title = match.group() if match else full_title[:50] + "..." if len(full_title) > 50 else full_title
        else:
            short_title = full_title[:50] + "..." if len(full_title) > 50 else full_title
    else:
        full_title, short_title = extract_document_titles(markdown_text)
        # Если полное название найдено, создаем короткое
        if full_title:
            if "ПРАВИЛА №" in full_title:
                match = re.search(r'ПРАВИЛА №\s*\d+', full_title, re.IGNORECASE)
                short_title = match.group() if match else full_title[:50] + "..." if len(full_title) > 50 else full_title
            else:
                short_title = full_title[:50] + "..." if len(full_title) > 50 else full_title
    
    # 2. Извлекаем все заголовки разделов из исходного текста
    section_headers: dict[str, str] = {}
    
    # Ищем заголовки в формате "Глава X. НАЗВАНИЕ" или "Раздел X. НАЗВАНИЕ"
    chapter_matches = re.findall(r'Глава\s+(\d+)\.\s+(.+?)(?:\n|$)', markdown_text, re.MULTILINE)
    for chapter_num, chapter_title in chapter_matches:
        section_headers[chapter_num] = f"{chapter_num}. {chapter_title.strip()}"
    
    # Ищем заголовки в формате "# X. НАЗВАНИЕ" (markdown)
    header_matches = re.findall(r'#\s+(\d+)\.\s+(.+?)(?:\n|$)', markdown_text, re.MULTILINE)
    for section_number, section_title in header_matches:
        section_headers[section_number] = f"{section_number}. {section_title.strip()}"
    
    # Ищем заголовки разделов где все слова написаны заглавными буквами
    for line in markdown_text.split('\n'):
        line = line.strip()
        # Проверяем строки, которые начинаются с номера и точки
        match = re.match(r'^(\d+)\.\s+(.+?)$', line)
        if match and not re.match(r'^\d+\.\d+', line):  # Исключаем номера пунктов
            section_num, section_title = match.groups()
            if section_title and len(section_title) > 3:  # Минимальная длина названия
                # Проверяем, что все слова в названии написаны заглавными буквами
                words = section_title.split()
                is_all_upper = True
                for word in words:
                    # Убираем пунктуацию
                    clean_word = re.sub(r'[^\w]', '', word)
                    if not clean_word:
                        continue
                    # Проверяем, что слово написано заглавными буквами
                    if not clean_word.isupper():
                        is_all_upper = False
                        break
                
                if is_all_upper:
                    section_headers[section_num] = f"{section_num}. {section_title.strip()}"
    
    # 3. Разделение на пункты и определение их принадлежности к разделам
    # Ищем все пункты в формате "X.Y. текст" или "X.Y.Z. текст"
    clause_pattern = r'(\d+)\.(\d+(?:\.\d+)*)\.\s+(.+?)(?=\n\s*\d+\.\d+(?:\.\d+)*\.|\n\s*#|\n\s*Глава|\Z)'
    clause_matches = re.findall(clause_pattern, markdown_text, re.DOTALL)
    
    chunks: List[Chunk] = []
    
    for section_num, clause_num, clause_content in clause_matches:
        # Определяем заголовок раздела
        current_section_title = section_headers.get(section_num, f"{section_num}. Раздел {section_num}")
        
        # Очищаем содержимое от лишних переносов и пробелов
        content = re.sub(r'\n+', ' ', clause_content.strip())
        
        # Создаем полный номер пункта
        full_clause_number = f"{section_num}.{clause_num}"
        
        # Создаем метаданные
        metadata = ChunkMetadata(
            source_document_title=full_title,
            short_document_title=short_title,
            clause_number=full_clause_number,
            parent_section_title=current_section_title,
            hierarchy=[short_title, current_section_title, full_clause_number],
            cross_references={}
        )
        
        # Создаем чанк
        chunk = Chunk(
            page_content=content,
            metadata=metadata
        )
        
        chunks.append(chunk)
    
    return chunks