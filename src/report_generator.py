"""Модуль для генерации HTML-отчетов с использованием шаблонизатора Jinja2."""

import logging
from pathlib import Path
from typing import List
from src.data_models import Chunk

import jinja2
from jinja2 import Environment, FileSystemLoader


def generate_report(chunks: List[Chunk], template_path: str, output_path: str) -> None:
    """
    Генерирует HTML-отчет на основе списка чанков и шаблона Jinja2.
    
    Функция загружает HTML-шаблон из указанного файла, рендерит его с данными
    о чанках и сохраняет результат в выходной файл. Автоматически создает
    необходимые директории для выходного файла.
    
    Args:
        chunks (List[Chunk]): Список объектов Chunk для включения в отчет.
        template_path (str): Путь к HTML-шаблону Jinja2.
        output_path (str): Путь для сохранения сгенерированного HTML-отчета.
        
    Raises:
        FileNotFoundError: Если шаблон не найден по указанному пути.
        PermissionError: При отсутствии прав на запись в выходной файл.
        jinja2.TemplateError: При ошибках в шаблоне или его рендеринге.
        OSError: При проблемах с файловой системой.
        
    Example:
        >>> chunks = [Chunk(content="Текст", metadata={"context": "Глава 1"})]
        >>> generate_report(chunks, "templates/report.html", "output/report.html")
    """
    logger = logging.getLogger(__name__)
    
    # Проверяем существование шаблона
    template_file = Path(template_path)
    if not template_file.exists():
        error_msg = f"Шаблон не найден: {template_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    logger.info(f"Загрузка шаблона из: {template_path}")
    
    try:
        # Создаем окружение Jinja2 с загрузчиком файловой системы
        template_dir = template_file.parent
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        
        # Загружаем шаблон
        template_name = template_file.name
        template = env.get_template(template_name)
        
        logger.info(f"Шаблон '{template_name}' успешно загружен")
        
    except jinja2.TemplateError as e:
        error_msg = f"Ошибка при загрузке шаблона: {e}"
        logger.error(error_msg)
        raise jinja2.TemplateError(error_msg) from e
    
    # Подготавливаем контекст для рендеринга
    context = {'chunks': chunks}
    logger.info(f"Подготовлен контекст с {len(chunks)} чанками")
    
    try:
        # Рендерим шаблон
        rendered_html = template.render(context)
        logger.info("Шаблон успешно отрендерен")
        
    except jinja2.TemplateError as e:
        error_msg = f"Ошибка при рендеринге шаблона: {e}"
        logger.error(error_msg)
        raise jinja2.TemplateError(error_msg) from e
    
    # Создаем директорию для выходного файла если она не существует
    output_file = Path(output_path)
    output_dir = output_file.parent
    
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Директория для выходного файла готова: {output_dir}")
        
    except OSError as e:
        error_msg = f"Не удалось создать директорию {output_dir}: {e}"
        logger.error(error_msg)
        raise OSError(error_msg) from e
    
    # Записываем отрендеренный HTML в файл
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
            
        logger.info(f"HTML-отчет успешно сохранен: {output_path}")
        logger.info(f"Размер файла: {len(rendered_html):,} символов")
        
    except PermissionError as e:
        error_msg = f"Нет прав на запись в файл {output_path}: {e}"
        logger.error(error_msg)
        raise PermissionError(error_msg) from e
        
    except OSError as e:
        error_msg = f"Ошибка при записи файла {output_path}: {e}"
        logger.error(error_msg)
        raise OSError(error_msg) from e