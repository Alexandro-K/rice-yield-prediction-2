import os
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = Path(os.getenv("DB_PATH", BASE_DIR / "data" / "app.db"))

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class HistorisIndex(Base):
    __tablename__ = "historis_index"

    id = Column(Integer, primary_key=True, autoincrement=True)
    kabupaten = Column(String, index=True, nullable=False)
    tahun = Column(Integer, nullable=False)
    bulan = Column(Integer, nullable=False)
    tanggal = Column(DateTime, nullable=False)
    ndvi_mean = Column(Float, nullable=False)
    evi_mean = Column(Float, nullable=False)
    savi_mean = Column(Float, nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()