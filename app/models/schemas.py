from pydantic import BaseModel
from typing import List, Optional


class Block(BaseModel):
    type: str
    content: Optional[str] = None
    url: Optional[str] = None
    name: Optional[str] = None
    # accesibilidad imagen
    alt_text: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None

    question: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[int] = None


class Page(BaseModel):
    title: str
    blocks: List[Block]


class Course(BaseModel):
    title: str
    code: str   # 👈 AGREGA ESTO
    pages: List[Page]