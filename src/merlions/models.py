"""Pydantic models shared across agents and tools."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Stall(BaseModel):
    """A hawker stall recommendation."""

    name: str
    centre: str
    cuisine: str
    signature_dish: str
    distance_m: int
    source: str = Field(description="Citation key, e.g. menu_index/satay-bay/2026-06-13")


class PSIReading(BaseModel):
    """A PSI reading from NEA-style data."""

    region: Literal["north", "south", "east", "west", "central"]
    psi: int
    band: Literal["Good", "Moderate", "Unhealthy", "Very Unhealthy", "Hazardous"]
    timestamp: datetime
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    source: str


class Joke(BaseModel):
    """A safe, on-tone joke from the Wisecracker."""

    text: str
    style: Literal["pun", "observation", "wordplay"]
    safe: bool = True


class AgentReply(BaseModel):
    """Composed reply from a single agent."""

    agent_id: str
    summary: str
    citations: list[str] = Field(default_factory=list)
    latency_ms: int = 0


class RouterReply(BaseModel):
    """Final composed reply from the router."""

    parts: list["AgentReply"]
    total_latency_ms: int
    trace_id: str


class InvalidInput(ValueError):
    """Raised when an agent or tool gets unusable input. Fails closed."""
