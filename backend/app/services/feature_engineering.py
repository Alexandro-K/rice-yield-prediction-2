import numpy as np
import pandas as pd
from app.core.config import FITUR_INDEX, KOLOM_KABUPATEN, KABUPATEN_LIST


def build_month_sin_cos(bulan: int):
    bulan_sin = np.sin(2 * np.pi * bulan / 12)
    bulan_cos = np.cos(2 * np.pi * bulan / 12)
    return bulan_sin, bulan_cos


def build_kabupaten_dummy(kabupaten: str) -> dict:
    dummy = {col: 0 for col in KOLOM_KABUPATEN}
    col_name = f"Kab_{kabupaten}"
    if col_name in dummy:
        dummy[col_name] = 1
    return dummy


def build_feature_row(kabupaten: str, bulan: int, index_bulan_ini: dict, historis_df: pd.DataFrame) -> dict:
    """
    index_bulan_ini: {'NDVI_mean': ..., 'EVI_mean': ..., 'SAVI_mean': ...} hasil extract_monthly_stats
    historis_df: dataframe historis kabupaten terkait, sudah terurut berdasarkan tanggal,
                 minimal berisi 2 bulan sebelum bulan yang diprediksi
    """
    fitur = {}
    for col in FITUR_INDEX:
        fitur[col] = index_bulan_ini[col]

    lag1 = historis_df.iloc[-1]
    lag2 = historis_df.iloc[-2]

    for col in FITUR_INDEX:
        fitur[f"{col}_lag1"] = lag1[col]
        fitur[f"{col}_lag2"] = lag2[col]
        fitur[f"{col}_delta1"] = fitur[col] - lag1[col]
        fitur[f"{col}_trend"] = lag1[col] - lag2[col]

    roll_window = pd.concat([historis_df[FITUR_INDEX].tail(2), pd.DataFrame([index_bulan_ini])])
    for col in FITUR_INDEX:
        fitur[f"{col}_roll3"] = roll_window[col].mean()

    bulan_sin, bulan_cos = build_month_sin_cos(bulan)
    fitur["Bulan_sin"] = bulan_sin
    fitur["Bulan_cos"] = bulan_cos

    fitur.update(build_kabupaten_dummy(kabupaten))

    return fitur