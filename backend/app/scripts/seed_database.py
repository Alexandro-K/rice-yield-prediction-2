import pandas as pd
from app.core.database import init_db, SessionLocal, HistorisIndex, DB_PATH
from app.core.config import DATA_DIR

def seed():
    init_db()
    db = SessionLocal()

    df = pd.read_csv(DATA_DIR / "historis_index.csv", parse_dates=["tanggal"])

    count = 0
    for _, row in df.iterrows():
        exists = (
            db.query(HistorisIndex)
            .filter_by(kabupaten=row["Kabupaten"], tahun=int(row["Tahun"]), bulan=int(row["Bulan"]))
            .first()
        )
        if exists:
            continue
        db.add(HistorisIndex(
            kabupaten=row["Kabupaten"],
            tahun=int(row["Tahun"]),
            bulan=int(row["Bulan"]),
            tanggal=row["tanggal"],
            ndvi_mean=row["NDVI_mean"],
            evi_mean=row["EVI_mean"],
            savi_mean=row["SAVI_mean"],
        ))
        count += 1

    db.commit()
    db.close()
    print(f"Seeding selesai. {count} baris baru dimasukkan ke {DB_PATH}")


if __name__ == "__main__":
    seed()