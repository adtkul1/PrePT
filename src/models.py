from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# -------------------------
# 1) Core slide/presentation models (compatible with existing tests)
# -------------------------

class SlideType(str, Enum):
    TITLE_SLIDE = "title_slide"
    CONTENT_SLIDE = "content_slide"
    TWO_COLUMN = "two_column"
    CLOSING_SLIDE = "closing_slide"


class Citation(BaseModel):
    """
    A pointer to where a claim came from (RAG grounding).
    """
    source_id: str
    chunk_id: str
    quote: Optional[str] = None
    # Optional coordinates for highlighting within a chunk
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class SlideBullet(BaseModel):
    """
    Bullet text + citations supporting it.
    """
    text: str
    citations: List[Citation] = Field(default_factory=list)


class SlideOutline(BaseModel):
    """
    Slide outline structure.
    Keeps compatibility with existing tests expecting .content
    and/or constructing via content=[...].
    """
    model_config = ConfigDict(populate_by_name=True)

    slide_number: int = Field(..., ge=1)
    slide_type: SlideType
    title: str = Field(..., max_length=80)
    subtitle: Optional[str] = Field(None, max_length=100)

    # Accept "content" as input; store canonically as bullet_points
    bullet_points: List[str] = Field(default_factory=list, alias="content")

    # Agent/RAG ready: richer bullets (optional)
    bullets: Optional[List[SlideBullet]] = None

    speaker_notes: Optional[str] = None

    @property
    def content(self) -> List[str]:
        return self.bullet_points

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Slide title cannot be empty")
        return v.strip()

    @field_validator("bullet_points")
    @classmethod
    def validate_bullets(cls, v: List[str]) -> List[str]:
        # Keep this configurable so tests/POCs can pass short bullets
        import os
        min_len = int(os.getenv("MIN_BULLET_LENGTH", "1"))
        for bullet in v or []:
            if len(bullet) > 120:
                raise ValueError(f"Bullet point exceeds 120 characters: {bullet[:50]}...")
            if len(bullet) < min_len:
                raise ValueError(f"Bullet point too short: {bullet}")
        return v


class PresentationOutline(BaseModel):
    """
    Complete presentation outline.
    Derives title from topic and total_slides from slides.
    """
    title: Optional[str] = Field(None, max_length=100)
    topic: str
    target_audience: Optional[str] = None
    key_message: Optional[str] = None

    slides: List[SlideOutline]
    total_slides: Optional[int] = None

    # Traceability hooks for agent + RAG
    trace_id: Optional[str] = None
    retrieval_summary: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.title:
            self.title = self.topic
        self.total_slides = len(self.slides)


# -------------------------
# 2) RAG models (sources, chunks, retrieval)
# -------------------------

class SourceType(str, Enum):
    FILE = "file"
    URL = "url"
    WIKI = "wiki"
    NOTE = "note"
    OTHER = "other"


class DocumentSource(BaseModel):
    """
    A knowledge input to RAG.
    """
    source_id: str
    source_type: SourceType
    display_name: str
    uri: Optional[str] = None  # path or URL
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    """
    A chunk used for retrieval/grounding.
    """
    chunk_id: str
    source_id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    # Optional embeddings reference (don’t store vectors directly)
    embedding_ref: Optional[str] = None


class RetrievalConfig(BaseModel):
    """
    How to retrieve grounding context.
    """
    strategy: Literal["naive_rag", "agentic_rag", "multimodal_rag"] = "naive_rag"
    top_k: int = Field(default=6, ge=1, le=50)
    min_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    filters: Dict[str, Any] = Field(default_factory=dict)
    rerank: bool = False


class RetrievalQuery(BaseModel):
    query: str
    expanded_queries: List[str] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    query: RetrievalQuery
    chunks: List[DocumentChunk] = Field(default_factory=list)
    # Optional scoring map if you want to keep it simple
    scores: Dict[str, float] = Field(default_factory=dict)  # chunk_id -> score


# -------------------------
# 3) Agent orchestration models (plan, tools, trace)
# -------------------------

class ToolCall(BaseModel):
    """
    A record of a tool invocation by an agent step.
    """
    tool_name: str
    input: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    status: Literal["ok", "error", "skipped"] = "ok"
    error: Optional[str] = None


class AgentStep(BaseModel):
    """
    A single reasoning/action step.
    Mirrors the “sequential prompts + memory” agent style described for doc generation agents.
    """
    step_id: str
    name: str
    instruction: str
    prompt: Optional[str] = None
    tool_calls: List[ToolCall] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)  # e.g., extracted_facts, draft_outline
    notes: Optional[str] = None


class AgentConfig(BaseModel):
    """
    Agent behavior knobs.
    """
    enabled: bool = True
    max_steps: int = Field(default=8, ge=1, le=50)
    allow_retrieval_refinement: bool = True
    allow_outline_revision: bool = True


class GenerationTrace(BaseModel):
    """
    End-to-end run trace for debugging/evaluation.
    """
    trace_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

    retrieval: Optional[RetrievalResult] = None
    steps: List[AgentStep] = Field(default_factory=list)

    # Useful for eval
    warnings: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)


# -------------------------
# 4) Request model (user intent + retrieval + agent config)
# -------------------------

class GenerationRequest(BaseModel):
    """
    User request for generation.
    Extends your current request model with RAG & agent knobs.
    """
    topic: str = Field(..., min_length=3, max_length=200)
    num_slides: int = Field(default=4, ge=3, le=20)
    template: str = Field(default="corporate")
    audience: Optional[str] = None
    tone: str = Field(default="professional")
    custom_prompt: Optional[str] = None

    # New: knowledge inputs for RAG
    sources: List[DocumentSource] = Field(default_factory=list)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)

    # New: agent knobs
    agent: AgentConfig = Field(default_factory=AgentConfig)