from fastapi import APIRouter
from app.api.v1.pro import ar

pro_router = APIRouter()
pro_router.include_router(ar.router, prefix="/ar", tags=["Pro A&R - Intelligence & Deals"])

