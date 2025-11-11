"""
Pydantic схемы для структур данных пайплайна.
Определяет валидируемые модели для чанков и метаданных.
"""

from typing import Annotated
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """
    Метаданные для чанка документа.
    
    Содержит структурную информацию о положении чанка в иерархии документа,
    включая полное и краткое название документа, номер пункта, родительский
    раздел, иерархию заголовков и перекрестные ссылки.
    """
    
    source_document_title: Annotated[
        str,
        Field(
            description="Полное название исходного документа, включая все номера и даты"
        )
    ]
    
    short_document_title: Annotated[
        str,
        Field(
            description="Краткое название документа без избыточной информации"
        )
    ]
    
    clause_number: Annotated[
        str,
        Field(
            description="Номер пункта документа в формате '1.2.1' или '1.2'"
        )
    ]
    
    parent_section_title: Annotated[
        str,
        Field(
            description="Название родительского раздела, к которому относится данный пункт"
        )
    ]
    
    hierarchy: Annotated[
        list[str],
        Field(
            description="Иерархия заголовков от корневого раздела до текущего пункта"
        )
    ]
    
    cross_references: Annotated[
        dict[str, str],
        Field(
            description="Словарь перекрестных ссылок, где ключ - номер пункта, значение - описание ссылки"
        )
    ]


class Chunk(BaseModel):
    """
    Основная модель чанка документа.
    
    Содержит текстовое содержимое и связанные с ним метаданные.
    """
    
    page_content: Annotated[
        str,
        Field(
            description="Текстовое содержимое чанка с обогащенным контекстом"
        )
    ]
    
    metadata: Annotated[
        ChunkMetadata,
        Field(
            description="Метаданные чанка с информацией о его положении в документе"
        )
    ]
