from fastapi import APIRouter
from app.api.v1.creator.router import creator_router
from app.api.v1.pro.router import pro_router
from app.api.v1.pro.dossiers import router as dossiers_router

api_v1_router = APIRouter()

# Rotas do App de Criadores: /api/v1/creator/*
api_v1_router.include_router(creator_router, prefix="/creator")

# Rotas do Portal Pro A&R: /api/v1/pro/*
api_v1_router.include_router(pro_router, prefix="/pro")

# Rota dedicada de Dossiês e Análise Assíncrona: /api/v1/dossiers/*
api_v1_router.include_router(
    dossiers_router,
    prefix="/dossiers",
    tags=["Pro A&R - Dossiers & AI Intelligence"],
)
