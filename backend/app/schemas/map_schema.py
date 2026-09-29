from pydantic import BaseModel
from typing import Any


class MapLayerRequest(BaseModel):
    kabupaten: str
    tahun: int
    bulan: int
    layer: str = "NDVI"  # pilihan: NDVI, EVI, SAVI, RGB

class MapLayerResponse(BaseModel):
    kabupaten: str
    tile_url: str
    batas_geojson: dict[str, Any]
    sawah_geojson: dict[str, Any]
    center_lat: float
    center_lon: float
    jumlah_citra: int