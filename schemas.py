from fastapi import Query
from pydantic import BaseModel


class UserBase(BaseModel):
    user: str


class TransactionBase(BaseModel):
    veritel: str
    dluznik: str
    castka: float



