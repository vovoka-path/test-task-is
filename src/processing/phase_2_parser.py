"""
Фаза 2: Парсинг Markdown и структурный чанкинг (новая версия).
Разделяет текст на логические чанки согласно структуре документа.
"""

import re
from typing import List, Tuple, Dict, Any
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
    # Обрабатываем все форматы нумерации в документе

    def get_line_num_from_pos(pos: int, text: str) -> int:
        lines = text.split('\n')
        current_pos = 0
        for i, line in enumerate(lines):
            line_len = len(line) + 1  # +1 for \n
            if current_pos <= pos < current_pos + line_len:
                return i
            current_pos += line_len
        return len(lines) - 1

    def get_chapter_num_by_position(line_num: int, chapter_boundaries: Dict[str, Dict[str, Any]]) -> str:
        chapter_num = None
        for ch_num, ch_info in sorted(chapter_boundaries.items(), key=lambda x: x[1]['start_line'], reverse=True):
            if ch_info['start_line'] <= line_num:
                chapter_num = ch_num
                break
        return chapter_num or '1'

    chunks: List[Chunk] = []
    processed_clauses: set[str] = set()  # Для избежания дублирования

    # Определяем границы глав для правильной привязки пунктов к разделам
    chapter_boundaries: Dict[str, Dict[str, Any]] = {}

    # Находим границы глав
    lines = markdown_text.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        # Ищем заголовки глав
        chapter_match = re.match(r'Глава\s+(\d+)\.\s+(.+)', line)
        if chapter_match:
            chapter_num = chapter_match.group(1)
            chapter_title = chapter_match.group(2).strip()
            chapter_boundaries[chapter_num] = {
                'title': f"{chapter_num}. {chapter_title}",
                'start_line': i
            }

    # Собираем определения терминов для объединения в пункт 1.5
    term_definitions: dict[str, str] = {}

    # 3.1. Пункты формата X.Y.Z. (например, 3.5.17, 3.8.1)
    clause_pattern_xyz = r'\s*(\d+)\.(\d+)\.(\d+)\.\s+(.+?)(?=\n\s*\d+\.\d+\.\d+\.|\n\s*#|\n\s*Глава|\Z)'
    xyz_matches = list(re.finditer(clause_pattern_xyz, markdown_text, re.DOTALL))

    for match in xyz_matches:
        section_num = match.group(1)
        subsection_num = match.group(2)
        clause_num = match.group(3)
        clause_content = match.group(4)
        start_pos = match.start()
        line_num = get_line_num_from_pos(start_pos, markdown_text)
        chapter_num = get_chapter_num_by_position(line_num, chapter_boundaries)

        if section_num in section_headers:
            full_clause_number = f"{section_num}.{subsection_num}.{clause_num}"
        else:
            full_clause_number = f"{chapter_num}.{section_num}.{subsection_num}.{clause_num}"

        if full_clause_number not in processed_clauses:
            current_section_title = section_headers.get(chapter_num, f"{chapter_num}. Раздел {chapter_num}")
            content = re.sub(r'\n+', ' ', clause_content.strip())

            metadata = ChunkMetadata(
                source_document_title=full_title,
                short_document_title=short_title,
                clause_number=full_clause_number,
                parent_section_title=current_section_title,
                hierarchy=[short_title, current_section_title, full_clause_number],
                cross_references={}
            )

            chunk = Chunk(page_content=content, metadata=metadata)
            chunks.append(chunk)
            processed_clauses.add(full_clause_number)

    # 3.2. Пункты формата X.Y. (например, 3.5, 3.8, 5.23)
    clause_pattern_xy = r'\s*(\d+)\.(\d+)\.\s+(.+?)(?=\n\s*\d+\.\d+\.|\n\s*#|\n\s*Глава|\Z)'
    xy_matches = list(re.finditer(clause_pattern_xy, markdown_text, re.DOTALL))

    for match in xy_matches:
        section_num = match.group(1)
        clause_num = match.group(2)
        clause_content = match.group(3)
        start_pos = match.start()
        line_num = get_line_num_from_pos(start_pos, markdown_text)
        chapter_num = get_chapter_num_by_position(line_num, chapter_boundaries)

        if section_num in section_headers:
            full_clause_number = f"{section_num}.{clause_num}"
        else:
            full_clause_number = f"{chapter_num}.{section_num}.{clause_num}"

        if full_clause_number not in processed_clauses:
            current_section_title = section_headers.get(chapter_num, f"{chapter_num}. Раздел {chapter_num}")
            content = re.sub(r'\n+', ' ', clause_content.strip())

            metadata = ChunkMetadata(
                source_document_title=full_title,
                short_document_title=short_title,
                clause_number=full_clause_number,
                parent_section_title=current_section_title,
                hierarchy=[short_title, current_section_title, full_clause_number],
                cross_references={}
            )

            chunk = Chunk(page_content=content, metadata=metadata)
            chunks.append(chunk)
            processed_clauses.add(full_clause_number)

    # 3.3. Пункты формата "X.Y." (например, "1.1.", "1.2.", "3.4.")
    # Формат без пробела после точки номера
    clause_pattern_dotted = r'\s*(\d+)\.(\d+)\.(.+?)(?=\n\s*\d+\.\d+\.|\n\s*#|\n\s*Глава|\Z)'
    dotted_matches = list(re.finditer(clause_pattern_dotted, markdown_text, re.DOTALL))

    for match in dotted_matches:
        section_num = match.group(1)
        clause_num = match.group(2)
        clause_content = match.group(3)
        start_pos = match.start()
        line_num = get_line_num_from_pos(start_pos, markdown_text)
        chapter_num = get_chapter_num_by_position(line_num, chapter_boundaries)

        if section_num in section_headers:
            full_clause_number = f"{section_num}.{clause_num}"
        else:
            full_clause_number = f"{chapter_num}.{section_num}.{clause_num}"

        if full_clause_number not in processed_clauses:
            current_section_title = section_headers.get(chapter_num, f"{chapter_num}. Раздел {chapter_num}")
            content = re.sub(r'\n+', ' ', clause_content.strip())

            metadata = ChunkMetadata(
                source_document_title=full_title,
                short_document_title=short_title,
                clause_number=full_clause_number,
                parent_section_title=current_section_title,
                hierarchy=[short_title, current_section_title, full_clause_number],
                cross_references={}
            )

            chunk = Chunk(page_content=content, metadata=metadata)
            chunks.append(chunk)
            processed_clauses.add(full_clause_number)

    # 3.4. Простые номера разделов (например, 1., 2., 3.)
    # Ищем разделы, которые содержат текст (не только заголовки)
    section_pattern = r'\s*(\d+)\.\s+(.+?)(?=\n\s*\d+\.\s+|\n\s*#|\n\s*Глава|\Z)'
    section_matches = list(re.finditer(section_pattern, markdown_text, re.DOTALL))

    for match in section_matches:
        section_num = match.group(1)
        section_content = match.group(2)
        start_pos = match.start()
        line_num = get_line_num_from_pos(start_pos, markdown_text)
        chapter_num = get_chapter_num_by_position(line_num, chapter_boundaries)

        if section_num in section_headers:
            full_clause_number = section_num
        else:
            full_clause_number = f"{chapter_num}.{section_num}"

        # Проверяем, что это не заголовок раздела (содержит значимый текст)
        if len(section_content.strip()) > 5:  # Значительно снижен порог для захвата всех пунктов
            current_section_title = section_headers.get(chapter_num, f"{chapter_num}. Раздел {chapter_num}")

            if full_clause_number not in processed_clauses:
                content = re.sub(r'\n+', ' ', section_content.strip())

                metadata = ChunkMetadata(
                    source_document_title=full_title,
                    short_document_title=short_title,
                    clause_number=full_clause_number,
                    parent_section_title=current_section_title,
                    hierarchy=[short_title, current_section_title, full_clause_number],
                    cross_references={}
                )

                chunk = Chunk(page_content=content, metadata=metadata)
                chunks.append(chunk)
                processed_clauses.add(full_clause_number)

    # 4. Постобработка: разбиение чанков на подпункты
    processed_chunks = []
    for chunk in chunks:
        sub_chunks = split_chunk_into_subclauses(chunk)
        processed_chunks.extend(sub_chunks)

    return processed_chunks


