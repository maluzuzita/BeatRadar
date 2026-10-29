from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class DealStatus(str, Enum):
    SCOUTING = "scouting"
    CONTACT_MADE = "contact_made"
    OFFER_SENT = "offer_sent"
    NEGOTIATION = "negotiation"
    SIGNED = "signed"
    PASSED = "passed"


class DealCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artist_id: UUID
    track_id: Optional[UUID] = None
    status: DealStatus = DealStatus.SCOUTING
    valuation_estimate: Optional[float] = Field(None, ge=0.0)
    offered_advance: Optional[float] = Field(None, ge=0.0)
    royalty_rate_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    contract_terms: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None


class DealUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Optional[DealStatus] = None
    valuation_estimate: Optional[float] = Field(None, ge=0.0)
    offered_advance: Optional[float] = Field(None, ge=0.0)
    royalty_rate_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    contract_terms: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class DealItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    artist_id: UUID
    track_id: Optional[UUID] = None
    created_by: UUID
    status: DealStatus
    valuation_estimate: Optional[float] = None
    offered_advance: Optional[float] = None
    royalty_rate_percentage: Optional[float] = None
    contract_terms: Dict[str, Any]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DossierDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    artist_id: UUID
    track_id: Optional[UUID] = None
    executive_summary: str
    ai_insights: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    market_fit_score: float = Field(..., ge=0.0, le=100.0)
    version: int
    generated_at: datetime


class DossierJobStatus(str, Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DossierAnalyzeResponse(BaseModel):
    """
    Resposta retornada no disparo assíncrono de análise de dossiê (202 Accepted).
    """
    model_config = ConfigDict(from_attributes=True)

    job_id: str = Field(..., example="8d98606c-8473-4556-9a2c-eec4e47bc2a1")
    track_id: UUID
    status: DossierJobStatus = DossierJobStatus.QUEUED
    message: str = Field(
        default="Análise de inteligência A&R enfileirada para processamento assíncrono.",
        example="Análise de inteligência A&R enfileirada para processamento assíncrono."
    )
    websocket_url: str = Field(
        ...,
        example="/api/v1/dossiers/ws/8d98606c-8473-4556-9a2c-eec4e47bc2a1",
        description="URL de WebSocket para acompanhamento de progresso em tempo real"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DossierJobProgress(BaseModel):
    """
    Mensagem de progresso transmitida via WebSocket / Polling.
    """
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    track_id: Optional[str] = None
    step: str = Field(..., example="SOCIAL_METRICS")
    progress: int = Field(..., ge=0, le=100, example=35)
    status: DossierJobStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message: Optional[str] = None
    dossier_id: Optional[str] = None
    market_fit_score: Optional[float] = None
    error: Optional[str] = None
