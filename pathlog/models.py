"""Pydantic models for the PathLog API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ConsentRequest(BaseModel):
    email: str = Field(..., description="Primary user email for contact")
    accept_terms: bool = Field(..., description="User consent acknowledgement")
    passphrase: Optional[str] = Field(None, description="Optional vault unlock passphrase")
    alias: Optional[str] = Field(None, description="Human readable identifier")

    @validator("email")
    def _validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("A valid email address is required")
        return value.lower().strip()


class ConsentResponse(BaseModel):
    user_id: str
    key_id: str
    key_file: str
    message: str


class ConnectToolRequest(BaseModel):
    user_id: str
    tool_name: str


class ConnectToolResponse(BaseModel):
    user_id: str
    connected_tools: List[str]


class CaptureEventRequest(BaseModel):
    user_id: str
    tool_name: str
    prompt: str
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    passphrase: Optional[str] = None


class CaptureEventResponse(BaseModel):
    event_id: str
    stored_at: datetime


class TimelineEntry(BaseModel):
    event_id: str
    timestamp: datetime
    tool_name: str
    prompt: str
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineResponse(BaseModel):
    user_id: str
    events: List[TimelineEntry]


class StatsResponse(BaseModel):
    user_id: str
    total_events: int
    by_tool: Dict[str, int]


class ExportResponse(BaseModel):
    user_id: str
    bundle: Dict[str, Any]


class ImportRequest(BaseModel):
    bundle: Dict[str, Any]
    target_user_id: Optional[str] = None


class ImportResponse(BaseModel):
    user_id: str
    imported_events: int


class RotateKeyRequest(BaseModel):
    user_id: str
    passphrase: Optional[str] = None


class RotateKeyResponse(BaseModel):
    user_id: str
    key_id: str
    message: str


__all__ = [
    "ConsentRequest",
    "ConsentResponse",
    "ConnectToolRequest",
    "ConnectToolResponse",
    "CaptureEventRequest",
    "CaptureEventResponse",
    "TimelineResponse",
    "StatsResponse",
    "ExportResponse",
    "ImportRequest",
    "ImportResponse",
    "RotateKeyRequest",
    "RotateKeyResponse",
]
