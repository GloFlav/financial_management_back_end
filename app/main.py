from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import Base, engine
from app.models import wallet, transaction  # noqa: F401 — enregistre les modèles
from app.models import fixed_charge, provisional_expense  # noqa: F401
from app.models import user_settings as _user_settings_model  # noqa: F401
from app.routers.finance import router as finance_router
from app.seed import seed

Base.metadata.create_all(bind=engine)

# Migration douce : ajouter la colonne attachment si elle n'existe pas encore
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS attachment TEXT"))
        conn.commit()
except Exception:
    pass  # Certains backends SQL ne supportent pas IF NOT EXISTS — on ignore silencieusement

# Seed user_settings par défaut
try:
    from app.database import SessionLocal
    from app.models.user_settings import UserSetting
    _db = SessionLocal()
    defaults = {
        "monthly_salary":             2_500_000,
        "monthly_savings_goal":       1_000_000,
        "exceptional_savings_amount": 0,
        "exceptional_savings_month":  0,
        "savings_wallet_id":          0,
        "current_savings_balance":    0,
    }
    for key, value in defaults.items():
        if not _db.query(UserSetting).filter(UserSetting.key == key).first():
            _db.add(UserSetting(key=key, value=value))
    _db.commit()
    _db.close()
except Exception:
    pass

seed()

app = FastAPI(title="Financial Management API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(finance_router)

@app.get("/health")
def health():
    return {"status": "ok"}
