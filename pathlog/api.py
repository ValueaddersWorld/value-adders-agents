"""FastAPI router exposing the PathLog prototype service."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .models import (
    CaptureEventRequest,
    CaptureEventResponse,
    ConsentRequest,
    ConsentResponse,
    ConnectToolRequest,
    ConnectToolResponse,
    ExportResponse,
    ImportRequest,
    ImportResponse,
    RotateKeyRequest,
    RotateKeyResponse,
    StatsResponse,
    TimelineEntry,
    TimelineResponse,
)
from .service import PathLogService

app = FastAPI(
    title="PathLog Prototype",
    description="Encrypted memory kernel for Value Adders agents.",
    version="0.1.0",
)

service = PathLogService()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "PathLog prototype is running.",
        "docs": "/docs",
        "health": "/healthz",
    }


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/consent", response_model=ConsentResponse)
def consent(request: ConsentRequest) -> ConsentResponse:
    try:
        result = service.register_user(
            email=request.email,
            accept_terms=request.accept_terms,
            passphrase=request.passphrase,
            alias=request.alias,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ConsentResponse(
        user_id=result["user_id"],
        key_id=result["key_id"],
        key_file=result["key_file_path"],
        message="Vault created and master key generated.",
    )


@app.post("/connect", response_model=ConnectToolResponse)
def connect_tool(request: ConnectToolRequest) -> ConnectToolResponse:
    try:
        tools = service.connect_tool(request.user_id, request.tool_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    return ConnectToolResponse(user_id=request.user_id, connected_tools=tools)


@app.post("/capture", response_model=CaptureEventResponse)
def capture_event(request: CaptureEventRequest) -> CaptureEventResponse:
    try:
        result = service.capture_event(
            user_id=request.user_id,
            tool_name=request.tool_name,
            prompt=request.prompt,
            response=request.response,
            metadata=request.metadata,
            passphrase=request.passphrase,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CaptureEventResponse(event_id=result["event_id"], stored_at=result["stored_at"])


@app.get("/timeline/{user_id}", response_model=TimelineResponse)
def timeline(user_id: str, passphrase: str | None = None) -> TimelineResponse:
    try:
        events = service.fetch_timeline(user_id, passphrase)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    entries = [
        TimelineEntry(
            event_id=item["event_id"],
            timestamp=item["timestamp"],
            tool_name=item["tool_name"],
            prompt=item["prompt"],
            response=item["response"],
            metadata=item.get("metadata", {}),
        )
        for item in events
    ]
    return TimelineResponse(user_id=user_id, events=entries)


@app.get("/stats/{user_id}", response_model=StatsResponse)
def stats(user_id: str, passphrase: str | None = None) -> StatsResponse:
    try:
        result = service.stats(user_id, passphrase)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return StatsResponse(**result)


@app.post("/export", response_model=ExportResponse)
def export_bundle(request: RotateKeyRequest) -> ExportResponse:
    try:
        bundle = service.export_bundle(request.user_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    return ExportResponse(user_id=request.user_id, bundle=bundle)


@app.post("/import", response_model=ImportResponse)
def import_bundle(request: ImportRequest) -> ImportResponse:
    result = service.import_bundle(request.bundle, request.target_user_id)
    return ImportResponse(**result)


@app.post("/rotate-key", response_model=RotateKeyResponse)
def rotate_key(request: RotateKeyRequest) -> RotateKeyResponse:
    try:
        result = service.rotate_key(request.user_id, request.passphrase)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RotateKeyResponse(**result)


@app.post("/backup", response_model=ExportResponse)
def backup(request: RotateKeyRequest) -> ExportResponse:
    """Alias for /export for clarity."""
    return export_bundle(request)


@app.post("/restore", response_model=ImportResponse)
def restore(request: ImportRequest) -> ImportResponse:
    """Alias for /import."""
    return import_bundle(request)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("pathlog.api:app", host="0.0.0.0", port=8002, reload=False)
