import sys
import time
from datetime import datetime

import pandas as pd

from app.core.config import DATA_DIR, KABUPATEN_LIST
from app.services.gee_pipeline import init_gee, extract_monthly_stats_for_kabupaten

CSV_PATH = DATA_DIR / "historis_index.csv"
KUNCI_INDEKS = ["NDVI_mean", "EVI_mean", "SAVI_mean"]


def backfill(tahun_akhir: int, bulan_akhir: int):
    df = pd.read_csv(CSV_PATH, dtype={"tanggal": str})
    contoh_tanggal = str(df["tanggal"].iloc[0])
    format_tanggal = "%Y-%m-%d %H:%M:%S" if " " in contoh_tanggal else "%Y-%m-%d"

    idx_akhir = tahun_akhir * 12 + (bulan_akhir - 1)
    init_gee()

    dilewati = []
    for kab in KABUPATEN_LIST:
        sub = df[df["Kabupaten"] == kab]
        idx_terakhir = int((sub["Tahun"] * 12 + sub["Bulan"] - 1).max())

        for idx in range(idx_terakhir + 1, idx_akhir + 1):
            tahun, bulan = idx // 12, idx % 12 + 1
            mulai = time.time()

            try:
                stats = extract_monthly_stats_for_kabupaten(kab, tahun, bulan)
            except Exception as e:
                print(f"[GAGAL] {kab} {bulan:02d}/{tahun}: {e}")
                dilewati.append(f"{kab} {bulan:02d}/{tahun}")
                continue

            if any(stats.get(k) is None for k in KUNCI_INDEKS):
                print(f"[DILEWATI] {kab} {bulan:02d}/{tahun}: tidak ada citra bersih")
                dilewati.append(f"{kab} {bulan:02d}/{tahun}")
                continue

            baris = {
                "Kabupaten": kab,
                "Tahun": tahun,
                "Bulan": bulan,
                "tanggal": datetime(tahun, bulan, 1).strftime(format_tanggal),
                **{k: stats[k] for k in KUNCI_INDEKS},
            }
            df = pd.concat([df, pd.DataFrame([baris])], ignore_index=True)
            df.to_csv(CSV_PATH, index=False)  # simpan tiap bulan agar aman jika dihentikan

            print(f"[OK] {kab} {bulan:02d}/{tahun} ({time.time() - mulai:.0f} dtk)")

    print("\nSelesai.")
    if dilewati:
        print("Bulan yang tidak berhasil diisi:", dilewati)


if __name__ == "__main__":
    tahun_akhir = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    bulan_akhir = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    backfill(tahun_akhir, bulan_akhir)