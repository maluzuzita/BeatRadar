from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SampleRiskStatus(str, Enum):
    CLEARED = "CLEARED"
    POTENTIAL_SAMPLE = "POTENTIAL_SAMPLE"
    UNLICENSED_SAMPLE = "UNLICENSED_SAMPLE"
    PENDING_SCAN = "PENDING_SCAN"


class SocialPlatform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    SOUNDCLOUD = "soundcloud"


class ArtistSocialHandles(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tiktok: Optional[str] = Field(None, example="@mc_pedrinho_original")
    instagram: Optional[str] = Field(None, example="@mcpedrinho")
    spotify_id: Optional[str] = Field(None, example="4Yv4mG0Q4R6L3B2X8T")


class ArtistBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str = Field(..., max_length=255, example="DJ GBR")
    avatar_url: Optional[str] = Field(None, example="https://assets.beatradar.io/avatars/dj-gbr.jpg")
    country_code: str = Field(default="BR", max_length=2, example="BR")
    genres: List[str] = Field(default_factory=list, example=["Funk MTG", "Phonk", "Brazilian Bass"])
    is_verified: bool = Field(default=False)
    monthly_listeners: int = Field(default=0, example=1850000)
    handles: ArtistSocialHandles = Field(default_factory=ArtistSocialHandles)


class SampleDetectionBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    detected: bool = Field(..., description="Indica se foi detectado sample na faixa")
    original_title: Optional[str] = Field(None, example="Sweet Dreams (Are Made of This)")
    original_artist: Optional[str] = Field(None, example="Eurythmics")
    sample_type: Optional[str] = Field(None, example="interpolation")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, example=0.94)


class HotPickMetrics(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tiktok_creations_count: int = Field(default=0, example=87400, description="Número de vídeos criados com este áudio")
    estimated_views_reach: int = Field(default=0, example=24500000, description="Alcance estimado em visualizações")
    streams_velocity_delta: float = Field(default=0.0, example=340.5, description="Variação percentual de streams nas últimas 48h")
    shares_count: int = Field(default=0, example=15200)


class HotPickTrackItem(BaseModel):
    """
    Contrato de cada aposta quente (Hot Pick) retornada no feed do Radar de Criadores.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID = Field(..., description="Identificador único da faixa")
    title: str = Field(..., example="MTG - Quem Não Quer Sou Eu", max_length=255)
    isrc: Optional[str] = Field(None, example="BR-ABC-24-00123")
    audio_preview_url: Optional[str] = Field(
        None,
        example="https://assets.beatradar.io/audio/previews/preview-uuid.mp3",
        description="URL do trecho viral em alta fidelidade"
    )
    duration_seconds: Optional[int] = Field(None, example=142)
    bpm: Optional[float] = Field(None, example=130.0)
    key_signature: Optional[str] = Field(None, example="F# Minor")
    cover_art_url: Optional[str] = Field(
        None,
        example="https://assets.beatradar.io/covers/cover-uuid.jpg"
    )

    # Métricas de Radar & Inteligência
    virality_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        example=94.8,
        description="Score algorítmico do BeatRadar indicando probabilidade de estouro nacional/global"
    )
    velocity_score: float = Field(
        ...,
        example=280.4,
        description="Aceleração percentual de viralidade nas últimas 24-48h"
    )
    predicted_peak_window: str = Field(
        default="Next 7-14 days",
        example="Next 3-7 days",
        description="Janela de tempo estimada pela IA para o pico de popularidade"
    )
    primary_platform: SocialPlatform = Field(
        default=SocialPlatform.TIKTOK,
        example=SocialPlatform.TIKTOK,
        description="Plataforma de tração inicial mais expressiva"
    )
    trending_platforms: List[SocialPlatform] = Field(
        default_factory=lambda: [SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM],
        example=[SocialPlatform.TIKTOK, SocialPlatform.INSTAGRAM]
    )
    sample_risk: SampleRiskStatus = Field(
        default=SampleRiskStatus.CLEARED,
        example=SampleRiskStatus.POTENTIAL_SAMPLE,
        description="Status de conformidade de direitos autorais e samples"
    )
    sample_intel: Optional[SampleDetectionBrief] = None
    ai_curator_note: Optional[str] = Field(
        None,
        example="Faixa ganhando tração exponencial em reels de dança; pico de engajamento previsto para o próximo fim de semana."
    )

    # Detalhes do Artista e Métricas
    artist: ArtistBrief
    metrics: HotPickMetrics
    created_at: datetime


class HotPicksQueryFilter(BaseModel):
    """
    Parâmetros de consulta e filtros para o endpoint de Apostas Quentes.
    """
    model_config = ConfigDict(extra="forbid")

    genre: Optional[str] = Field(None, example="Funk MTG", description="Filtrar por gênero musical")
    min_virality_score: float = Field(default=70.0, ge=0.0, le=100.0, description="Corte mínimo de score")
    platform: Optional[SocialPlatform] = Field(None, description="Filtrar por plataforma de tração")
    limit: int = Field(default=20, ge=1, le=100, description="Quantidade de faixas por página")
    cursor: Optional[str] = Field(None, description="Cursor opaco para paginação contínua (keyset pagination)")


class HotPicksResponse(BaseModel):
    """
    Envelope de resposta estruturado para GET /api/v1/creator/radar/hot-picks.
    """
    model_config = ConfigDict(from_attributes=True)

    items: List[HotPickTrackItem] = Field(..., description="Lista de faixas no radar de apostas quentes")
    total_returned: int = Field(..., example=20)
    has_more: bool = Field(..., example=True)
    next_cursor: Optional[str] = Field(None, example="eyJ2aXJhbGl0eV9zY29yZSI6IDg5LjMsICJpZCI6ICJ1dWlkIn0=")
    cached: bool = Field(default=False, description="Indica se a resposta veio do Redis 7.2")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

