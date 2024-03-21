from sqlalchemy.orm import Mapped, mapped_column, Session

from .db import Base
from . import schemas


class DBPost(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    address: Mapped[str]
    title: Mapped[str]
    text: Mapped[str]
    kind: Mapped[str]
    data: Mapped[bytes]
    score: Mapped[int]


class DBKind(Base):
    __tablename__ = "kinds"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str]


def get_post_img(db: Session, id: int):
    return db.query(DBPost.data).filter(DBPost.id == id).one()[0]


def create_post(
    db: Session,
    latitude: float,
    longitude: float,
    text: str,
    image: bytes,
    kind: str,
    title: str,
    address: str,
):
    db_post = DBPost(
        latitude=latitude,
        longitude=longitude,
        text=text,
        data=image,
        kind=kind,
        title=title,
        address=address,
        score=0,
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post.id


def get_posts(db: Session):
    return [
        schemas.BasePost.model_validate(x, from_attributes=True)
        for x in db.query(DBPost).all()
    ]


def get_kinds(db: Session):
    return [
        schemas.Kind.model_validate(x, from_attributes=True)
        for x in db.query(DBKind).all()
    ]


def create_kind(db: Session, kind: schemas.Kind):
    kind = DBKind(**kind.model_dump())
    db.add(kind)
    db.commit()
    db.refresh(kind)
    return kind.id


def delete_kind(db: Session, name: str):
    kind = db.query(DBKind).filter(DBKind.name == name).one()
    db.delete(kind)
    db.commit()


def upvote(db: Session, id: int):
    post = db.query(DBPost).filter(DBPost.id == id).one()
    post.score += 1
    db.commit()
