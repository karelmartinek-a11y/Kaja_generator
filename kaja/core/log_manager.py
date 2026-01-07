from __future__ import annotations

import base64
import hashlib
import json
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from .state import RunArtifacts, UiState
from .path_utils import create_dir
from .settings import Settings
from .pricing import PricingStore, Receipt


_LOG_ENCRYPTION_KEY: bytes | None = None


def configure_log_encryption(key: str | None) -> None:
    global _LOG_ENCRYPTION_KEY
    if key:
        _LOG_ENCRYPTION_KEY = hashlib.sha256(key.encode("utf-8")).digest()
    else:
        _LOG_ENCRYPTION_KEY = None


def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    key_len = len(key)
    return bytes(data[i] ^ key[i % key_len] for i in range(len(data)))


def _timestamp_ddmmyyyyhhmm() -> str:
    return time.strftime("%d%m%Y%H%M", time.localtime())


def _sanitize_identifier(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", (value or "").strip())
    return cleaned.strip("_") or "item"


def _build_log_filename(
    run: RunArtifacts,
    kind: str,
    *,
    stage: str = "",
    project_name: str = "",
    response_id: str = "",
    suffix: str = "",
) -> str:
    parts: List[str] = []
    if project_name:
        parts.append(_sanitize_identifier(project_name))
    if stage:
        parts.append(_sanitize_identifier(stage))
    identifier = response_id or run.run_id
    if identifier:
        parts.append(_sanitize_identifier(identifier))
    if suffix:
        parts.append(_sanitize_identifier(suffix))
    parts.append(kind)
    parts.append(_timestamp_ddmmyyyyhhmm())
    return "_".join(parts) + ".json"


def new_run_id() -> str:
    suffix = uuid.uuid4().hex[:4]
    return f"RUN_{_timestamp_ddmmyyyyhhmm()}_{suffix}"


def init_run(root_dir: Path) -> RunArtifacts:
    log_root = root_dir / "LOG"
    create_dir(log_root)
    run_id = new_run_id()
    run_dir = log_root / run_id
    create_dir(run_dir)
    return RunArtifacts(run_id=run_id, log_dir=str(run_dir))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    raw = json.dumps(payload, indent=2, ensure_ascii=False)
    if _LOG_ENCRYPTION_KEY:
        encrypted = _xor_encrypt(raw.encode("utf-8"), _LOG_ENCRYPTION_KEY)
        content = b"ENCRYPTED\n" + base64.b64encode(encrypted)
        path.write_bytes(content)
    else:
        with path.open("w", encoding="utf-8") as handle:
            handle.write(raw)


def log_ui_state(run: RunArtifacts, ui_state: UiState, *, response_id: str = "") -> Path:
    metadata = {
        "run_id": run.run_id,
        "response_id": response_id or "",
        "captured_at": datetime.utcnow().isoformat(),
        "project": ui_state.project_name,
        "mode": ui_state.mode,
    }
    payload = {
        "metadata": metadata,
        "ui_state": _to_json(ui_state),
    }
    name = _build_log_filename(
        run,
        "ui_state",
        stage=ui_state.mode,
        project_name=ui_state.project_name,
        response_id=response_id or run.run_id,
    )
    path = Path(run.log_dir) / name
    write_json(path, payload)
    return path


def log_request(
    run: RunArtifacts,
    payload: Dict[str, Any],
    *,
    stage: str = "",
    project_name: str = "",
    response_id: str = "",
    request_id: str = "",
    suffix: str = "",
) -> Path:
    metadata = {
        "run_id": run.run_id,
        "project": project_name,
        "stage": stage,
        "response_id": response_id,
        "logged_at": datetime.utcnow().isoformat(),
    }
    if request_id:
        metadata["request_id"] = request_id
    payload_with_meta = {
        "metadata": metadata,
        "payload": _to_json(payload),
    }
    suffix_parts = []
    if suffix:
        suffix_parts.append(suffix)
    if request_id:
        suffix_parts.append(f"req_{request_id}")
    suffix_value = "_".join(suffix_parts)
    name = _build_log_filename(
        run,
        "request",
        stage=stage,
        project_name=project_name,
        response_id=response_id or run.run_id,
        suffix=suffix_value,
    )
    path = Path(run.log_dir) / name
    write_json(path, payload_with_meta)
    return path


def log_response(
    run: RunArtifacts,
    payload: Dict[str, Any],
    *,
    stage: str = "",
    project_name: str = "",
    response_id: str = "",
    request_id: str = "",
    suffix: str = "",
) -> Path:
    metadata = {
        "run_id": run.run_id,
        "project": project_name,
        "stage": stage,
        "response_id": response_id,
        "logged_at": datetime.utcnow().isoformat(),
    }
    if request_id:
        metadata["request_id"] = request_id
    payload_with_meta = {
        "metadata": metadata,
        "payload": _to_json(payload),
    }
    suffix_parts = []
    if suffix:
        suffix_parts.append(suffix)
    if request_id:
        suffix_parts.append(f"req_{request_id}")
    suffix_value = "_".join(suffix_parts)
    name = _build_log_filename(
        run,
        "response",
        stage=stage,
        project_name=project_name,
        response_id=response_id or run.run_id,
        suffix=suffix_value,
    )
    path = Path(run.log_dir) / name
    write_json(path, payload_with_meta)
    return path


def log_file_ops(run: RunArtifacts, payload: Dict[str, Any]) -> Path:
    name = _build_log_filename(
        run,
        "file_ops",
        stage=payload.get("stage", ""),
        project_name=payload.get("project", ""),
        response_id=payload.get("response_id", ""),
        suffix=payload.get("action", ""),
    )
    path = Path(run.log_dir) / name
    write_json(path, payload)
    return path


def log_manifest(run: RunArtifacts, payload: Dict[str, Any], name: str) -> Path:
    manifest_name = _build_log_filename(
        run,
        name,
        project_name=str(payload.get("project", "")),
        response_id=str(payload.get("response_id", "")),
    )
    path = Path(run.log_dir) / manifest_name
    write_json(path, payload)
    return path


def log_hook_execution(run: RunArtifacts, payload: Dict[str, Any]) -> Path:
    name = _build_log_filename(
        run,
        "hook",
        stage=str(payload.get("stage", "")),
        project_name=str(payload.get("project", "")),
        response_id=str(payload.get("response_id", "")),
        suffix=str(payload.get("kind", "")),
    )
    path = Path(run.log_dir) / name
    write_json(path, payload)
    return path


def log_timeline(run: RunArtifacts, timeline: List[Dict[str, Any]]) -> Path:
    name = _build_log_filename(run, "timeline")
    path = Path(run.log_dir) / name
    payload = {
        "run_id": run.run_id,
        "timeline": timeline,
    }
    write_json(path, payload)
    return path


def _ensure_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def log_run_metadata(run: RunArtifacts, metadata: Dict[str, Any]) -> Path:
    payload = {
        "metadata": metadata,
        "captured_at": datetime.utcnow().isoformat(),
        "run_id": run.run_id,
    }
    name = _build_log_filename(
        run,
        "run_metadata",
        project_name=str(metadata.get("project", "")),
        response_id=str(metadata.get("response_id", "")),
    )
    path = Path(run.log_dir) / name
    write_json(path, payload)
    return path


def log_file_snapshot(run: RunArtifacts, rel_path: Path, content: str) -> Path:
    target = Path(run.log_dir) / "files" / rel_path
    _ensure_dir(target.parent)
    with target.open("w", encoding="utf-8") as handle:
        handle.write(content)
    return target


def log_file_operation(run: RunArtifacts, payload: Dict[str, Any]) -> Path:     
    payload_with_time = {
        **payload,
        "timestamp": datetime.utcnow().isoformat(),
        "run_id": run.run_id,
    }
    return log_file_ops(run, payload_with_time)


def log_file_upload(run: RunArtifacts, payload: Dict[str, Any]) -> Path:
    payload_with_meta = {
        **payload,
        "timestamp": datetime.utcnow().isoformat(),
        "run_id": run.run_id,
    }
    name = _build_log_filename(
        run,
        "file_upload",
        project_name=str(payload.get("project", "")),
        response_id=str(payload.get("response_id", "")),
        suffix=str(payload.get("scope", "")),
    )
    path = Path(run.log_dir) / name
    write_json(path, payload_with_meta)
    return path


def log_vector_store_entry(run: RunArtifacts, payload: Dict[str, Any]) -> Path:
    payload_with_meta = {
        **payload,
        "timestamp": datetime.utcnow().isoformat(),
        "run_id": run.run_id,
    }
    name = _build_log_filename(
        run,
        "vector_store",
        project_name=str(payload.get("project", "")),
        response_id=str(payload.get("response_id", "")),
        suffix=str(payload.get("vector_store_id", "")),
    )
    path = Path(run.log_dir) / name
    write_json(path, payload_with_meta)
    return path



def _to_json(payload: Dict[str, Any]) -> Dict[str, Any]:
    def convert(value: Any) -> Any:
        if hasattr(value, "__dict__"):
            return {key: convert(val) for key, val in value.__dict__.items()}
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, dict):
            return {key: convert(val) for key, val in value.items()}
        return value

    return convert(payload)


