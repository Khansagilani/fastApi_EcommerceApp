from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select


db_con = f"postgresql://postgres:khansa1086@localhost:5432/ecommerce_app"

engine = create_engine(db_con)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
