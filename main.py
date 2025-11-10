import os
from pathlib import Path
from typing import List
from datetime import datetime

from src.chunk import Chunk
from src.doc_processor import DocumentProcessor
from src.report_generator import ReportGenerator


def process_document_chunks(document_path: str) -> List[Chunk]:
    """Обрабатывает реальный документ и извлекает из него структурированные чанки.
    
    Функция использует DocumentProcessor для загрузки и парсинга .docx файла,
    извлекая текстовые фрагменты с сохранением иерархической структуры документа.
    
    Args:
        document_path: Путь к .docx файлу для обработки
        
    Returns:
        List[Chunk]: Список извлеченных чанков из документа
        
    Raises:
        FileNotFoundError: Если указанный файл не существует
        Exception: При ошибках обработки документа
    """
    try:
        # Создаем экземпляр процессора документов
        processor = DocumentProcessor(document_path)
        
        # Обрабатываем документ и получаем список чанков
        chunks = processor.process()
        
        print(f"Успешно обработан документ: {document_path}")
        print(f"Извлечено чанков: {len(chunks)}")
        
        return chunks
        
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Документ не найден: {document_path}. {e}")
    except Exception as e:
        raise Exception(f"Ошибка при обработке документа {document_path}: {e}")


def ensure_output_directory() -> None:
    """Создает директорию для выходных файлов если она не существует.
    
    Функция гарантирует наличие директории output/ для сохранения
    сгенерированных отчетов.
    """
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Директория для выходных файлов готова: {output_dir.absolute()}")


def main() -> None:
    """Основная функция для запуска системы чанкинга документов.
    
    Функция выполняет следующие шаги:
    1. Обрабатывает реальный документ data/example_rules.docx
    2. Извлекает структурированные чанки с помощью DocumentProcessor
    3. Генерирует HTML-отчет с помощью ReportGenerator
    4. Обрабатывает возможные ошибки
    """
    try:
        print("=" * 60)
        print("ЗАПУСК СИСТЕМЫ ЧАНКИНГА ДОКУМЕНТОВ")
        print("=" * 60)
        
        # Шаг 1: Обработка реального документа
        print("\n1. Обработка документа data/example_rules.docx...")
        document_path = "data/example_rules.docx"
        chunks = process_document_chunks(document_path)
        
        # Вывод информации о извлеченных чанках для отладки
        print("\n   Информация об извлеченных чанках:")
        for i, chunk in enumerate(chunks, 1):
            chapter = chunk.metadata.get('chapter', 'N/A')
            section = chunk.metadata.get('section', 'N/A')
            content_preview = chunk.content[:50] + "..." if len(chunk.content) > 50 else chunk.content
            print(f"   Чанк {i}: '{content_preview}' (глава {chapter}, раздел {section})")
        
        # Шаг 2: Подготовка выходной директории
        print("\n2. Подготовка выходной директории...")
        ensure_output_directory()
        
        # Шаг 3: Инициализация генератора отчетов
        print("\n3. Инициализация генератора отчетов...")
        report_generator = ReportGenerator()
        print("   Генератор отчетов успешно инициализирован")
        
        # Шаг 4: Генерация отчета
        print("\n4. Генерация HTML-отчета...")
        template_path = "templates/report_template.html"
        output_path = "output/report.html"
        
        # Проверяем существование шаблона
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Шаблон отчета не найден: {template_path}")
        
        report_generator.generate(
            chunks=chunks,
            template_path="templates",  # Передаем директорию, файл ищется внутри
            output_path=output_path
        )
        
        print("\n" + "=" * 60)
        print("ОБРАБОТКА ДОКУМЕНТА УСПЕШНО ЗАВЕРШЕНА!")
        print("=" * 60)
        print(f"Отчет сохранен в файл: {output_path}")
        print("Откройте файл в браузере для просмотра результата.")
        
        # Дополнительная информация о созданном файле
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            creation_time = datetime.fromtimestamp(os.path.getctime(output_path))
            print(f"Размер файла: {file_size:,} байт")
            print(f"Время создания: {creation_time.strftime('%d.%m.%Y %H:%M:%S')}")
        
    except FileNotFoundError as e:
        print(f"\n❌ ОШИБКА: Файл не найден - {e}")
        print("Убедитесь, что файл data/example_rules.docx существует")
        print("Также проверьте наличие шаблона templates/report_template.html")
        
    except Exception as e:
        print(f"\n❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
        print("Проверьте корректность установленных зависимостей и структуру проекта")
        print("Подробности ошибки могут помочь в диагностике проблемы")


if __name__ == "__main__":
    main()