def log_pricing_receipt(run: RunArtifacts, settings: Settings, receipt: Receipt) -> Path:
    db_path = Path(settings.db_path)
    if not db_path.is_absolute():
        db_path = Path(run.log_dir).parents[1] / db_path
    PricingStore(db_path).add_receipt(receipt)
    payload = {
        "receipt": {
            "run_id": receipt.run_id,
            "project": receipt.project,
            "model": receipt.model,
            "mode": receipt.mode,
            "response_id": receipt.response_id,
            "total_cost": receipt.total_cost,
            "details": json.loads(receipt.details_json),
            "created_at": receipt.created_at,
            "verified_pricing": receipt.verified_pricing,
        },
        "logged_at": datetime.utcnow().isoformat(),
    }
    name = _build_log_filename(
        run,
        "receipt",
        project_name=receipt.project,
        response_id=receipt.response_id,
        suffix=receipt.mode,
    )
    path = Path(run.log_dir) / name
    write_json(path, payload)
    return path


def log_run_index(root_dir: Path, entry: Dict[str, Any]) -> Path:
    index_dir = root_dir / "LOG"
    _ensure_dir(index_dir)
    index_path = index_dir / "run_index.json"
    entries: List[Dict[str, Any]] = []
    if index_path.exists():
        try:
            loaded = json.loads(index_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                entries = loaded
        except Exception:
            entries = []
    entries.append(entry)
    write_json(index_path, entries)
    return index_path
