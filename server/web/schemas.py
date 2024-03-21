from pydantic import BaseModel


class Post(BaseModel):
    id: int
    latitude: float
    longitude: float
    address: str
    title: str
    text: str
    kind: str
    data: bytes
    score: int


class BasePost(BaseModel):
    id: int
    latitude: float
    longitude: float
    address: str
    title: str
    text: str
    kind: str
    score: int


class Kind(BaseModel):
    name: str
    description: str
