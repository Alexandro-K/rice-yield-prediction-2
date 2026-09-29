import json
import ee
from app.core.config import GEE_PROJECT_ID, GEE_SERVICE_ACCOUNT_JSON, GEE_SERVICE_ACCOUNT_JSON_CONTENT
import threading
import tempfile

_gee_lock = threading.Lock()
CLOUD_PROB_THRESHOLD = 40


def init_gee():
    if not GEE_SERVICE_ACCOUNT_JSON_CONTENT and not GEE_SERVICE_ACCOUNT_JSON:
        raise RuntimeError(
            "Kredensial GEE tidak ditemukan. Pastikan environment variable "
            "GEE_SERVICE_ACCOUNT_JSON_CONTENT (untuk deployment) atau "
            "GEE_SERVICE_ACCOUNT_JSON (untuk lokal) sudah diset dengan benar."
        )

    if GEE_SERVICE_ACCOUNT_JSON_CONTENT:
        key_data = json.loads(GEE_SERVICE_ACCOUNT_JSON_CONTENT)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            json.dump(key_data, tmp)
            key_path = tmp.name
    else:
        with open(GEE_SERVICE_ACCOUNT_JSON) as f:
            key_data = json.load(f)
        key_path = GEE_SERVICE_ACCOUNT_JSON

    service_account_email = key_data["client_email"]
    credentials = ee.ServiceAccountCredentials(service_account_email, key_path)
    ee.Initialize(credentials, project=GEE_PROJECT_ID)
    print(f"GEE terautentikasi sebagai: {service_account_email}")

def get_s2_sr_cloud_collection(aoi, start_date, end_date, max_cloudy_pct=90):
    s2_sr = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', max_cloudy_pct))
    )
    s2_cloud_prob = (
        ee.ImageCollection('COPERNICUS/S2_CLOUD_PROBABILITY')
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
    )
    return ee.Join.saveFirst('cloud_prob').apply(
        primary=s2_sr,
        secondary=s2_cloud_prob,
        condition=ee.Filter.equals(leftField='system:index', rightField='system:index'),
    )


def mask_clouds_s2cloudless(image):
    cloud_prob = ee.Image(image.get('cloud_prob')).select('probability')
    is_cloud = cloud_prob.gt(CLOUD_PROB_THRESHOLD)
    return image.updateMask(is_cloud.Not()).divide(10000).copyProperties(image, ['system:time_start'])


def build_monthly_composite(aoi, year, month):
    month_start = ee.Date.fromYMD(year, month, 1)
    month_end = month_start.advance(1, 'month')
    joined = get_s2_sr_cloud_collection(aoi, month_start, month_end)
    collection = ee.ImageCollection(joined).map(mask_clouds_s2cloudless)
    n_images = collection.size()
    composite = collection.median().clip(aoi)
    return composite, n_images


def add_vegetation_indices(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    evi = image.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {'NIR': image.select('B8'), 'RED': image.select('B4'), 'BLUE': image.select('B2')}
    ).rename('EVI')
    L = 0.5
    savi = image.expression(
        '((NIR - RED) / (NIR + RED + L)) * (1 + L)',
        {'NIR': image.select('B8'), 'RED': image.select('B4'), 'L': L}
    ).rename('SAVI')
    return image.addBands([ndvi, evi, savi])


def get_monthly_composite_with_indices(aoi, year, month):
    composite, n_images = build_monthly_composite(aoi, year, month)
    composite_indexed = add_vegetation_indices(composite)
    return composite_indexed, n_images


from app.services.geometry_service import get_aoi, get_sawah_mask

def extract_monthly_stats_for_kabupaten(kabupaten: str, year: int, month: int) -> dict:
    with _gee_lock:
        aoi = get_aoi(kabupaten)
        sawah_mask_geom = get_sawah_mask(kabupaten)
        sawah_mask_image = ee.Image.constant(1).clip(sawah_mask_geom)

        composite, n_images = get_monthly_composite_with_indices(aoi, year, month)
        composite_masked = composite.updateMask(sawah_mask_image)

        stats = composite_masked.select(['NDVI', 'EVI', 'SAVI']).reduceRegion(
            reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), sharedInputs=True)
                     .combine(ee.Reducer.count(), sharedInputs=True),
            geometry=aoi,
            scale=10,
            maxPixels=1e9,
        )

        result = stats.getInfo()
        result["n_images"] = n_images.getInfo()
        return result