from fastapi import APIRouter, HTTPException

from app.schemas.insight_schema import InterpretRequest, InterpretResponse
from app.services import insight_service as svc

router = APIRouter()

@router.post("/interpret", response_model=InterpretResponse)
def interpret_hasil(payload: InterpretRequest):
    if not svc.kabupaten_tersedia(payload.kabupaten):
        raise HTTPException(status_code=400, detail=f"Kabupaten '{payload.kabupaten}' tidak dikenali.")
    if not 1 <= payload.bulan <= 12:
        raise HTTPException(status_code=400, detail="Bulan harus bernilai 1 sampai 12.")

    kategori_prod, batas_prod, sumber_prod = svc.klasifikasi_produksi(
        payload.kabupaten, payload.bulan, payload.prediksi_produksi_ton
    )
    kat_ndvi, batas_ndvi, desk_ndvi = svc.klasifikasi_vegetasi(payload.kabupaten, "NDVI", payload.ndvi_mean)
    kat_evi, batas_evi, desk_evi = svc.klasifikasi_vegetasi(payload.kabupaten, "EVI", payload.evi_mean)
    kat_savi, batas_savi, desk_savi = svc.klasifikasi_vegetasi(payload.kabupaten, "SAVI", payload.savi_mean)

    rata_bulan, selisih = svc.bandingkan_musiman(payload.kabupaten, payload.bulan, payload.prediksi_produksi_ton)

    narasi = svc.susun_narasi(
        payload.kabupaten, payload.tahun, payload.bulan, payload.prediksi_produksi_ton,
        kategori_prod, sumber_prod, rata_bulan, selisih,
        payload.ndvi_mean, kat_ndvi, desk_ndvi,
        payload.evi_mean, kat_evi, desk_evi,
        payload.savi_mean, kat_savi, desk_savi,
    )

    return InterpretResponse(
        kategori_produksi=kategori_prod,
        batas_produksi=batas_prod,
        sumber_batas_produksi=sumber_prod,
        rata_rata_bulan_sama_ton=rata_bulan,
        selisih_persen_vs_musiman=selisih,
        ndvi={"kategori": kat_ndvi, "batas": batas_ndvi, "deskripsi": desk_ndvi},
        evi={"kategori": kat_evi, "batas": batas_evi, "deskripsi": desk_evi},
        savi={"kategori": kat_savi, "batas": batas_savi, "deskripsi": desk_savi},
        narasi=narasi,
        riwayat_produksi=svc.get_riwayat_produksi(payload.kabupaten),
    )

@router.get("/model-info")
def informasi_model():
    return svc.get_model_insight()