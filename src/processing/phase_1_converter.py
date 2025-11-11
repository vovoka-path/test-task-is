"""
Фаза 1: Конвертация DOCX в Markdown.
Преобразует исходный документ из DOCX в текстовый формат Markdown.
"""

import re
import pypandoc
from src.utils.exceptions import PandocNotInstalledError


def convert_docx_to_markdown(file_path: str) -> tuple[str, str]:
    """
    Конвертирует DOCX файл в формат Markdown и извлекает название документа.
    
    Args:
        file_path: Путь к исходному DOCX файлу
        
    Returns:
        Кортеж из (название_документа, markdown_текст)
        
    Raises:
        PandocNotInstalledError: Если Pandoc не установлен в системе
    """
    try:
        # Конвертация с помощью pypandoc
        markdown_text = pypandoc.convert_file(file_path, 'markdown')
        if markdown_text is None:
            raise ValueError("Конвертация вернула пустой результат")
        
        # Извлекаем название документа из содержимого DOCX файла
        try:
            from docx import Document
            doc = Document(file_path)
            
            # Ищем строки с "ПРАВИЛА" и "№" для извлечения полного названия
            full_title_parts = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                    
                # Ищем строки с "ПРАВИЛА" и "№"
                if re.search(r'ПРАВИЛА.*№', text, re.IGNORECASE):
                    full_title_parts.append(text)
                elif full_title_parts and len(full_title_parts) < 3:
                    # После найденной строки с правилами, добавляем следующие строки
                    # если они не являются служебными
                    if not re.match(r'^\(', text) and not re.match(r'^Правила в редакции', text):
                        full_title_parts.append(text)
                    else:
                        break
            
            if full_title_parts:
                doc_title = ' '.join(full_title_parts)
            else:
                # Fallback к имени файла
                import os
                filename = os.path.basename(file_path)
                doc_title = os.path.splitext(filename)[0]
                
        except ImportError:
            # Если python-docx не доступен, используем имя файла
            import os
            filename = os.path.basename(file_path)
            doc_title = os.path.splitext(filename)[0]
        except Exception:
            # При любых ошибках используем имя файла
            import os
            filename = os.path.basename(file_path)
            doc_title = os.path.splitext(filename)[0]
        
        # Если в markdown есть первый заголовок (#), используем его как fallback
        lines = markdown_text.strip().split('\n')
        first_title = ""
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                first_title = line[2:].strip()
                break
        
        # Предпочитаем название из содержимого, если оно выглядит как документ
        if any(keyword in doc_title.upper() for keyword in ['ПРАВИЛА', 'ПОЛОЖЕНИЕ', 'ПРИКАЗ', 'УКАЗ']):
            final_title = doc_title
        else:
            # Получаем имя файла для сравнения
            import os
            filename = os.path.basename(file_path)
            final_title = doc_title if doc_title != os.path.splitext(filename)[0] else (first_title if first_title else "Документ")
        
        return (final_title, markdown_text)
        
    except OSError as e:
        raise PandocNotInstalledError(
            "Pandoc не установлен в системе. Установите Pandoc для продолжения."
        ) from e
    except Exception as e:
        raise ValueError(f"Ошибка при конвертации файла {file_path}: {e}") from e
