import json
from fastapi import APIRouter, HTTPException

from app.core.config import KABUPATEN_LIST, DATA_DIR
from app.schemas.map_schema import MapLayerRequest, MapLayerResponse
from app.services.gee_pipeline import get_monthly_composite_with_indices
from app.services.geometry_service import get_aoi
from app.services.gee_pipeline import _gee_lock

router = APIRouter()

VIS_PARAMS = {
    "NDVI": {"min": -0.2, "max": 0.9, "palette": ["red", "yellow", "green"]},
    "EVI": {"min": -0.2, "max": 0.9, "palette": ["red", "yellow", "green"]},
    "SAVI": {"min": -0.2, "max": 0.9, "palette": ["red", "yellow", "green"]},
    "RGB": {"bands": ["B4", "B3", "B2"], "min": 0, "max": 0.3},
}


def _load_geojson_raw(kabupaten: str, jenis: str) -> dict:
    path = DATA_DIR / "geometries" / f"{kabupaten}_{jenis}.geojson"
    with open(path) as f:
        return json.load(f)


def _get_centroid(geojson_data: dict) -> tuple[float, float]:
    coords = geojson_data["features"][0]["geometry"]["coordinates"]
    flat = []

    def _flatten(c):
        if isinstance(c[0], (float, int)):
            flat.append(c)
        else:
            for sub in c:
                _flatten(sub)

    _flatten(coords)
    lons = [c[0] for c in flat]
    lats = [c[1] for c in flat]
    return sum(lats) / len(lats), sum(lons) / len(lons)


@router.post("/map-layer", response_model=MapLayerResponse)
def get_map_layer(payload: MapLayerRequest):
    if payload.kabupaten not in KABUPATEN_LIST:
        raise HTTPException(status_code=400, detail=f"Kabupaten '{payload.kabupaten}' tidak dikenali. Pilihan: {KABUPATEN_LIST}")

    if payload.layer not in VIS_PARAMS:
        raise HTTPException(status_code=400, detail=f"Layer '{payload.layer}' tidak dikenali. Pilihan: {list(VIS_PARAMS.keys())}")

    aoi = get_aoi(payload.kabupaten)
    # di dalam fungsi get_map_layer, bungkus bagian yang manggil ee:
    with _gee_lock:
        composite, n_images = get_monthly_composite_with_indices(aoi, payload.tahun, payload.bulan)

        if payload.layer == "RGB":
            image_to_show = composite
        else:
            image_to_show = composite.select(payload.layer)

        map_id_dict = image_to_show.getMapId(VIS_PARAMS[payload.layer])
        tile_url = map_id_dict["tile_fetcher"].url_format
        jumlah_citra = n_images.getInfo()

    batas_geojson = _load_geojson_raw(payload.kabupaten, "batas")
    sawah_geojson = _load_geojson_raw(payload.kabupaten, "sawah")
    center_lat, center_lon = _get_centroid(batas_geojson)

    return MapLayerResponse(
        kabupaten=payload.kabupaten,
        tile_url=tile_url,
        batas_geojson=batas_geojson,
        sawah_geojson=sawah_geojson,
        center_lat=center_lat,
        center_lon=center_lon,
        jumlah_citra=n_images.getInfo(),
    )