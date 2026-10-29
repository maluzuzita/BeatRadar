from fastapi import APIRouter
from app.api.v1.creator import radar

creator_router = APIRouter()
creator_router.include_router(radar.router, prefix="/radar", tags=["Creator - Music Radar"])

