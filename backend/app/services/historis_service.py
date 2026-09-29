import pandas as pd
from sqlalchemy.orm import Session
from app.core.database import HistorisIndex


def get_last_n_months(db: Session, kabupaten: str, before_tahun: int, before_bulan: int, n: int = 2) -> pd.DataFrame:
    """
    Ambil n bulan historis terakhir SEBELUM (before_tahun, before_bulan) untuk kabupaten tertentu.
    Diurutkan dari yang paling lama ke paling baru (agar iloc[-1] = lag1, iloc[-2] = lag2 konsisten
    dengan logika feature_engineering.py).
    """
    rows = (
        db.query(HistorisIndex)
        .filter(HistorisIndex.kabupaten == kabupaten)
        .filter(
            (HistorisIndex.tahun < before_tahun)
            | ((HistorisIndex.tahun == before_tahun) & (HistorisIndex.bulan < before_bulan))
        )
        .order_by(HistorisIndex.tahun.desc(), HistorisIndex.bulan.desc())
        .limit(n)
        .all()
    )
    rows = list(reversed(rows))

    return pd.DataFrame([{
        "tahun": r.tahun,
        "bulan": r.bulan,
        "tanggal": r.tanggal,
        "NDVI_mean": r.ndvi_mean,
        "EVI_mean": r.evi_mean,
        "SAVI_mean": r.savi_mean,
    } for r in rows])


def insert_new_month(db: Session, kabupaten: str, tahun: int, bulan: int, tanggal, ndvi: float, evi: float, savi: float):
    """Simpan hasil ekstraksi bulan baru agar bisa dipakai sebagai historis untuk prediksi bulan berikutnya."""
    existing = (
        db.query(HistorisIndex)
        .filter_by(kabupaten=kabupaten, tahun=tahun, bulan=bulan)
        .first()
    )
    if existing:
        existing.ndvi_mean, existing.evi_mean, existing.savi_mean = ndvi, evi, savi
    else:
        db.add(HistorisIndex(
            kabupaten=kabupaten, tahun=tahun, bulan=bulan, tanggal=tanggal,
            ndvi_mean=ndvi, evi_mean=evi, savi_mean=savi,
        ))
    db.commit()
    
def bulan_sebelumnya(tahun: int, bulan: int, n: int) -> tuple[int, int]:
    idx = tahun * 12 + (bulan - 1) - n
    return idx // 12, idx % 12 + 1


def get_index_map(db: Session, kabupaten: str) -> dict:
    """Seluruh indeks vegetasi kabupaten dalam bentuk {(tahun, bulan): {NDVI_mean, EVI_mean, SAVI_mean}}."""
    rows = db.query(HistorisIndex).filter(HistorisIndex.kabupaten == kabupaten).all()
    return {
        (r.tahun, r.bulan): {
            "NDVI_mean": r.ndvi_mean,
            "EVI_mean": r.evi_mean,
            "SAVI_mean": r.savi_mean,
        }
        for r in rows
    }