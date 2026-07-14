"""Server-Sent Events (SSE) progress streaming for generation stages.

Generation stages produce *structured JSON*, so token-by-token streaming would
show JSON assembling, poor UX. Instead we stream coarse but honest progress
events (phase changes + heartbeats) around the real work, so the client shows
live activity and elapsed time instead of a frozen skeleton, and never mistakes
a slow call for a dead one. The final `done` event carries the persisted result;
`error` carries a clear message.

Event format (SSE):
    event: phase   data: {"phase": "calling_model", "label": "Calling the model…"}
    event: heartbeat data: {"elapsed_ms": 5300}
    event: done     data: <result JSON>
    event: error    data: {"code": "...", "message": "..."}
"""
from __future__ import annotations

import json
import queue
import threading
import time
from collections.abc import Callable, Iterator
from typing import Any

from app.core.errors import AppError


def _sse(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def stream_stage(
    work: Callable[[Callable[[str, str], None]], Any],
    *,
    heartbeat_interval: float = 2.0,
) -> Iterator[str]:
    """Run ``work`` in a background thread, streaming progress as SSE.

    ``work`` receives a ``phase(name, label)`` callback it can call to announce
    progress, and must return a JSON-serializable result (already persisted).
    """
    events: "queue.Queue[tuple[str, Any]]" = queue.Queue()
    result: dict[str, Any] = {}

    def emit_phase(name: str, label: str) -> None:
        events.put(("phase", {"phase": name, "label": label}))

    def runner() -> None:
        try:
            out = work(emit_phase)
            result["value"] = out
            events.put(("done", out))
        except AppError as exc:
            events.put(("error", {"code": exc.code, "message": exc.message}))
        except Exception as exc:  # pragma: no cover - defensive
            events.put(("error", {"code": "internal_error", "message": str(exc)}))
        finally:
            events.put(("__end__", None))

    thread = threading.Thread(target=runner, daemon=True)
    thread.start()

    start = time.monotonic()
    yield _sse("phase", {"phase": "started", "label": "Starting…"})

    while True:
        try:
            event, data = events.get(timeout=heartbeat_interval)
        except queue.Empty:
            elapsed = int((time.monotonic() - start) * 1000)
            yield _sse("heartbeat", {"elapsed_ms": elapsed})
            continue
        if event == "__end__":
            break
        yield _sse(event, data)
