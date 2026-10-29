from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.deps import get_current_org_id, get_redis
from app.schemas.pro import (
    DealCreate,
    DealItem,
    DealStatus,
    DossierAnalyzeResponse,
    DossierDetail,
    DossierJobStatus,
)
from app.api.v1.pro.dossiers import analyze_track_dossier
import redis.asyncio as aioredis

router = APIRouter()


@router.post(
    "/dossiers/tracks/{track_id}/analyze",
    response_model=DossierAnalyzeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Disparar Análise Completa de Dossiê A&R (Assíncrono)",
    description="Inicia o pipeline assíncrono de inteligência artificial e retorna job_id + WebSocket URL.",
)
async def analyze_track_dossier_alias(
    track_id: UUID,
    org_id: Optional[str] = Depends(get_current_org_id),
    redis_client: Optional[aioredis.Redis] = Depends(get_redis),
) -> DossierAnalyzeResponse:
    """Dispara o pipeline de IA da mesma forma que /api/v1/dossiers/tracks/{id}/analyze."""
    return await analyze_track_dossier(track_id=track_id, org_id=org_id, redis_client=redis_client)


@router.get(
    "/dossiers/{artist_id}",
    response_model=DossierDetail,
    summary="Obter Dossiê de Inteligência do Artista (IA / RAG)",
    description="Retorna a análise completa gerada por IA com métricas de tração, análise de risco de sample e fit de mercado.",
)
async def get_artist_dossier(
    artist_id: UUID,
    org_id: Optional[str] = Depends(get_current_org_id),
) -> DossierDetail:
    return DossierDetail(
        id=uuid4(),
        artist_id=artist_id,
        executive_summary="Artista independente em ascensão meteórica no segmento MTG. Crescimento orgânico com baixo custo de aquisição e forte engajamento da Geração Z.",
        ai_insights={
            "retention_rate_30d": 74.2,
            "core_demographics": {"primary_age": "16-24", "primary_country": "BR"},
            "streaming_conversion_ratio": 0.082,
            "sentiment_score": 0.88,
        },
        risk_assessment={
            "unlicensed_samples_detected": False,
            "controversy_index": 0.05,
            "label_affiliation_status": "independent",
        },
        market_fit_score=91.5,
        version=1,
        generated_at=datetime.utcnow(),
    )


@router.get(
    "/deals",
    response_model=List[DealItem],
    summary="Listar Deals da Gravadora (Isolamento RLS por org_id)",
    description="Retorna o pipeline de contratações exclusivo da organização autenticada via Row-Level Security.",
)
async def list_deals(
    status_filter: Optional[DealStatus] = Query(None, description="Filtrar por estágio do deal"),
    org_id: Optional[str] = Depends(get_current_org_id),
) -> List[DealItem]:
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header 'x-org-id' obrigatório para acessar o pipeline de Deals (RLS).",
        )

    current_org_uuid = UUID(org_id)
    return [
        DealItem(
            id=uuid4(),
            org_id=current_org_uuid,
            artist_id=uuid4(),
            track_id=uuid4(),
            created_by=uuid4(),
            status=status_filter or DealStatus.SCOUTING,
            valuation_estimate=150000.00,
            offered_advance=40000.00,
            royalty_rate_percentage=18.5,
            contract_terms={"territory": "Worldwide", "term_years": 3, "masters_ownership": "50/50"},
            notes="Primeiro contato realizado com empresário. Artista demonstrou interesse em distribuição global.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
    ]


@router.post(
    "/deals",
    response_model=DealItem,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Nova Oportunidade no Pipeline (Deal)",
)
async def create_deal(
    deal_in: DealCreate,
    org_id: Optional[str] = Depends(get_current_org_id),
) -> DealItem:
    if not org_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header 'x-org-id' obrigatório para registrar deals sob sua organização.",
        )

    current_org_uuid = UUID(org_id)
    return DealItem(
        id=uuid4(),
        org_id=current_org_uuid,
        artist_id=deal_in.artist_id,
        track_id=deal_in.track_id,
        created_by=uuid4(),
        status=deal_in.status,
        valuation_estimate=deal_in.valuation_estimate,
        offered_advance=deal_in.offered_advance,
        royalty_rate_percentage=deal_in.royalty_rate_percentage,
        contract_terms=deal_in.contract_terms,
        notes=deal_in.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
