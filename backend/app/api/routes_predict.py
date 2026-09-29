import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_session
from app.core.config import KABUPATEN_LIST, FITUR_FINAL
from app.schemas.predict_schema import (
    PredictRequest, PredictResponse, TrajectoryResponse, TitikTrajectory,
)
from app.services.gee_pipeline import extract_monthly_stats_for_kabupaten
from app.services.historis_service import (
    get_last_n_months, insert_new_month, bulan_sebelumnya, get_index_map,
)
from app.services.feature_engineering import build_feature_row
from app.services.model_service import predict, predict_batch
from app.services.insight_service import get_riwayat_produksi

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict_produksi(payload: PredictRequest, db: Session = Depends(get_session)):
    if payload.kabupaten not in KABUPATEN_LIST:
        raise HTTPException(status_code=400, detail=f"Kabupaten '{payload.kabupaten}' tidak dikenali. Pilihan: {KABUPATEN_LIST}")

    historis_df = get_last_n_months(db, payload.kabupaten, payload.tahun, payload.bulan, n=2)

    t1, b1 = bulan_sebelumnya(payload.tahun, payload.bulan, 1)
    t2, b2 = bulan_sebelumnya(payload.tahun, payload.bulan, 2)
    bulan_tersedia = [
        (int(t), int(b))
        for t, b in zip(historis_df.get("tahun", []), historis_df.get("bulan", []))
    ]
    if bulan_tersedia != [(t2, b2), (t1, b1)]:
        raise HTTPException(
            status_code=422,
            detail=(
                "Data indeks vegetasi dua bulan sebelum periode ini belum lengkap di basis data, "
                "sehingga fitur lag tidak dapat dibentuk dengan benar dan prediksi tidak dihitung."
            ),
        )

    stats = extract_monthly_stats_for_kabupaten(payload.kabupaten, payload.tahun, payload.bulan)

    required_keys = ["NDVI_mean", "EVI_mean", "SAVI_mean"]
    missing = [k for k in required_keys if stats.get(k) is None]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Citra Sentinel-2 tidak cukup jernih/tersedia untuk periode ini. Data hilang: {missing}"
        )

    index_bulan_ini = {k: stats[k] for k in required_keys}

    fitur_row = build_feature_row(
        kabupaten=payload.kabupaten,
        bulan=payload.bulan,
        index_bulan_ini=index_bulan_ini,
        historis_df=historis_df,
    )

    hasil_prediksi = predict(fitur_row)
    fitur_final_digunakan = {k: fitur_row[k] for k in FITUR_FINAL}

    tanggal_bulan_ini = datetime(payload.tahun, payload.bulan, 1)
    insert_new_month(
        db, payload.kabupaten, payload.tahun, payload.bulan, tanggal_bulan_ini,
        ndvi=index_bulan_ini["NDVI_mean"], evi=index_bulan_ini["EVI_mean"], savi=index_bulan_ini["SAVI_mean"],
    )

    return PredictResponse(
        kabupaten=payload.kabupaten,
        tahun=payload.tahun,
        bulan=payload.bulan,
        prediksi_produksi_ton=hasil_prediksi,
        ndvi_mean=index_bulan_ini["NDVI_mean"],
        evi_mean=index_bulan_ini["EVI_mean"],
        savi_mean=index_bulan_ini["SAVI_mean"],
        jumlah_citra=stats.get("n_images", 0),
        fitur_digunakan=fitur_final_digunakan,
    )
    
@router.post("/predict-trajectory", response_model=TrajectoryResponse)
def predict_trajectory(payload: PredictRequest, db: Session = Depends(get_session)):
    """Prediksi tiap bulan setelah data produksi terakhir hingga sebelum bulan target (tanpa memanggil GEE)."""
    if payload.kabupaten not in KABUPATEN_LIST:
        raise HTTPException(status_code=400, detail=f"Kabupaten '{payload.kabupaten}' tidak dikenali.")

    kosong = TrajectoryResponse(kabupaten=payload.kabupaten, titik=[], bulan_dilewati=[])

    riwayat = get_riwayat_produksi(payload.kabupaten)
    if not riwayat:
        return kosong

    terakhir = riwayat[-1]
    idx_mulai = terakhir["tahun"] * 12 + terakhir["bulan"]   # bulan pertama setelah data produksi terakhir
    idx_target = payload.tahun * 12 + payload.bulan - 1

    if idx_target <= idx_mulai:
        return kosong
    if idx_target - idx_mulai > 36:
        raise HTTPException(status_code=422, detail="Rentang prediksi terlalu panjang (maksimum 36 bulan).")

    data = get_index_map(db, payload.kabupaten)
    baris, kunci_bulan, dilewati = [], [], []

    for idx in range(idx_mulai, idx_target):
        t, b = idx // 12, idx % 12 + 1
        t1, b1 = bulan_sebelumnya(t, b, 1)
        t2, b2 = bulan_sebelumnya(t, b, 2)

        if (t, b) not in data or (t1, b1) not in data or (t2, b2) not in data:
            dilewati.append(f"{b:02d}/{t}")
            continue

        historis_df = pd.DataFrame([data[(t2, b2)], data[(t1, b1)]])
        baris.append(build_feature_row(payload.kabupaten, b, data[(t, b)], historis_df))
        kunci_bulan.append((t, b))

    prediksi = predict_batch(baris) if baris else []

    return TrajectoryResponse(
        kabupaten=payload.kabupaten,
        titik=[
            TitikTrajectory(tahun=t, bulan=b, prediksi_produksi_ton=p)
            for (t, b), p in zip(kunci_bulan, prediksi)
        ],
        bulan_dilewati=dilewati,
    )