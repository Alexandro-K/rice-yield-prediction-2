import json
from pathlib import Path
import ee
from app.core.config import DATA_DIR

GEOM_DIR = DATA_DIR / "geometries"

_aoi_cache = {}
_sawah_cache = {}


def _load_geojson_as_ee_geometry(path: Path) -> ee.Geometry:
    with open(path) as f:
        geojson_data = json.load(f)

    geoms = [feature["geometry"] for feature in geojson_data["features"]]
    if len(geoms) == 1:
        return ee.Geometry(geoms[0])
    return ee.Geometry.MultiPolygon(
        [g["coordinates"] for g in geoms if g["type"] == "Polygon"]
    )


def get_aoi(kabupaten: str) -> ee.Geometry:
    if kabupaten not in _aoi_cache:
        path = GEOM_DIR / f"{kabupaten}_batas.geojson"
        _aoi_cache[kabupaten] = _load_geojson_as_ee_geometry(path)
    return _aoi_cache[kabupaten]


def get_sawah_mask(kabupaten: str) -> ee.Geometry:
    if kabupaten not in _sawah_cache:
        path = GEOM_DIR / f"{kabupaten}_sawah.geojson"
        _sawah_cache[kabupaten] = _load_geojson_as_ee_geometry(path)
    return _sawah_cache[kabupaten]