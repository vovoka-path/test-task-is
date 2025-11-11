"""
Главный файл приложения для обработки документов.
Содержит точки входа для запуска парсинга документов и пайплайна обработки.
"""

import json
import logging
import sys
from pathlib import Path
from typing import List

from src.schemas import Chunk

# Путь к документу
input_file_path_str = "data/input/1. Правила № 32 с 11.12.2023.docx"
# Путь к выходному файлу
output_file_path_str = "data/output/processed_chunks.json"

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def save_chunks_to_json(chunks: List[Chunk], output_path: Path) -> None:
    """
    Сохраняет список чанков в JSON файл.
    
    Args:
        chunks: Список чанков для сохранения
        output_path: Путь к выходному JSON файлу
    """
    # Создание родительской директории, если она не существует
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Преобразование списка Pydantic-объектов Chunk в список словарей
    chunks_data = [chunk.model_dump() for chunk in chunks]
    
    # Запись данных в файл с правильным кодированием и форматированием
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    try:
        # Импорты для работы с путями и схемами данных
        from src.pipeline import run_pipeline
        from src.schemas import Chunk
        
        # Создание пути к тестовому файлу
        # input_file_path: Path = Path("data/input/test_rules.docx")
        input_file_path: Path = Path(input_file_path_str)
        
        # Информационный print о начале процесса обработки
        print(f"🚀 Начинаю обработку документа: {input_file_path}")
        print("=" * 60)
        
        # Запуск пайплайна обработки документа
        chunks: List[Chunk] = run_pipeline(str(input_file_path))
        
        # Вывод общего количества созданных чанков
        print(f"✅ Пайплайн успешно завершен. Получено чанков: {len(chunks)}")
        print("=" * 60)
        
        # Вывод информации по первым 3 чанкам для ручной проверки
        print("📋 ПЕРВЫЕ 3 ЧАНКА ДЛЯ ПРОВЕРКИ:")
        print("=" * 60)
        
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n--- Чанк №{i+1} ---")
            print(f"Содержимое page_content:")
            print(f"{chunk.page_content}")
            print(f"\nМетаданные metadata:")
            for key, value in chunk.metadata.model_dump().items():
                print(f"  {key}: {value}")
            print("-" * 40)
        
        # Сохранение чанков в JSON файл
        output_file_path = Path(output_file_path_str)
        save_chunks_to_json(chunks, output_file_path)
        print(f"💾 Результаты сохранены в файл: {output_file_path}")
            
    except Exception as e:
        print(f"❌ Ошибка при выполнении пайплайна: {e}")
        logger.error(f"Ошибка в пайплайне: {e}", exc_info=True)