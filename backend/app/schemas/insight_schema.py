from typing import Optional
from pydantic import BaseModel


class InterpretRequest(BaseModel):
    kabupaten: str
    tahun: int
    bulan: int
    prediksi_produksi_ton: float
    ndvi_mean: float
    evi_mean: float
    savi_mean: float


class TitikRiwayat(BaseModel):
    tahun: int
    bulan: int
    produksi_ton: float


class KategoriIndeks(BaseModel):
    kategori: str
    batas: dict[str, float]
    deskripsi: str


class InterpretResponse(BaseModel):
    kategori_produksi: str
    batas_produksi: dict[str, float]
    sumber_batas_produksi: str
    rata_rata_bulan_sama_ton: Optional[float] = None
    selisih_persen_vs_musiman: Optional[float] = None
    ndvi: KategoriIndeks
    evi: KategoriIndeks
    savi: KategoriIndeks
    narasi: str
    riwayat_produksi: list[TitikRiwayat]