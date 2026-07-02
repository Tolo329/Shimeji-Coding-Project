from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///mascota_virtual.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def init_db():
    from database.modelos import MascotaModel, ActividadModel
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
