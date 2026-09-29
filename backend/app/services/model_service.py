import pandas as pd
from tabpfn_client import TabPFNRegressor, set_access_token
from app.core.config import DATA_DIR, FITUR_FINAL, TABPFN_TOKEN, TABPFN_BEST_PARAMS

_model_instance = None


def load_model():
    global _model_instance
    if _model_instance is not None:
        return _model_instance

    set_access_token(TABPFN_TOKEN)

    df_train = pd.read_csv(DATA_DIR / "training_data.csv")
    X_train = df_train[FITUR_FINAL]
    y_train = df_train["Produksi_Ton"]

    model = TabPFNRegressor(**TABPFN_BEST_PARAMS)
    model.fit(X_train.values, y_train.values)

    _model_instance = model
    print(f"TabPFN siap. Dilatih dengan {len(df_train)} baris, {len(FITUR_FINAL)} fitur.")
    return _model_instance


def predict(feature_row: dict) -> float:
    model = load_model()
    df_input = pd.DataFrame([feature_row])[FITUR_FINAL]
    pred = model.predict(df_input.values)
    return float(pred[0])

def predict_batch(feature_rows: list[dict]) -> list[float]:
    model = load_model()
    df_input = pd.DataFrame(feature_rows)[FITUR_FINAL]
    pred = model.predict(df_input.values)
    return [float(p) for p in pred]