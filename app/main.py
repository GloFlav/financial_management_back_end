import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy import text

from app.database import Base, engine
from app.models import wallet, transaction  # noqa: F401 — enregistre les modèles
from app.models import fixed_charge, provisional_expense  # noqa: F401
from app.models import user_settings as _user_settings_model  # noqa: F401
from app.models import category_budget as _category_budget_model  # noqa: F401
from app.models import action_log as _action_log_model  # noqa: F401
from app.models import occupation_type as _occupation_type_model  # noqa: F401
from app.models import agenda_event as _agenda_event_model  # noqa: F401
from app.routers.finance import router as finance_router
from app.seed import seed
from app.ws_manager import manager

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

# Seed budget par défaut : alimentation = 400 000 Ar
try:
    from app.database import SessionLocal as _SL2
    from app.models.category_budget import CategoryBudget as _CB
    _db2 = _SL2()
    if not _db2.query(_CB).filter(_CB.category == "alimentation").first():
        _db2.add(_CB(category="alimentation", default_amount=400_000))
        _db2.commit()
    _db2.close()
except Exception:
    pass

# Seed occupation types par défaut
try:
    from app.database import SessionLocal as _SL3
    from app.models.occupation_type import OccupationType as _OT
    import json as _json
    _db3 = _SL3()
    if _db3.query(_OT).count() == 0:
        _defaults_occ = [
            _OT(name="Projet perso",  color="#60a5fa", collaborators=_json.dumps(["Guil"])),
            _OT(name="Enseignement",  color="#c084fc", collaborators=_json.dumps([])),
            _OT(name="Hello Soins",   color="#34d399", collaborators=_json.dumps(["Guil","Flavien","Marie","Jo","Dev1","Dev2","Client X","Partenaire"])),
            _OT(name="RH Automation", color="#fbbf24", collaborators=_json.dumps(["Guil","Flavien","Marie","Jo"])),
        ]
        _db3.add_all(_defaults_occ)
        _db3.commit()
    _db3.close()
except Exception:
    pass

app = FastAPI(title="Financial Management API", version="0.1.0")


class BroadcastMiddleware(BaseHTTPMiddleware):
    """Diffuse un refresh WebSocket après chaque mutation réussie."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if request.method in ("POST", "PATCH", "DELETE", "PUT") and response.status_code < 300:
            await manager.broadcast({"type": "refresh"})
        return response


_cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3001,http://localhost:5173").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(BroadcastMiddleware)

app.include_router(finance_router)


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()   # keep-alive — on ignore le contenu
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.get("/health")
def health():
    return {"status": "ok"}
