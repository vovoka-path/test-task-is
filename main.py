from pathlib import Path
from typing import List

from src.chunk import Chunk
from src.report_generator import ReportGenerator


def create_test_chunks() -> List[Chunk]:
    """Создает список тестовых чанков для проверки системы.
    
    Функция создает два тестовых объекта Chunk с различными
    метаданными для проверки корректности работы генератора отчетов.
    
    Returns:
        List[Chunk]: Список из двух тестовых чанков
    """
    # Первый тестовый чанк
    chunk1 = Chunk(
        content="Это тестовый текст первого чанка",
        metadata={
            "source_document": "test.docx",
            "chapter": "1",
            "section": "1.1"
        }
    )
    
    # Второй тестовый чанк
    chunk2 = Chunk(
        content="Это тестовый текст второго чанка",
        metadata={
            "source_document": "test.docx",
            "chapter": "1",
            "section": "1.2"
        }
    )
    
    return [chunk1, chunk2]


def ensure_output_directory() -> None:
    """Создает директорию для выходных файлов если она не существует.
    
    Функция гарантирует наличие директории output/ для сохранения
    сгенерированных отчетов.
    """
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Директория для выходных файлов готова: {output_dir.absolute()}")


def main() -> None:
    """Основная функция для запуска дымового теста системы чанкинга.
    
    Функция выполняет следующие шаги:
    1. Создает тестовые данные (чанки)
    2. Инициализирует генератор отчетов
    3. Генерирует HTML-отчет
    4. Обрабатывает возможные ошибки
    """
    try:
        print("=" * 60)
        print("ЗАПУСК ДЫМОВОГО ТЕСТА СИСТЕМЫ ЧАНКИНГА ДОКУМЕНТОВ")
        print("=" * 60)
        
        # Шаг 1: Создание тестовых данных
        print("\n1. Создание тестовых чанков...")
        test_chunks = create_test_chunks()
        print(f"   Создано {len(test_chunks)} тестовых чанков")
        
        # Вывод информации о созданных чанках для отладки
        for i, chunk in enumerate(test_chunks, 1):
            print(f"   Чанк {i}: '{chunk.content[:30]}...' "
                  f"(глава {chunk.metadata.get('chapter', 'N/A')}, раздел {chunk.metadata.get('section', 'N/A')})")
        
        # Шаг 2: Подготовка выходной директории
        print("\n2. Подготовка выходной директории...")
        ensure_output_directory()
        
        # Шаг 3: Инициализация генератора отчетов
        print("\n3. Инициализация генератора отчетов...")
        report_generator = ReportGenerator()
        print("   Генератор отчетов успешно инициализирован")
        
        # Шаг 4: Генерация отчета
        print("\n4. Генерация HTML-отчета...")
        template_path = "templates"
        output_path = "output/report.html"
        
        report_generator.generate(
            chunks=test_chunks,
            template_path=template_path,
            output_path=output_path
        )
        
        print("\n" + "=" * 60)
        print("ДЫМОВОЙ ТЕСТ УСПЕШНО ЗАВЕРШЕН!")
        print("=" * 60)
        print(f"Отчет сохранен в файл: {output_path}")
        print("Откройте файл в браузере для просмотра результата.")
        
    except FileNotFoundError as e:
        print(f"\n❌ ОШИБКА: Файл не найден - {e}")
        print("Убедитесь, что файл шаблона templates/report_template.html существует")
        
    except Exception as e:
        print(f"\n❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
        print("Проверьте корректность установленных зависимостей и структуру проекта")


if __name__ == "__main__":
    main()