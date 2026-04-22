import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine, SessionLocal
from .models import Base, Territory, User
from .routers import leads, territories, whatsapp, ai_agent, dashboard, auth as auth_router
from .services.auth_service import create_user, get_user_by_username


SEED_TERRITORIES = [
    {
        "name": "São Paulo - Capital",
        "description": "Região metropolitana de São Paulo",
        "color": "#3B82F6",
        "responsible_agent": "Equipe SP",
        "polygon": json.dumps([
            [-23.3567, -46.8259], [-23.3567, -46.3654],
            [-23.8000, -46.3654], [-23.8000, -46.8259],
        ]),
    },
    {
        "name": "Rio de Janeiro",
        "description": "Região metropolitana do Rio de Janeiro",
        "color": "#10B981",
        "responsible_agent": "Equipe RJ",
        "polygon": json.dumps([
            [-22.7462, -43.7958], [-22.7462, -43.1003],
            [-23.0820, -43.1003], [-23.0820, -43.7958],
        ]),
    },
    {
        "name": "Minas Gerais - BH",
        "description": "Belo Horizonte e região metropolitana",
        "color": "#F59E0B",
        "responsible_agent": "Equipe BH",
        "polygon": json.dumps([
            [-19.7942, -44.0621], [-19.7942, -43.8694],
            [-20.0522, -43.8694], [-20.0522, -44.0621],
        ]),
    },
    {
        "name": "Rio Grande do Sul",
        "description": "Porto Alegre e região",
        "color": "#EF4444",
        "responsible_agent": "Equipe RS",
        "polygon": json.dumps([
            [-29.8240, -51.3196], [-29.8240, -50.9154],
            [-30.2860, -50.9154], [-30.2860, -51.3196],
        ]),
    },
    {
        "name": "Bahia - Salvador",
        "description": "Salvador e região metropolitana",
        "color": "#8B5CF6",
        "responsible_agent": "Equipe BA",
        "polygon": json.dumps([
            [-12.7762, -38.6614], [-12.7762, -38.2897],
            [-13.0794, -38.2897], [-13.0794, -38.6614],
        ]),
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Territory).count() == 0:
            for t in SEED_TERRITORIES:
                db.add(Territory(**t))
            db.commit()
        # Seed default admin user
        if not get_user_by_username(db, "admin"):
            create_user(db, username="admin", password="admin123",
                        full_name="Administrador", email="admin@leadplatform.com", is_admin=True)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Plataforma de Captação de Leads com Inteligência Territorial",
    description="MVP – Automação de leads com IA e WhatsApp",
    version="1.0.0",
    lifespan=lifespan,
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(leads.router)
app.include_router(territories.router)
app.include_router(whatsapp.router)
app.include_router(ai_agent.router)
app.include_router(dashboard.router)
app.include_router(auth_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "Lead Platform API"}
