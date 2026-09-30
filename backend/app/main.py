from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.services.gee_pipeline import init_gee
from app.services.model_service import load_model
from app.api.routes_predict import router as predict_router
from app.api.routes_map import router as map_router
from app.api.routes_insight import router as insight_router

app = FastAPI(title="Prediksi Produksi Padi API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=r"https://rice-yield-prediction-2-two.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(predict_router, prefix="/api")
app.include_router(map_router, prefix="/api")
app.include_router(insight_router, prefix="/api")

from app.scripts.seed_database import seed

@app.on_event("startup")
def on_startup():
    init_db()
    seed()
    init_gee()
    load_model()
    print("Aplikasi siap: database, GEE, dan model TabPFN sudah diinisialisasi.")

@app.get("/")
@app.head("/")
def health_check():
    return {"status": "ok"}