import json
from typing import Optional

import pandas as pd

from app.core.config import DATA_DIR

NAMA_BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

# Parafrase dari paper yang diberikan pengguna. NDVI dan EVI punya dasar literatur;
# SAVI belum punya sumber literatur yang diberikan, sehingga narasinya netral.
DESKRIPSI_NDVI = {
    "Rendah": (
        "berada pada 25% terendah riwayat NDVI kabupaten ini. Penurunan NDVI dari waktu ke waktu "
        "umumnya diasosiasikan dengan pencoklatan atau penurunan kehijauan vegetasi (Myers-Smith et al., 2020)."
    ),
    "Sedang": "berada pada rentang tengah riwayat NDVI kabupaten ini, sejalan dengan fase pertumbuhan tanaman.",
    "Tinggi": (
        "berada pada 25% tertinggi riwayat NDVI kabupaten ini. Kenaikan NDVI umumnya diasosiasikan dengan "
        "penghijauan atau kehijauan vegetasi yang meningkat (Myers-Smith et al., 2020), dan NDVI secara umum "
        "dipakai sebagai ukuran kehijauan aboveground vegetation (Pettorelli et al., 2005; 2011)."
    ),
}

DESKRIPSI_EVI = {
    "Rendah": (
        "berada pada 25% terendah riwayat EVI kabupaten ini. Nilai EVI yang menurun dari waktu ke waktu "
        "dapat mengindikasikan pelemahan kondisi dan kesehatan vegetasi."
    ),
    "Sedang": "berada pada rentang tengah riwayat EVI kabupaten ini.",
    "Tinggi": (
        "berada pada 25% tertinggi riwayat EVI kabupaten ini. Pada vegetasi sehat, nilai EVI umumnya berkisar "
        "0,2 sampai 0,8, dengan nilai yang lebih tinggi menunjukkan kanopi yang lebih rapat dan sehat."
    ),
}

DESKRIPSI_SAVI = {
    "Rendah": "berada pada 25% terendah riwayat SAVI kabupaten ini.",
    "Sedang": "berada pada rentang tengah riwayat SAVI kabupaten ini.",
    "Tinggi": "berada pada 25% tertinggi riwayat SAVI kabupaten ini.",
}

DESKRIPSI_PER_INDEKS = {"NDVI": DESKRIPSI_NDVI, "EVI": DESKRIPSI_EVI, "SAVI": DESKRIPSI_SAVI}

_cache = {}


def _load_data() -> dict:
    if not _cache:
        with open(DATA_DIR / "produksi_stats.json") as f:
            _cache["produksi_stats"] = json.load(f)
        with open(DATA_DIR / "vegetasi_stats.json") as f:
            _cache["vegetasi_stats"] = json.load(f)
        _cache["riwayat"] = pd.read_csv(DATA_DIR / "produksi_historis.csv")
        with open(DATA_DIR / "model_insight.json") as f:
            _cache["model_insight"] = json.load(f)
    return _cache


def _format_angka(nilai: float, desimal: int = 2) -> str:
    teks = f"{nilai:,.{desimal}f}"
    return teks.replace(",", "X").replace(".", ",").replace("X", ".")


def kabupaten_tersedia(kabupaten: str) -> bool:
    return kabupaten in _load_data()["produksi_stats"]


def get_model_insight() -> dict:
    return _load_data()["model_insight"]


def get_riwayat_produksi(kabupaten: str) -> list[dict]:
    df = _load_data()["riwayat"]
    df_kab = df[df["Kabupaten"] == kabupaten].sort_values(["Tahun", "Bulan"])
    return [
        {"tahun": int(r.Tahun), "bulan": int(r.Bulan), "produksi_ton": float(r.Produksi_Ton)}
        for r in df_kab.itertuples()
    ]


def klasifikasi_produksi(kabupaten: str, bulan: int, prediksi: float) -> tuple[str, dict, str]:
    s = _load_data()["produksi_stats"][kabupaten]
    per_bulan = s["kuartil_per_bulan"].get(str(bulan))

    if per_bulan:
        q25, q75 = per_bulan["q25"], per_bulan["q75"]
        sumber = f"kuartil produksi bulan {NAMA_BULAN[bulan - 1]} kabupaten ini ({per_bulan['n']} tahun data)"
    else:
        q25, q75 = s["q25_keseluruhan"], s["q75_keseluruhan"]
        sumber = "kuartil produksi seluruh bulan kabupaten ini (data bulan tersebut belum cukup untuk dihitung terpisah)"

    if prediksi < q25:
        kategori = "Rendah"
    elif prediksi > q75:
        kategori = "Tinggi"
    else:
        kategori = "Sedang"

    return kategori, {"q25": q25, "q75": q75}, sumber


def klasifikasi_vegetasi(kabupaten: str, indeks: str, nilai: float) -> tuple[str, dict, str]:
    s = _load_data()["vegetasi_stats"][kabupaten][indeks]
    batas = {"q25": s["q25"], "q75": s["q75"]}
    if nilai < s["q25"]:
        kategori = "Rendah"
    elif nilai > s["q75"]:
        kategori = "Tinggi"
    else:
        kategori = "Sedang"
    deskripsi = DESKRIPSI_PER_INDEKS[indeks][kategori]
    return kategori, batas, deskripsi


def bandingkan_musiman(kabupaten: str, bulan: int, prediksi: float) -> tuple[Optional[float], Optional[float]]:
    per_bulan = _load_data()["produksi_stats"][kabupaten]["kuartil_per_bulan"].get(str(bulan))
    if not per_bulan:
        return None, None
    rata = per_bulan["rata_rata"]
    selisih = (prediksi - rata) / rata * 100
    return rata, selisih


def susun_narasi(kabupaten, tahun, bulan, prediksi,
                  kategori_prod, sumber_kuartil_prod, rata_bulan, selisih,
                  ndvi_val, kategori_ndvi, deskripsi_ndvi,
                  evi_val, kategori_evi, deskripsi_evi,
                  savi_val, kategori_savi, deskripsi_savi) -> str:
    nama_bulan = NAMA_BULAN[bulan - 1]

    kalimat = [
        f"Produksi padi di {kabupaten} pada {nama_bulan} {tahun} diprediksi sebesar "
        f"{_format_angka(prediksi)} ton, termasuk kategori {kategori_prod.lower()} berdasarkan {sumber_kuartil_prod}."
    ]

    if rata_bulan is not None and selisih is not None:
        arah = "lebih tinggi" if selisih >= 0 else "lebih rendah"
        kalimat.append(
            f"Nilai ini {_format_angka(abs(selisih), 1)}% {arah} dari rata-rata historis bulan "
            f"{nama_bulan} di kabupaten ini ({_format_angka(rata_bulan)} ton)."
        )

    kalimat.append(
        f"Nilai NDVI pada periode ini adalah {ndvi_val:.4f} (kategori {kategori_ndvi.lower()}), "
        f"{deskripsi_ndvi}"
    )
    kalimat.append(
        f"Nilai EVI adalah {evi_val:.4f} (kategori {kategori_evi.lower()}), {deskripsi_evi}"
    )
    kalimat.append(
        f"Nilai SAVI adalah {savi_val:.4f} (kategori {kategori_savi.lower()}), {deskripsi_savi}"
    )
    kalimat.append(
        "Seluruh kategori vegetasi dan produksi ditentukan dari kuartil pertama dan ketiga riwayat data "
        "kabupaten yang bersangkutan. Interpretasi ini bersifat indikatif, bukan pengganti data produksi resmi."
    )
    return " ".join(kalimat)