def split_chunk_into_subclauses(chunk: Chunk) -> List[Chunk]:
    """
    Разбивает чанк на подпункты, если они присутствуют в содержимом.

    Args:
        chunk: Исходный чанк для разбивки

    Returns:
        Список чанков: либо исходный чанк, либо разбитые на подпункты
    """
    content = chunk.page_content
    metadata = chunk.metadata

    # Ищем подпункты в формате X. текст (простые номера подпунктов)
    subclause_pattern = r'(\d+)\.\s+(.+?)(?=\d+\.\s+|\Z)'
    subclause_matches = list(re.finditer(subclause_pattern, content, re.DOTALL))

    if not subclause_matches:
        # Если подпунктов нет, возвращаем исходный чанк
        return [chunk]

    # Разбиваем на подпункты
    sub_chunks = []
    processed_positions = set()

    for match in subclause_matches:
        subclause_num = match.group(1)
        subclause_content = match.group(2).strip()

        # Создаем номер подпункта на основе номера текущего чанка
        subclause_number = f"{metadata.clause_number}.{subclause_num}"

        # Создаем новый чанк для подпункта
        new_metadata = ChunkMetadata(
            source_document_title=metadata.source_document_title,
            short_document_title=metadata.short_document_title,
            clause_number=subclause_number,
            parent_section_title=metadata.parent_section_title,
            hierarchy=[metadata.short_document_title, metadata.parent_section_title, subclause_number],
            cross_references={}
        )

        # Очищаем текст от лишних пробелов и переносов строк
        clean_content = re.sub(r'\n+', ' ', subclause_content)

        new_chunk = Chunk(page_content=clean_content, metadata=new_metadata)
        sub_chunks.append(new_chunk)
        processed_positions.add(match.start())

    # Если подпункты найдены, возвращаем их вместо исходного чанка
    if sub_chunks:
        return sub_chunks
    else:
        # Если подпункты не найдены, возвращаем исходный чанк
        return [chunk]