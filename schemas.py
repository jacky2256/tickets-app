from typing import List
from pydantic import BaseModel


class EntryKeyword(BaseModel):
    id: int
    name: str


class EntryKeywords(BaseModel):
    keywords: List[EntryKeyword]


class OutputKeyword(BaseModel):
    id: int
    name: str
    min_price_vivid: int = 0
    min_price_ticket: int = 0


class OutputKeywords(BaseModel):
    keywords: List[OutputKeyword]