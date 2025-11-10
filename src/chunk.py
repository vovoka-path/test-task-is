from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Chunk:
    """Структура данных для хранения фрагмента текста и его метаданных.
    
    Класс Chunk представляет собой единицу текстового контента, извлеченного
    из документа, вместе с метаданными о его расположении в исходном документе.
    
    Attributes:
        content (str): Текстовое содержимое чанка.
        metadata (Dict[str, Any]): Словарь с метаданными чанка, включающий информацию
                                 об источнике, главе и разделе.
    """
    
    content: str
    metadata: Dict[str, Any]