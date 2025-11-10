from typing import List, Any, Dict
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

from src.chunk import Chunk


class ReportGenerator:
    """
    Класс для генерации HTML-отчетов из списка чанков.
    
    Класс отвечает за загрузку Jinja2 шаблона и рендеринг 
    HTML-отчета на основе переданного списка чанков.
    """
    
    def __init__(self) -> None:
        """Инициализация генератора отчетов."""
        self.jinja_env = None
    
    def _setup_jinja_environment(self, template_path: str) -> Environment:
        """
        Настройка окружения Jinja2 для работы с шаблонами.
        
        Args:
            template_path: Путь к директории с шаблонами
            
        Returns:
            Environment: Настроенное окружение Jinja2
            
        Raises:
            FileNotFoundError: Если директория с шаблонами не найдена
        """
        template_dir = Path(template_path)
        if not template_dir.exists():
            raise FileNotFoundError(f"Директория с шаблонами не найдена: {template_path}")
        
        return Environment(loader=FileSystemLoader(str(template_dir)))
    
    def generate(self, chunks: List[Chunk], template_path: str, output_path: str) -> None:
        """
        Генерация HTML-отчета из списка чанков.
        
        Метод загружает Jinja2 шаблон из указанного пути, 
        рендерит его с переданным списком чанков и сохраняет 
        результат в файл.
        
        Args:
            chunks: Список чанков для включения в отчет
            template_path: Путь к директории с шаблонами
            output_path: Путь для сохранения сгенерированного HTML-файла
            
        Raises:
            FileNotFoundError: Если шаблон не найден
            Exception: При ошибках рендеринга или сохранения файла
        """
        try:
            # Настройка окружения Jinja2
            if self.jinja_env is None:
                self.jinja_env = self._setup_jinja_environment(template_path)
            
            # Загрузка шаблона report_template.html
            template_name = "report_template.html"
            template = self.jinja_env.get_template(template_name)
            
            # Подготовка данных для рендеринга
            render_data: Dict[str, Any] = {
                "chunks": chunks,
                "total_chunks": len(chunks),
                "generated_at": "Текущее время"  # Можно добавить datetime.now()
            }
            
            # Рендеринг шаблона
            rendered_html = template.render(**render_data)
            
            # Создание директории для выходного файла, если она не существует
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Сохранение результата
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            print(f"Отчет успешно сгенерирован: {output_path}")
            print(f"Количество обработанных чанков: {len(chunks)}")
            
        except FileNotFoundError as e:
            print(f"Ошибка: Шаблон не найден - {e}")
            raise
        except Exception as e:
            print(f"Ошибка при генерации отчета: {e}")
            raise