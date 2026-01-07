from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .design_standard import design_standard_block
from .log_manager import (
    log_file_operation,
    log_file_snapshot,
    log_file_upload,
    log_hook_execution,
    log_manifest,
    log_pricing_receipt,
    log_request,
    log_response,
    log_run_index,
    log_run_metadata,
    log_timeline,
    log_vector_store_entry,
)
from .openai_client import OpenAIClient
from .path_utils import create_dir, is_versing_dir, iter_files
from .pricing import Receipt
from .settings import Settings
from .state import FileRecord, RunArtifacts, UiState
from .diagnostics import (
    DiagnosticPackage,
    collect_ssh_diagnostics,
    collect_windows_diagnostics,
)
from .price_catalog import PriceCatalog
from . import security

MAX_CHUNK_LINES = 500
DEFAULT_CHUNK_LINES = 500
MAX_COMPATIBLE_FILE_BYTES = 5 * 1024 * 1024
TEXT_SAMPLE_BYTES = 4096
DEFAULT_CONTEXT_LIMIT = 8192
PROMPT_TRIM_CONTRACT = "KAJA_PROMPT_SPLIT"
LONG_PROMPT_CONTRACT = "LONG_PROMPT_COMPRESS"
FILE_MAP_CONTRACT = "A2X_FILE_MAP"

ProgressCallback = Callable[[str, float], None]
StopCheck = Callable[[], bool]


class PipelineCancelled(Exception):
    """Raised when a run is canceled through the UI."""


@dataclass
class PipelineResult:
    mode: str
    run_id: str
    response_id: str
    files_written: List[Path] = field(default_factory=list)
    log_messages: List[str] = field(default_factory=list)
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    timeline_log: str | None = None
    manifest_log: str | None = None
    dry_run_summary: Dict[str, Any] | None = None
    post_hook_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AttachmentInfo:
    file_id: str
    name: str
    purpose: str
    size_bytes: int
    local_path: Path | None = None


@dataclass
class MirrorEntry:
    path: str
    absolute_path: str
    size_bytes: int
    uploaded: bool
    file_id: str | None = None
    reason: str | None = None
    notes: str | None = None
    local_path: Path | None = None


@dataclass
class MirrorManifestInfo:
    path: Path
    file_id: str


@dataclass
class DiagnosticEntry:
    file_id: str
    path: str
    description: str
    local_path: Path
    scope: str
    captured_at: str


@dataclass
class RequestAssets:
    attachments: List[AttachmentInfo] = field(default_factory=list)
    mirror_entries: List[MirrorEntry] = field(default_factory=list)
    mirror_manifest: MirrorManifestInfo | None = None
    diagnostics: List[DiagnosticEntry] = field(default_factory=list)
    vector_store_id: str | None = None
    file_search_enabled: bool = False
    attachments_in_vector_store: bool = False
    attachments_as_input_files: bool = True


def _slugify(name: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]+", "-", name.lower())
    sanitized = sanitized.strip("-")
    return sanitized or "project"


def _ensure_json_serializable(value: Dict[str, Any]) -> Dict[str, Any]:
    text = json.dumps(value, ensure_ascii=False)
    return json.loads(text)


def _is_probably_text(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:TEXT_SAMPLE_BYTES]
    except OSError:
        return False
    if b"\x00" in sample:
        return False
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _is_sensitive_env(path: Path) -> bool:
    name = path.name.lower()
    if name == ".env":
        return True
    return name.startswith(".env.")


def chunk_text(content: str, max_lines: int = MAX_CHUNK_LINES) -> List[Dict[str, Any]]:
    lines = content.splitlines()
    chunk_capacity = max(max_lines, 1)
    total_chunks = math.ceil(len(lines) / chunk_capacity) if lines else 1
    if not lines:
        return [
            {
                "chunking": {
                    "max_lines": chunk_capacity,
                    "chunk_index": 0,
                    "chunk_count": 1,
                    "has_more": False,
                    "next_chunk_index": None,
                },
                "content": "",
            }
        ]
    chunks: List[Dict[str, Any]] = []
    for index in range(total_chunks):
        start = index * chunk_capacity
        end = start + chunk_capacity
        slice_lines = lines[start:end]
        has_more = index < total_chunks - 1
        chunk = {
            "chunking": {
                "max_lines": chunk_capacity,
                "chunk_index": index,
                "chunk_count": total_chunks,
                "has_more": has_more,
                "next_chunk_index": index + 1 if has_more else None,
            },
            "content": "\n".join(slice_lines),
        }
        chunks.append(chunk)
    return chunks


class PipelineExecutor:
    def __init__(
        self,
        root_dir: Path,
        run_artifacts: RunArtifacts,
        ui_logger: Callable[[str], None],
        *,
        client: Optional[OpenAIClient] = None,
        settings: Optional[Settings] = None,
        initial_logs: Optional[Sequence[Tuple[Path, str]]] = None,
        security_policy: security.SecurityPolicy | None = None,
        dry_run_confirmation: Callable[[Dict[str, Any]], bool] | None = None,
    ):
        self._root_dir = root_dir
        self._run = run_artifacts
        self._logger = ui_logger
        self._client = client
        self._settings = settings or Settings(db_path=str(root_dir / "kaja.db"))
        self._out_root = self._root_dir / "OUT"
        create_dir(self._out_root)
        self._buffers: Dict[str, List[str]] = {}
        self._log_entries: List[Dict[str, Any]] = []
        self._ui_state_log_path: Path | None = None
        self._pricing_receipt_path: Path | None = None
        self._ui_state: UiState | None = None
        self._response_id = ""
        self._diagnostic_packages: Dict[str, DiagnosticPackage] = {}
        self._diagnostic_uploads: List[Dict[str, Any]] = []
        self._timeline: List[Dict[str, Any]] = []
        self._request_snapshot: Dict[str, Any] = {}
        self._progress_callback: ProgressCallback | None = None
        self._last_progress_ratio = 0.0
        self._expected_a2_paths: List[str] = []
        self._model_capabilities: Dict[str, Any] = {
            "supports_vector_store": False,
            "supports_file_search": False,
            "supports_temperature": False,
            "resolved": False,
        }
        self._versing_snapshot_path: Path | None = None
        self._watchdog_interval = 30.0
        self._last_progress_update = time.time()
        self._last_watchdog_log = time.time()
        self._request_templates: Dict[str, Dict[str, Any]] = {}
        self._c_contract_block: str = ""
        self._pricing_steps: List[Dict[str, Any]] = []
        self._pricing_step_index = 0
        self._price_catalog = PriceCatalog(
            cache_path=self._root_dir / "pricing_cache.json",
            settings=self._settings,
        )
        self._price_catalog.refresh_if_needed(force=self._settings.pricing_auto_refresh)
        self._security_policy = security_policy
        self._in_security_policy = security.policy_from_settings(self._settings, "in")
        self._dry_run_confirmation = dry_run_confirmation
        self._dry_run_summary: Dict[str, Any] | None = None
        self._dry_run_summary_log_path: Path | None = None
        for log_path, category in (initial_logs or []):
            self._register_log_entry(log_path, category)

    @classmethod
    def generate_response_id(cls, mode: str) -> str:
        return cls._generate_response_id(mode)

    def _relative_log_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self._run.log_dir))
        except ValueError:
            return str(path)

    def _register_log_entry(
        self,
        path: Path,
        category: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        entry: Dict[str, Any] = {
            "path": self._relative_log_path(path),
            "category": category,
        }
        if extra:
            entry["meta"] = extra
        self._log_entries.append(entry)
        if category == "ui_state":
            self._ui_state_log_path = path
        if category == "receipt":
            self._pricing_receipt_path = path

    def _start_timeline_entry(self, step: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {"step": step, "details": details or {}, "start": time.time()}

    def _finish_timeline_entry(self, context: Dict[str, Any], result: str, ids: Dict[str, Any] | None = None) -> None:
        end = time.time()
        entry = {
            "step": context["step"],
            "start": datetime.utcfromtimestamp(context["start"]).isoformat(),
            "end": datetime.utcfromtimestamp(end).isoformat(),
            "duration_s": round(end - context["start"], 3),
            "result": result,
            "details": context.get("details", {}),
            "ids": ids or {},
        }
        self._timeline.append(entry)

    def _notify_progress(self, message: str) -> None:
        if self._progress_callback:
            self._progress_callback(message, self._last_progress_ratio)

    def _load_request_templates(self) -> None:
        if self._request_templates:
            return
        doc_path = self._root_dir / "doc" / "00_zadani_MASTER_FULL.md"
        text = doc_path.read_text(encoding="utf-8")
        self._request_templates = {
            "A1": self._extract_json_from_section(text, "## A1) Request JSON"),
            "A2": self._extract_json_from_section(text, "## A2) Request JSON"),
            "A3": self._extract_json_from_section(text, "## A3) Request JSON"),
            "B1": self._extract_json_from_section(text, "## B1) Request JSON"),
            "B2": self._extract_json_from_section(text, "## B2) Request JSON"),
            "B3": self._extract_json_from_section(text, "## B3) Request JSON"),
        }
        self._c_contract_block = self._extract_contract_block(
            text,
            "**KONTRAKT C_FILES_ALL:**",
        )

    def _extract_json_from_section(self, text: str, header: str) -> Dict[str, Any]:
        header_pattern = re.compile(rf"^{re.escape(header)}[^\n]*$", re.M)
        match = header_pattern.search(text)
        if not match:
            raise ValueError(f"Nelze najít sekci {header} v zadání.")
        section_start = match.end()
        next_header = re.search(r"^##\\s", text[section_start:], re.M)
        section_end = section_start + next_header.start() if next_header else len(text)
        segment = text[section_start:section_end]
        brace_start = segment.find("{")
        while brace_start >= 0:
            try:
                block = self._extract_braced_block(segment, brace_start)
            except ValueError:
                brace_start = segment.find("{", brace_start + 1)
                continue
            try:
                payload = json.loads(block)
            except json.JSONDecodeError:
                brace_start = segment.find("{", brace_start + 1)
                continue
            if isinstance(payload, dict) and {"model", "instructions", "input"} <= payload.keys():
                return payload
            brace_start = segment.find("{", brace_start + 1)
        raise ValueError(f"Nelze najít JSON v sekci {header}.")

    def _extract_contract_block(self, text: str, marker: str) -> str:
        marker_index = text.find(marker)
        if marker_index < 0:
            raise ValueError("Nelze najít kontrakt C_FILES_ALL v zadání.")
        brace_start = text.find("{", marker_index)
        if brace_start < 0:
            raise ValueError("Nelze najít JSON kontrakt C_FILES_ALL.")
        block = self._extract_braced_block(text, brace_start)
        return block.strip()

    def _extract_braced_block(self, text: str, start_index: int) -> str:
        in_string = False
        escape = False
        depth = 0
        for idx in range(start_index, len(text)):
            char = text[idx]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start_index : idx + 1]
        raise ValueError("JSON blok není korektně uzavřen.")

    def _prepare_request_assets(
        self,
        mode: str,
        ui_state: UiState,
        attachments: Sequence[FileRecord],
    ) -> RequestAssets:
        assets = RequestAssets()
        if mode in {"GENERATE", "MODIFY", "QA"}:
            assets.attachments = self._prepare_attachments(attachments)
        supports_file_search = bool(
            self._model_capabilities.get("supports_vector_store")
            and self._model_capabilities.get("supports_file_search")
        )
        attachment_ids = [
            attachment.file_id
            for attachment in assets.attachments
            if attachment.file_id and not attachment.file_id.startswith("ATT_")
        ]
        if supports_file_search and self._client and attachment_ids:
            if not assets.vector_store_id:
                assets.vector_store_id = self._create_vector_store(
                    ui_state.project_name or "Kaja"
                )
            if assets.vector_store_id:
                for attachment in assets.attachments:
                    if not attachment.file_id or attachment.file_id.startswith("ATT_"):
                        continue
                    self._add_vector_store_file(
                        assets.vector_store_id,
                        attachment.file_id,
                        {
                            "source": "attachment",
                            "filename": attachment.name,
                        },
                    )
                assets.file_search_enabled = True
                assets.attachments_in_vector_store = True
                assets.attachments_as_input_files = False
        if mode != "MODIFY":
            return assets
        in_root = Path(ui_state.in_dir)
        if not in_root.exists():
            raise ValueError("IN adresář neexistuje.")
        vector_store_id = assets.vector_store_id
        if supports_file_search and self._client:
            if not vector_store_id:
                vector_store_id = self._create_vector_store(ui_state.project_name or "Kaja")
        assets.vector_store_id = vector_store_id
        assets.file_search_enabled = bool(vector_store_id)
        diagnostics = []
        if self._diagnostic_packages:
            diagnostics = self._upload_diagnostics(vector_store_id)
        mirror_entries = self._build_mirror_entries(
            in_root,
            vector_store_id=vector_store_id,
        )
        mirror_manifest = self._create_mirror_manifest(
            in_root,
            mirror_entries,
            diagnostics,
            vector_store_id=vector_store_id,
        )
        assets.mirror_entries = mirror_entries
        assets.mirror_manifest = mirror_manifest
        assets.diagnostics = diagnostics
        return assets

    def _prepare_attachments(
        self,
        attachments: Sequence[FileRecord],
    ) -> List[AttachmentInfo]:
        prepared: List[AttachmentInfo] = []
        for record in attachments:
            file_id = record.file_id
            local_path = Path(record.filename)
            size_bytes = record.size_bytes
            if local_path.exists():
                size_bytes = local_path.stat().st_size
            needs_upload = bool(
                local_path.exists()
                and (not file_id or file_id.startswith("ATT_"))
            )
            if needs_upload:
                uploaded_id = self._upload_file(
                    local_path,
                    purpose=record.purpose or "user_data",
                    scope="attachment",
                )
                if uploaded_id:
                    file_id = uploaded_id
            prepared.append(
                AttachmentInfo(
                    file_id=file_id,
                    name=Path(record.filename).name,
                    purpose=record.purpose or "user_data",
                    size_bytes=size_bytes,
                    local_path=local_path if local_path.exists() else None,
                )
            )
        return prepared

    def _build_mirror_entries(
        self,
        in_root: Path,
        *,
        vector_store_id: str | None,
    ) -> List[MirrorEntry]:
        entries: List[MirrorEntry] = []
        root_name = in_root.name
        exclude_names = {"venv", ".venv", "LOG"}
        for path in iter_files(in_root, exclude_names, root_name):
            rel_path = path.relative_to(in_root).as_posix()
            size_bytes = path.stat().st_size
            entry = MirrorEntry(
                path=rel_path,
                absolute_path=str(path),
                size_bytes=size_bytes,
                uploaded=False,
                local_path=path,
            )
            if size_bytes > MAX_COMPATIBLE_FILE_BYTES:
                entry.reason = "file_too_large"
                entries.append(entry)
                continue
            if _is_sensitive_env(path) and not self._settings.allow_sensitive_uploads:
                entry.reason = "env_file"
                entry.notes = self._summarize_env_keys(path)
                entries.append(entry)
                continue
            if not _is_probably_text(path):
                entry.reason = "binary_or_non_text"
                entries.append(entry)
                continue
            report = self._in_security_policy.evaluate_path(path)
            if report.blocked:
                reasons = "; ".join(finding.reason for finding in report.findings)
                entry.reason = f"security_blocked: {reasons}"
                entries.append(entry)
                security.record_security_event(
                    self._run,
                    "in_mirror",
                    str(path),
                    report,
                    blocked=True,
                )
                continue
            if report.findings:
                reasons = "; ".join(finding.reason for finding in report.findings)
                entry.notes = f"security_warning: {reasons}"
                security.record_security_event(
                    self._run,
                    "in_mirror",
                    str(path),
                    report,
                    blocked=False,
                )
            uploaded_id = self._upload_file(path, purpose="in mirror", scope="in_mirror")
            if uploaded_id:
                entry.file_id = uploaded_id
                entry.uploaded = True
                if vector_store_id:
                    self._add_vector_store_file(
                        vector_store_id,
                        uploaded_id,
                        {
                            "path": str(path),
                            "source": "in_mirror",
                        },
                    )
            entries.append(entry)
        return entries

    def _create_mirror_manifest(
        self,
        in_root: Path,
        mirror_entries: Sequence[MirrorEntry],
        diagnostics: Sequence[DiagnosticEntry],
        *,
        vector_store_id: str | None,
    ) -> MirrorManifestInfo | None:
        payload = {
            "project": self._ui_state.project_name if self._ui_state else "",
            "response_id": self._response_id,
            "root": str(in_root),
            "generated_at": datetime.utcnow().isoformat(),
            "files": [
                {
                    "path": entry.path,
                    "absolute_path": entry.absolute_path,
                    "size_bytes": entry.size_bytes,
                    "uploaded": entry.uploaded,
                    "file_id": entry.file_id,
                    "reason": entry.reason,
                    "notes": entry.notes,
                }
                for entry in mirror_entries
            ],
            "diagnostics": [
                {
                    "scope": diag.scope,
                    "path": diag.path,
                    "description": diag.description,
                    "file_id": diag.file_id,
                    "captured_at": diag.captured_at,
                }
                for diag in diagnostics
            ],
        }
        manifest_path = log_manifest(self._run, payload, "mirror_manifest")
        self._register_log_entry(manifest_path, "mirror_manifest")
        file_id = self._upload_file(manifest_path, purpose="mirror manifest", scope="mirror_manifest")
        if not file_id:
            return None
        if vector_store_id:
            self._add_vector_store_file(
                vector_store_id,
                file_id,
                {"source": "mirror_manifest", "path": str(manifest_path)},
            )
        return MirrorManifestInfo(path=manifest_path, file_id=file_id)

    def _upload_diagnostics(self, vector_store_id: str | None) -> List[DiagnosticEntry]:
        entries: List[DiagnosticEntry] = []
        self._diagnostic_uploads.clear()
        policy = self._security_policy
        for scope, package in self._diagnostic_packages.items():
            descriptions = {record["path"]: record["description"] for record in package.records}
            for path in iter_files(package.root, set(), package.root.name):
                rel_path = path.relative_to(package.root).as_posix()
                if policy:
                    report = policy.evaluate_path(path)
                    if report.blocked:
                        reasons = "; ".join(finding.reason for finding in report.findings)
                        self._log(f"Diagnostika {scope} blokována: {rel_path} ({reasons})")
                        security.record_security_event(
                            self._run,
                            f"diagnostics_{scope}",
                            str(path),
                            report,
                            blocked=True,
                        )
                        continue
                    if report.findings:
                        reasons = "; ".join(finding.reason for finding in report.findings)
                        self._log(f"Diagnostika {scope} upozornění: {rel_path} ({reasons})")
                        security.record_security_event(
                            self._run,
                            f"diagnostics_{scope}",
                            str(path),
                            report,
                            blocked=False,
                        )
                file_id = self._upload_file(path, purpose="diagnostics", scope=f"diagnostics_{scope}")
                if not file_id:
                    continue
                upload_entry = {
                    "scope": scope,
                    "path": rel_path,
                    "file_id": file_id,
                    "status": "uploaded",
                    "uploaded_at": datetime.utcnow().isoformat(),
                }
                self._diagnostic_uploads.append(upload_entry)
                entry = DiagnosticEntry(
                    file_id=file_id,
                    path=f"{package.root.name}/{rel_path}",
                    description=descriptions.get(rel_path, "diagnostic file"),
                    local_path=path,
                    scope=scope,
                    captured_at=package.metadata.get("captured_at", ""),
                )
                if vector_store_id:
                    self._add_vector_store_file(
                        vector_store_id,
                        file_id,
                        {
                            "source": "diagnostics",
                            "scope": scope,
                            "captured_at": entry.captured_at,
                            "path": entry.path,
                        },
                    )
                entries.append(entry)
        return entries

    def _create_vector_store(self, project: str) -> str | None:
        if not self._client:
            return None
        timestamp = datetime.utcnow().strftime("%d%m%Y%H%M")
        name = f"{project}{timestamp}"
        try:
            response = self._client.create_vector_store(name)
        except Exception as exc:
            self._log(f"Vytvoření vector store selhalo: {exc}")
            return None
        store_id = response.get("id") or response.get("vector_store_id")
        if not store_id:
            self._log("Vector store nebyl vytvořen (chybí ID).")
            return None
        return str(store_id)

    def _add_vector_store_file(
        self,
        store_id: str,
        file_id: str,
        attributes: Dict[str, Any],
    ) -> None:
        try:
            self._client.add_vector_store_file(store_id, file_id, attributes=attributes)
            vs_payload = {
                "project": self._ui_state.project_name if self._ui_state else "",
                "response_id": self._response_id,
                "vector_store_id": store_id,
                "file_id": file_id,
                "attributes": attributes,
                "added_at": datetime.utcnow().isoformat(),
            }
            vs_log = log_vector_store_entry(self._run, vs_payload)
            self._register_log_entry(
                vs_log,
                "vector_store",
                {"vector_store_id": store_id},
            )
        except Exception as exc:
            self._log(f"Vector store attach ({store_id}) selhalo: {exc}")

    def _upload_file(self, path: Path, *, purpose: str, scope: str) -> str | None:
        if not self._client:
            self._log(f"OpenAI client není dostupný; upload {path} přeskočen.")
            return None
        try:
            upload_result = self._client.upload_file(path, purpose=purpose)
        except Exception as exc:
            self._log(f"Upload {path} selhal: {exc}")
            return None
        file_id = upload_result.get("id") or upload_result.get("file_id")
        if not file_id:
            self._log(f"Upload {path} selhal: chybí file_id.")
            return None
        payload = {
            "scope": scope,
            "project": self._ui_state.project_name if self._ui_state else "",
            "response_id": self._response_id,
            "local_path": str(path),
            "file_id": file_id,
            "purpose": purpose,
            "size": path.stat().st_size if path.exists() else 0,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        upload_log = log_file_upload(self._run, payload)
        self._register_log_entry(upload_log, "file_upload", {"scope": scope})
        return str(file_id)

    def _summarize_env_keys(self, path: Path) -> str:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return "env_keys_unavailable"
        keys = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key = stripped.split("=", 1)[0].strip()
            if key:
                keys.append(key)
        if not keys:
            return "env_keys_empty"
        return "env_keys: " + ", ".join(keys[:50])

    def _resolve_previous_response_id(self, ui_state: UiState, fallback: str | None) -> str:
        candidate = ui_state.response_id.strip()
        if candidate:
            return candidate
        return fallback or ""

    def _render_template_text(self, text: str, replacements: Dict[str, str]) -> str:
        rendered = text
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
        return rendered

    def _build_instructions_text(
        self,
        base: str,
        assets: RequestAssets,
        ui_state: UiState,
        *,
        include_mirror: bool,
        include_diagnostics: bool,
        include_design_standard: bool = True,
    ) -> str:
        sections: List[str] = []
        attachments = self._format_attachments(assets.attachments, assets)
        if attachments:
            sections.append(attachments)
        if include_mirror:
            mirror_block = self._format_mirror_entries(assets)
            if mirror_block:
                sections.append(mirror_block)
        if include_diagnostics:
            diag_block = self._format_diagnostics(assets.diagnostics)
            if diag_block:
                sections.append(diag_block)
        if include_design_standard:
            design_block = design_standard_block().strip()
            if design_block:
                sections.append(design_block)
        script_notice = self._format_script_expectation(ui_state)
        if script_notice:
            sections.append(script_notice)
        if not sections:
            return base
        return base + "\n\n" + "\n\n".join(sections)

    def _build_input_text_with_assets(
        self,
        base: str,
        assets: RequestAssets,
        ui_state: UiState,
        *,
        include_mirror: bool,
        include_diagnostics: bool,
    ) -> str:
        sections: List[str] = []
        attachments = self._format_attachments(assets.attachments, assets)
        if attachments:
            sections.append(attachments)
        if include_mirror:
            mirror_block = self._format_mirror_entries(assets)
            if mirror_block:
                sections.append(mirror_block)
        if include_diagnostics:
            diag_block = self._format_diagnostics(assets.diagnostics)
            if diag_block:
                sections.append(diag_block)
        script_notice = self._format_script_expectation(ui_state)
        if script_notice:
            sections.append(script_notice)
        if not sections:
            return base
        return base + "\n\n" + "\n\n".join(sections)

    def _build_input_parts(
        self,
        text: str,
        assets: RequestAssets,
        *,
        include_attachments: bool,
        include_mirror: bool,
        include_diagnostics: bool,
    ) -> List[Dict[str, Any]]:
        parts: List[Dict[str, Any]] = [{"type": "input_text", "text": text}]
        for file_id in self._collect_input_file_ids(
            assets,
            include_attachments=include_attachments,
            include_mirror=include_mirror,
            include_diagnostics=include_diagnostics,
        ):
            parts.append({"type": "input_file", "file_id": file_id})
        return [{"role": "user", "content": parts}]

    @staticmethod
    def _include_design_standard_for(template_key: str) -> bool:
        return template_key in {"A1", "A2", "A3", "B1", "B2", "B3"}

    def _strict_rules_block(self, template_key: str) -> str:
        rules: List[str] = []
        if template_key == "A1":
            rules = [
                "Piš plán jako finální specifikaci: používej explicitní názvy modulů, souborů a veřejných API.",
                "Architecture.modules musí uvádět konkrétní exporty (funkce/třídy/konstanty) a vazby mezi moduly.",
                "Uveď jednotné názvosloví doménových entit a sdílené datové modely.",
                "Pokud něco chybí, dej to do assumptions/constraints, nevymýšlej si nové požadavky.",
            ]
        elif template_key == "A2":
            rules = [
                "Každý soubor musí mít unikátní odpovědnost a žádné překryvy.",
                "Purpose musí explicitně obsahovat EXPORTS a IMPORTS (přesné názvy symbolů a odkazy na soubory).",
                "Název symbolů musí být konzistentní napříč soubory (jedna definice, mnoho použití).",
            ]
        elif template_key == "A3":
            rules = [
                "Implementuj pouze to, co je definováno v A1/A2/A2X; A2X_FILE_MAP je jediný zdroj pravdy pro exporty/importy.",
                "Exporty musí odpovídat A2X_FILE_MAP (name/kind/signature) a být v contentu doslovně přítomné.",
                "Nezaváděj nové symboly ani nové soubory; zachovej shodný datový model napříč soubory.",
                "Výsledek musí být spustitelný bez ručních úprav.",
            ]
        elif template_key in {"B1", "B2", "B3"}:
            rules = [
                "Změny musí respektovat existující API a neporušit kompatibilitu.",
                "Upravuj pouze soubory a symboly, které jsou explicitně v plánu změn.",
            ]
        if not rules:
            return ""
        return "STRIKTNÍ PRAVIDLA (determinismus):\n- " + "\n- ".join(rules)

    def _collect_input_file_ids(
        self,
        assets: RequestAssets,
        *,
        include_attachments: bool,
        include_mirror: bool,
        include_diagnostics: bool,
    ) -> List[str]:
        ids: List[str] = []
        seen: set[str] = set()
        if include_attachments and assets.attachments_as_input_files:
            for attachment in assets.attachments:
                if not attachment.file_id or attachment.file_id.startswith("ATT_"):
                    continue
                if attachment.file_id in seen:
                    continue
                ids.append(attachment.file_id)
                seen.add(attachment.file_id)
        if include_mirror:
            for entry in assets.mirror_entries:
                if not entry.file_id:
                    continue
                if entry.file_id in seen:
                    continue
                ids.append(entry.file_id)
                seen.add(entry.file_id)
            if assets.mirror_manifest and assets.mirror_manifest.file_id:
                if assets.mirror_manifest.file_id not in seen:
                    ids.append(assets.mirror_manifest.file_id)
                    seen.add(assets.mirror_manifest.file_id)
        if include_diagnostics:
            for diag in assets.diagnostics:
                if diag.file_id in seen:
                    continue
                ids.append(diag.file_id)
                seen.add(diag.file_id)
        return ids

    def _format_attachments(
        self,
        attachments: Sequence[AttachmentInfo],
        assets: RequestAssets | None = None,
    ) -> str:
        if not attachments:
            return ""
        use_vector_store = bool(
            assets and assets.attachments_in_vector_store and assets.vector_store_id
        )
        use_input_files = bool(assets and assets.attachments_as_input_files)
        store_id = assets.vector_store_id if assets else None
        lines = ["PŘIPOJENÉ SOUBORY (informational):"]
        for attachment in attachments:
            file_id = attachment.file_id or "MISSING"
            if not attachment.file_id or attachment.file_id.startswith("ATT_"):
                availability = "files_api (soubor není nahrán)"
            elif use_vector_store and store_id:
                availability = f"vector_store (store_id={store_id})"
            elif use_input_files:
                availability = "input_file"
            else:
                availability = "files_api (soubor je ve Files API)"
            lines.append(
                f"- {attachment.name} | file_id={file_id} | purpose={attachment.purpose} | "
                f"size={attachment.size_bytes} B | dostupnost={availability}"
            )
        return "\n".join(lines)

    def _format_mirror_entries(self, assets: RequestAssets) -> str:
        lines: List[str] = []
        if assets.mirror_entries:
            lines.append("MIRROR INPUT FILES:")
            for entry in assets.mirror_entries:
                status = "uploaded" if entry.file_id else f"skipped: {entry.reason or 'unknown'}"
                file_id = entry.file_id or "MISSING"
                lines.append(f"- {entry.path} | file_id={file_id} | {status} | source={entry.absolute_path}")
        if assets.mirror_manifest and assets.mirror_manifest.file_id:
            lines.append(
                f"MIRROR MANIFEST: file_id={assets.mirror_manifest.file_id} | path={assets.mirror_manifest.path}"
            )
        return "\n".join(lines)

    def _format_diagnostics(self, diagnostics: Sequence[DiagnosticEntry]) -> str:
        if not diagnostics:
            return ""
        lines = ["DIAGNOSTIKA (file_id + popis):"]
        for entry in diagnostics:
            lines.append(
                f"- {entry.path} | file_id={entry.file_id} | {entry.description} | scope={entry.scope}"
            )
        return "\n".join(lines)

    def _format_script_expectation(self, ui_state: UiState) -> str:
        if not (ui_state.diagnostics.windows_out or ui_state.diagnostics.ssh_out):
            return ""
        return "OČEKÁVANÝ VÝSTUP: musí obsahovat skript(y) a readmerepair.txt."

    def _format_dialog_block(self, label: str, content: str) -> str:
        if not label:
            return ""
        cleaned = content.strip()
        if cleaned:
            return f"{label}: {cleaned}"
        return f"{label}: (není zadáno)"

    def _format_json_block(self, label: str, payload: Any) -> str:
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        return f"{label}:\n{serialized}"

    @staticmethod
    def _split_text_into_chunks(text: str, max_chars: int) -> List[str]:
        if not text:
            return [""]
        if max_chars <= 0:
            return [text]
        lines = text.splitlines(keepends=True)
        chunks: List[str] = []
        buffer: List[str] = []
        size = 0
        for line in lines:
            line_len = len(line)
            if size + line_len > max_chars and buffer:
                chunks.append("".join(buffer))
                buffer = [line]
                size = line_len
                continue
            buffer.append(line)
            size += line_len
        if buffer:
            chunks.append("".join(buffer))
        return chunks

    def _build_long_prompt_payload(
        self,
        stage: str,
        label: str,
        *,
        chunk_index: int,
        chunk_count: int,
        previous_summary: str,
        chunk_text: str,
        ui_state: UiState,
        max_tokens: int,
    ) -> Dict[str, Any]:
        contract = {
            "contract": LONG_PROMPT_CONTRACT,
            "summary": "string",
            "chunk_index": "integer",
            "chunk_count": "integer",
            "notes": ["string"],
        }
        contract_text = json.dumps(contract, ensure_ascii=False)
        instructions = (
            "Jsi kompresní modul. Vrať pouze validní JSON bez markdownu. "
            f"KONTRAKT {LONG_PROMPT_CONTRACT}: {contract_text}. "
            "Zachovej všechna pravidla, kontrakty a význam. "
            "Výsledek musí být deterministicky použitelný jako vstup pro další kroky. "
            f"Limit: summary <= {max_tokens} tokenů (1 token ~ 4 znaky)."
        )
        input_text = (
            f"STAGE: {stage}\n"
            f"LABEL: {label}\n"
            f"CHUNK_INDEX: {chunk_index + 1}/{chunk_count}\n"
            f"MAX_TOKENS: {max_tokens}\n\n"
            "EXISTING_SUMMARY:\n<<<\n"
            f"{previous_summary or '(empty)'}\n"
            ">>>\n\n"
            "CHUNK_TEXT:\n<<<\n"
            f"{chunk_text}\n"
            ">>>\n\n"
            "VÝSTUP (JSON): "
            f'{{"contract":"{LONG_PROMPT_CONTRACT}","summary":"...","chunk_index":{chunk_index + 1},'
            f'"chunk_count":{chunk_count},"notes":[...]}}'
        )
        return {
            "model": ui_state.model or "gpt-4o",
            "temperature": 0.0,
            "instructions": instructions,
            "input": [{"role": "user", "content": [{"type": "input_text", "text": input_text}]}],
        }

    def _parse_long_prompt_response(self, response: Dict[str, Any]) -> str:
        text = self._extract_response_text(response)
        payload = self._coerce_json_payload(text, LONG_PROMPT_CONTRACT)
        if not isinstance(payload, dict):
            raise ValueError("LONG_PROMPT_COMPRESS response není objekt.")
        summary = payload.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            raise ValueError("LONG_PROMPT_COMPRESS response neobsahuje summary.")
        return summary.strip()

    def _compress_text_by_chunks(
        self,
        stage: str,
        label: str,
        text: str,
        ui_state: UiState,
        max_tokens: int,
        *,
        depth: int = 0,
    ) -> str:
        cleaned = text.strip()
        if not cleaned:
            return cleaned
        context_limit = self._model_context_limit(ui_state.model)
        max_chunk_tokens = max(512, int(context_limit * 0.2))
        max_chunk_chars = max_chunk_tokens * 4
        chunks = self._split_text_into_chunks(cleaned, max_chunk_chars)
        summary = ""
        chunk_count = len(chunks)
        for idx, chunk in enumerate(chunks):
            self._notify_progress(f"{stage}: komprimuji {label} ({idx + 1}/{chunk_count})")
            payload = self._build_long_prompt_payload(
                stage,
                label,
                chunk_index=idx,
                chunk_count=chunk_count,
                previous_summary=summary,
                chunk_text=chunk,
                ui_state=ui_state,
                max_tokens=max_tokens,
            )
            if not self._model_capabilities.get("supports_temperature", False):
                payload.pop("temperature", None)
            response = self._send_request(
                f"{stage}_LONG_PROMPT",
                payload,
                ui_state,
                update_response_id=False,
            )
            summary = self._parse_long_prompt_response(response)
        if self._estimate_tokens(summary) > max_tokens and depth < 1:
            return self._compress_text_by_chunks(
                stage,
                f"{label}_reshrink",
                summary,
                ui_state,
                max_tokens,
                depth=depth + 1,
            )
        if self._estimate_tokens(summary) > max_tokens:
            raise ValueError(
                f"{stage}: shrnutí je stále příliš dlouhé ({self._estimate_tokens(summary)} tokenů)."
            )
        return summary.strip()

    def _prepare_dialog_content(
        self,
        stage: str,
        content: str,
        ui_state: UiState,
    ) -> str:
        dialog = content.strip() or "(není zadáno)"
        max_tokens = self._max_request_tokens(ui_state.model)
        max_dialog_tokens = max(128, int(max_tokens * 0.5))
        if self._estimate_tokens(dialog) <= max_dialog_tokens:
            return dialog
        self._log(
            f"{stage}: zadání je dlouhé ({self._estimate_tokens(dialog)} tokenů); "
            "komprimuji po chunkech."
        )
        return self._compress_text_by_chunks(
            stage,
            "dialog",
            dialog,
            ui_state,
            max_dialog_tokens,
        )

    def _extract_response_text(self, response: Dict[str, Any]) -> str:
        if not response:
            raise ValueError("Response je prázdná.")
        if isinstance(response.get("output_text"), str):
            return response["output_text"].strip()
        if isinstance(response.get("text"), str):
            return response["text"].strip()
        output = response.get("output")
        if isinstance(output, list):
            parts: List[str] = []
            for item in output:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "message":
                    continue
                for content in item.get("content", []) or []:
                    if not isinstance(content, dict):
                        continue
                    if content.get("type") in {"output_text", "text"}:
                        text = content.get("text") or ""
                        parts.append(text)
            if parts:
                return "\n".join(parts).strip()
        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            message = choices[0].get("message", {})
            content = message.get("content")
            if isinstance(content, str):
                return content.strip()
        raise ValueError("Nelze extrahovat text odpovědi z response.")

    def _extract_json_block(self, text: str, start_index: int) -> str:
        if start_index < 0 or start_index >= len(text):
            raise ValueError("Neplatný start JSON bloku.")
        start_char = text[start_index]
        if start_char not in "{[":
            raise ValueError("JSON blok musí začínat { nebo [.")
        stack: List[str] = []
        in_string = False
        escape = False
        for idx in range(start_index, len(text)):
            char = text[idx]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue
            if char == '"':
                in_string = True
                continue
            if char in "{[":
                stack.append(char)
                continue
            if char in "}]":
                if not stack:
                    raise ValueError("Neplatné uzavření JSON bloku.")
                opener = stack.pop()
                if opener == "{" and char != "}":
                    raise ValueError("Neplatné uzavření JSON bloku.")
                if opener == "[" and char != "]":
                    raise ValueError("Neplatné uzavření JSON bloku.")
                if not stack:
                    return text[start_index : idx + 1]
        raise ValueError("JSON blok není korektně uzavřen.")

    def _iter_json_candidates(self, text: str) -> Iterable[str]:
        if text:
            yield text
        for match in re.finditer(r"```[a-zA-Z0-9_-]*\s*(.*?)```", text, re.S):
            snippet = match.group(1).strip()
            if snippet:
                yield snippet
        for idx, char in enumerate(text):
            if char not in "{[":
                continue
            try:
                block = self._extract_json_block(text, idx)
            except ValueError:
                continue
            if block:
                yield block

    def _looks_escaped_json(self, text: str) -> bool:
        return any(token in text for token in ("\\\"", "\\n", "\\r", "\\t", "\\u"))

    def _unescape_json_text(self, text: str) -> str:
        try:
            return text.encode("utf-8").decode("unicode_escape")
        except UnicodeDecodeError:
            return text

    def _try_parse_json_candidate(self, text: str) -> Any | None:
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = None
        if isinstance(payload, str):
            stripped = payload.strip()
            if stripped[:1] in "{[":
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    return None
            return None
        if payload is not None:
            return payload
        if self._looks_escaped_json(text):
            unescaped = self._unescape_json_text(text)
            if unescaped != text:
                try:
                    payload = json.loads(unescaped)
                except json.JSONDecodeError:
                    payload = None
                if isinstance(payload, str):
                    stripped = payload.strip()
                    if stripped[:1] in "{[":
                        try:
                            return json.loads(stripped)
                        except json.JSONDecodeError:
                            return None
                    return None
                if payload is not None:
                    return payload
        return None

    def _select_payload_object(
        self,
        payload: Any,
        expected_contract: str,
    ) -> Dict[str, Any] | None:
        if isinstance(payload, dict):
            if not expected_contract or payload.get("contract") == expected_contract:
                return payload
            return None
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    if not expected_contract or item.get("contract") == expected_contract:
                        return item
        return None

    def _coerce_json_payload(
        self,
        text: str,
        expected_contract: str,
    ) -> Dict[str, Any]:
        fallback: Dict[str, Any] | None = None
        for candidate in self._iter_json_candidates(text):
            payload = self._try_parse_json_candidate(candidate)
            if payload is None:
                continue
            selected = self._select_payload_object(payload, expected_contract)
            if selected is not None:
                return selected
            if fallback is None and isinstance(payload, dict):
                fallback = payload
            elif fallback is None and isinstance(payload, list):
                for item in payload:
                    if isinstance(item, dict):
                        fallback = item
                        break
        if fallback is not None:
            return fallback
        raise ValueError("Nenalezen validní JSON payload.")

    def _estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, len(text) // 4)

    def _model_context_limit(self, model: str | None) -> int:
        if not model:
            return DEFAULT_CONTEXT_LIMIT
        name = model.lower()
        for marker, size in (
            ("128k", 128000),
            ("64k", 64000),
            ("32k", 32768),
            ("16k", 16384),
        ):
            if marker in name:
                return size
        if name.startswith(("gpt-4o", "gpt-4.1")):
            return 128000
        if name.startswith(("gpt-4-turbo", "gpt-4-1106", "gpt-4-0125")):
            return 128000
        if name.startswith("gpt-4-32k"):
            return 32768
        if name.startswith("gpt-4"):
            return 8192
        if name.startswith("gpt-3.5-turbo-16k"):
            return 16384
        if name.startswith("gpt-3.5"):
            return 4096
        return DEFAULT_CONTEXT_LIMIT

    def _max_request_tokens(self, model: str | None) -> int:
        limit = self._model_context_limit(model)
        reserve = max(1024, int(limit * 0.2))
        return max(256, limit - reserve)

    def _estimate_request_tokens(self, instructions: str, input_text: str) -> int:
        combined = "\n".join(part for part in (instructions, input_text) if part)
        return self._estimate_tokens(combined)

    def _estimate_payload_tokens(self, payload: Dict[str, Any]) -> int:
        return self._estimate_tokens(self._extract_request_text(payload))

    def _ensure_payload_within_limits(
        self,
        stage: str,
        payload: Dict[str, Any],
        ui_state: UiState,
    ) -> None:
        max_tokens = self._max_request_tokens(ui_state.model)
        estimated = self._estimate_payload_tokens(payload)
        if estimated > max_tokens:
            raise ValueError(
                f"{stage}: request je příliš dlouhý ({estimated} tokenů > {max_tokens}). "
                "Zkraťte zadání nebo jej rozdělte na části."
            )

    def _build_prompt_trim_payload(
        self,
        stage: str,
        instructions: str,
        input_text: str,
        ui_state: UiState,
        max_tokens: int,
    ) -> Dict[str, Any]:
        trim_instructions = (
            "Jsi kompresní modul. Výstup musí být JEDINÝ validní JSON bez markdownu."
            f" Kontrakt: {PROMPT_TRIM_CONTRACT}."
            " Zkrať vstupní texty a rozděl je na instructions a input_text."
            " Obě pole musí obsahovat kontrakt, pravidla i obsah dialogového okna"
            " (zhuštěně, bez ztráty významu). Zachovej explicitní JSON kontrakty"
            " beze změny. Neopakuje se stejný text v obou polích, ale obě musí být"
            f" plnohodnotné. Celková délka instructions+input_text <= {max_tokens}"
            " tokenů (1 token ~ 4 znaky)."
        )
        trim_input = (
            f"STAGE: {stage}\n"
            f"MAX_TOKENS: {max_tokens}\n\n"
            "PŮVODNÍ INSTRUCTIONS:\n<<<\n"
            f"{instructions}\n"
            ">>>\n\n"
            "PŮVODNÍ INPUT_TEXT:\n<<<\n"
            f"{input_text}\n"
            ">>>\n\n"
            "VÝSTUP (JSON): "
            f'{{"contract":"{PROMPT_TRIM_CONTRACT}","instructions":"...","input_text":"...","notes":[...]}}'
        )
        return {
            "model": ui_state.model or "gpt-4o",
            "temperature": 0,
            "instructions": trim_instructions,
            "input": [{"role": "user", "content": [{"type": "input_text", "text": trim_input}]}],
        }

    def _parse_prompt_trim_response(self, response: Dict[str, Any]) -> Tuple[str, str]:
        text = self._extract_response_text(response)
        payload = self._coerce_json_payload(text, PROMPT_TRIM_CONTRACT)
        if not isinstance(payload, dict):
            raise ValueError("Trim response není objekt.")
        instructions = payload.get("instructions")
        input_text = payload.get("input_text")
        if not isinstance(instructions, str) or not instructions.strip():
            raise ValueError("Trim response neobsahuje instructions.")
        if not isinstance(input_text, str) or not input_text.strip():
            raise ValueError("Trim response neobsahuje input_text.")
        return instructions.strip(), input_text.strip()

    def _maybe_trim_prompt_texts(
        self,
        stage: str,
        instructions: str,
        input_text: str,
        ui_state: UiState,
    ) -> Tuple[str, str]:
        if not instructions and not input_text:
            return instructions, input_text
        max_tokens = self._max_request_tokens(ui_state.model)
        context_limit = self._model_context_limit(ui_state.model)
        estimated = self._estimate_request_tokens(instructions, input_text)
        if estimated <= max_tokens:
            return instructions, input_text
        if estimated > context_limit:
            raise ValueError(
                f"{stage}: zadání je příliš dlouhé i pro dotaz na zkrácení "
                f"({estimated} tokenů > {context_limit}). "
                "Zkraťte zadání nebo jej rozdělte na části."
            )
        self._log(
            f"{stage}: zadání je příliš dlouhé ({estimated} tokenů > {max_tokens}); "
            "spouštím zkracovací dotaz."
        )
        trim_payload = self._build_prompt_trim_payload(
            stage,
            instructions,
            input_text,
            ui_state,
            max_tokens,
        )
        if self._estimate_payload_tokens(trim_payload) > context_limit:
            raise ValueError(
                f"{stage}: zadání je příliš dlouhé i pro dotaz na zkrácení "
                f"({estimated} tokenů > {context_limit}). "
                "Zkraťte zadání nebo jej rozdělte na části."
            )
        response = self._send_request(
            f"{stage}_TRIM",
            trim_payload,
            ui_state,
            update_response_id=False,
        )
        trimmed_instructions, trimmed_input = self._parse_prompt_trim_response(response)
        trimmed_estimate = self._estimate_request_tokens(
            trimmed_instructions,
            trimmed_input,
        )
        if trimmed_estimate > max_tokens:
            raise ValueError(
                f"{stage}: zkrácené zadání je stále příliš dlouhé "
                f"({trimmed_estimate} tokenů > {max_tokens}). "
                "Zkraťte zadání nebo jej rozdělte na části."
            )
        self._log(
            f"{stage}: zadání zkráceno na ~{trimmed_estimate} tokenů."
        )
        return trimmed_instructions, trimmed_input

    def _extract_request_text(self, payload: Dict[str, Any]) -> str:
        parts: List[str] = []

        def collect(value: Any) -> None:
            if value is None:
                return
            if isinstance(value, str):
                if value:
                    parts.append(value)
                return
            if isinstance(value, dict):
                value_type = value.get("type")
                text_value = value.get("text")
                if isinstance(text_value, str) and value_type in {"input_text", "text", "output_text"}:
                    parts.append(text_value)
                if isinstance(text_value, str) and value_type is None:
                    parts.append(text_value)
                content = value.get("content")
                if content is not None:
                    collect(content)
                return
            if isinstance(value, list):
                for item in value:
                    collect(item)

        instructions = payload.get("instructions")
        if isinstance(instructions, str):
            parts.append(instructions)
        collect(payload.get("input"))
        return "\n".join([part for part in parts if part]).strip()

    def _record_pricing_step(
        self,
        stage: str,
        payload: Dict[str, Any],
        response: Dict[str, Any],
        ui_state: UiState,
    ) -> None:
        request_text = self._extract_request_text(payload)
        try:
            response_text = self._extract_response_text(response)
        except Exception:
            response_text = ""
        rates = self._price_catalog.get_rates(ui_state.model)
        estimated_input_tokens = self._estimate_tokens(request_text)
        estimated_output_tokens = self._estimate_tokens(response_text)
        estimated_input_cost = estimated_input_tokens * rates["input_token_rate"]
        estimated_output_cost = estimated_output_tokens * rates["output_token_rate"]
        discount = rates.get("batch_discount", 1.0) if stage == "C" else 1.0
        estimated_total = round((estimated_input_cost + estimated_output_cost) * discount, 6)

        usage = response.get("usage") if isinstance(response, dict) else None
        actual_input_tokens = None
        actual_output_tokens = None
        if isinstance(usage, dict):
            actual_input_tokens = usage.get("input_tokens")
            actual_output_tokens = usage.get("output_tokens")
        actual_total = None
        actual_input_cost = None
        actual_output_cost = None
        if isinstance(actual_input_tokens, int) and isinstance(actual_output_tokens, int):
            actual_input_cost = actual_input_tokens * rates["input_token_rate"]
            actual_output_cost = actual_output_tokens * rates["output_token_rate"]
            actual_total = round((actual_input_cost + actual_output_cost) * discount, 6)

        self._pricing_step_index += 1
        self._pricing_steps.append(
            {
                "index": self._pricing_step_index,
                "stage": stage,
                "model": ui_state.model or "gpt-4o",
                "response_id": response.get("id") or response.get("response_id") or "",
                "request_chars": len(request_text),
                "response_chars": len(response_text),
                "estimated": {
                    "input_tokens": estimated_input_tokens,
                    "output_tokens": estimated_output_tokens,
                    "input_cost": estimated_input_cost,
                    "output_cost": estimated_output_cost,
                    "discount_factor": discount,
                    "total_cost": estimated_total,
                },
                "actual": None
                if actual_total is None
                else {
                    "input_tokens": actual_input_tokens,
                    "output_tokens": actual_output_tokens,
                    "input_cost": actual_input_cost,
                    "output_cost": actual_output_cost,
                    "discount_factor": discount,
                    "total_cost": actual_total,
                },
                "pricing_status": self._price_catalog.status_text(),
            }
        )

    def _build_request_payload(
        self,
        template_key: str,
        replacements: Dict[str, str],
        assets: RequestAssets,
        ui_state: UiState,
        *,
        previous_response_id: str = "",
        include_mirror: bool,
        include_diagnostics: bool,
        include_attachments: bool,
        input_suffix: str = "",
        extra_input_blocks: Sequence[str] | None = None,
        dialog_label: str = "",
        dialog_content: str = "",
    ) -> Dict[str, Any]:
        template = dict(self._request_templates[template_key])
        model = ui_state.model or "gpt-4o"
        template["model"] = model
        instructions = self._render_template_text(
            template.get("instructions", ""),
            replacements,
        )
        core_instructions = instructions
        input_text = self._render_template_text(
            template.get("input", ""),
            replacements,
        )
        for block in extra_input_blocks or []:
            if block:
                input_text = f"{input_text}\n\n{block}"
        if input_suffix:
            input_text = f"{input_text}\n{input_suffix}"
        dialog_block = self._format_dialog_block(dialog_label, dialog_content)
        if dialog_block:
            instructions = f"{instructions}\n\n{dialog_block}"
            input_text = (
                f"{input_text}\n\n{dialog_block}\n\nPRAVIDLA A KONTRAKT:\n{core_instructions}"
            )
        strict_block = self._strict_rules_block(template_key)
        if strict_block:
            instructions = f"{instructions}\n\n{strict_block}"
            input_text = f"{input_text}\n\n{strict_block}"
        instructions = self._build_instructions_text(
            instructions,
            assets,
            ui_state,
            include_mirror=include_mirror,
            include_diagnostics=include_diagnostics,
            include_design_standard=self._include_design_standard_for(template_key),
        )
        input_text = self._build_input_text_with_assets(
            input_text,
            assets,
            ui_state,
            include_mirror=include_mirror,
            include_diagnostics=include_diagnostics,
        )
        instructions, input_text = self._maybe_trim_prompt_texts(
            template_key,
            instructions,
            input_text,
            ui_state,
        )
        template["instructions"] = instructions
        template["input"] = self._build_input_parts(
            input_text,
            assets,
            include_attachments=include_attachments,
            include_mirror=include_mirror,
            include_diagnostics=include_diagnostics,
        )
        if previous_response_id:
            template["previous_response_id"] = previous_response_id
        else:
            template.pop("previous_response_id", None)
        if "tools" in template:
            if assets.file_search_enabled and assets.vector_store_id:
                template["tools"] = [
                    {
                        "type": "file_search",
                        "vector_store_ids": [assets.vector_store_id],
                    }
                ]
            else:
                template.pop("tools", None)
        if not self._model_capabilities.get("supports_temperature", False):
            template.pop("temperature", None)
        self._ensure_payload_within_limits(template_key, template, ui_state)
        return template

    def _send_request(
        self,
        stage: str,
        payload: Dict[str, Any],
        ui_state: UiState,
        assets: RequestAssets | None = None,
        *,
        update_response_id: bool = True,
    ) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("OpenAI client není nakonfigurován.")
        request_id = uuid.uuid4().hex[:8]
        self._notify_progress(f"{stage}: sestavuji request")
        payload_json = _ensure_json_serializable(payload)
        payload_json["ui_state_snapshot"] = self._request_snapshot or {}
        request_log = log_request(
            self._run,
            payload_json,
            stage=stage,
            project_name=ui_state.project_name or "Kaja",
            response_id=self._response_id,
            request_id=request_id,
        )
        self._register_log_entry(
            request_log, "request", {"stage": stage, "request_id": request_id}
        )
        allowed_keys = {"model", "temperature", "instructions", "input", "previous_response_id", "tools"}
        api_payload = {k: v for k, v in payload.items() if k in allowed_keys}
        temp_adjusted = False
        tools_adjusted = False
        self._notify_progress(f"{stage}: odesílám request")
        while True:
            try:
                response = self._client.create_response(api_payload)
                break
            except Exception as exc:
                message = str(exc).lower()
                if (
                    not temp_adjusted
                    and "temperature" in message
                    and ("unsupported" in message or "unexpected" in message)
                    and "temperature" in api_payload
                ):
                    temp_adjusted = True
                    self._log("Model nepodporuje temperature; opakuji bez temperature.")
                    api_payload.pop("temperature", None)
                    self._model_capabilities["supports_temperature"] = False
                    continue
                if not tools_adjusted and ("file_search" in message or "tool" in message):
                    if "tools" in api_payload:
                        tools_adjusted = True
                        self._log("Model nepodporuje file_search; opakuji bez tools.")
                        api_payload.pop("tools", None)
                        if assets is not None:
                            assets.file_search_enabled = False
                            assets.vector_store_id = None
                        continue
                raise
        current_response_id = (
            response.get("id")
            or response.get("response_id")
            or response.get("run_id")
            or self._response_id
        )
        self._response_id = current_response_id
        self._notify_progress(f"{stage}: odpověď přijata")
        response_log = log_response(
            self._run,
            response,
            stage=stage,
            project_name=ui_state.project_name or "Kaja",
            response_id=current_response_id,
            request_id=request_id,
        )
        self._register_log_entry(
            response_log,
            "response",
            {
                "stage": stage,
                "response_id": current_response_id,
                "request_id": request_id,
            },
        )
        try:
            self._record_pricing_step(stage, api_payload, response, ui_state)
        except Exception as exc:
            self._log(f"Pricing step selhal ({stage}): {exc}")
        return response

    def _parse_json_response(
        self,
        response: Dict[str, Any],
        expected_contract: str,
        *,
        assets: RequestAssets | None = None,
    ) -> Dict[str, Any]:
        text = self._extract_response_text(response)
        try:
            payload = self._coerce_json_payload(text, expected_contract)
        except ValueError as exc:
            raise ValueError(f"Odpověď není validní JSON pro {expected_contract}: {exc}") from exc
        self._validate_contract(payload, expected_contract, assets)
        return payload

    def _validate_contract(
        self,
        payload: Dict[str, Any],
        expected_contract: str,
        assets: RequestAssets | None,
    ) -> None:
        if not isinstance(payload, dict):
            raise ValueError(f"Výstup pro {expected_contract} není objekt.")
        contract_value = payload.get("contract")
        if contract_value != expected_contract:
            raise ValueError(f"Kontrakt neodpovídá {expected_contract}: {contract_value}")
        if expected_contract == "A1_PLAN":
            self._validate_a1_plan(payload)
        elif expected_contract == "A2_STRUCTURE":
            self._validate_a2_structure(payload)
        elif expected_contract == FILE_MAP_CONTRACT:
            self._validate_a2x_file_map(payload)
        elif expected_contract == "A3_FILE":
            self._validate_a3_file(payload)
        elif expected_contract == "B1_PLAN":
            self._validate_b1_plan(payload)
        elif expected_contract == "B2_STRUCTURE":
            self._validate_b2_structure(payload, assets)
        elif expected_contract == "B3_FILE":
            self._validate_b3_file(payload, assets)
        elif expected_contract == "C_FILES_ALL":
            self._validate_c_files(payload)
        else:
            raise ValueError(f"Neznámý kontrakt: {expected_contract}")

    def _validate_a1_plan(self, payload: Dict[str, Any]) -> None:
        for key in ("project", "assumptions", "requirements", "architecture", "build_run", "deliverable_policy"):
            if key not in payload:
                raise ValueError(f"A1_PLAN: chybí {key}.")
        project = payload["project"]
        self._require_keys(project, {"name", "one_liner", "target_os", "language", "runtime"}, "A1_PLAN.project")
        requirements = payload["requirements"]
        self._require_keys(requirements, {"functional", "non_functional", "constraints"}, "A1_PLAN.requirements")

    def _validate_a2_structure(self, payload: Dict[str, Any]) -> None:
        files = payload.get("files")
        if not isinstance(files, list):
            raise ValueError("A2_STRUCTURE.files musí být list.")
        seen: set[str] = set()
        for entry in files:
            if not isinstance(entry, dict):
                raise ValueError("A2_STRUCTURE.files obsahuje neplatnou položku.")
            path = entry.get("path")
            self._validate_path_rules(path, "A2_STRUCTURE.path")
            if path in seen:
                raise ValueError(f"A2_STRUCTURE obsahuje duplicitní path {path}.")
            seen.add(path)
            if entry.get("generated_in_phase") != "A3":
                raise ValueError("A2_STRUCTURE.generated_in_phase musí být 'A3'.")

    def _validate_a2x_file_map(self, payload: Dict[str, Any]) -> None:
        root = payload.get("root")
        if not isinstance(root, str) or not root.strip():
            raise ValueError("A2X_FILE_MAP.root musí být string.")
        files = payload.get("files")
        if not isinstance(files, list):
            raise ValueError("A2X_FILE_MAP.files musí být list.")
        expected = {path for path in self._expected_a2_paths if isinstance(path, str)}
        seen: set[str] = set()
        export_names: set[str] = set()
        exports_by_path: Dict[str, set[str]] = {}
        for entry in files:
            if not isinstance(entry, dict):
                raise ValueError("A2X_FILE_MAP.files obsahuje neplatnou položku.")
            path = entry.get("path")
            self._validate_path_rules(path, "A2X_FILE_MAP.path")
            if path in seen:
                raise ValueError(f"A2X_FILE_MAP obsahuje duplicitní path {path}.")
            seen.add(path)
            purpose = entry.get("purpose")
            language = entry.get("language")
            if not isinstance(purpose, str) or not purpose.strip():
                raise ValueError("A2X_FILE_MAP.purpose musí být string.")
            if not isinstance(language, str) or not language.strip():
                raise ValueError("A2X_FILE_MAP.language musí být string.")
            exports = entry.get("exports", [])
            if not isinstance(exports, list):
                raise ValueError("A2X_FILE_MAP.exports musí být list.")
            export_set: set[str] = set()
            for export in exports:
                if not isinstance(export, dict):
                    raise ValueError("A2X_FILE_MAP.exports obsahuje neplatnou položku.")
                name = export.get("name")
                kind = export.get("kind")
                signature = export.get("signature")
                if not isinstance(name, str) or not name.strip():
                    raise ValueError("A2X_FILE_MAP.exports.name musí být string.")
                if not isinstance(kind, str) or not kind.strip():
                    raise ValueError("A2X_FILE_MAP.exports.kind musí být string.")
                if not isinstance(signature, str) or not signature.strip():
                    raise ValueError("A2X_FILE_MAP.exports.signature musí být string.")
                if name in export_names:
                    raise ValueError(f"A2X_FILE_MAP duplicitní export {name}.")
                export_names.add(name)
                export_set.add(name)
            exports_by_path[path] = export_set
            imports = entry.get("imports", [])
            if not isinstance(imports, list):
                raise ValueError("A2X_FILE_MAP.imports musí být list.")
            for item in imports:
                if not isinstance(item, dict):
                    raise ValueError("A2X_FILE_MAP.imports obsahuje neplatnou položku.")
                import_path = item.get("path")
                symbols = item.get("symbols")
                if not isinstance(import_path, str) or not import_path.strip():
                    raise ValueError("A2X_FILE_MAP.imports.path musí být string.")
                if not isinstance(symbols, list) or not symbols:
                    raise ValueError("A2X_FILE_MAP.imports.symbols musí být neprázdný list.")
                for symbol in symbols:
                    if not isinstance(symbol, str) or not symbol.strip():
                        raise ValueError("A2X_FILE_MAP.imports.symbols musí být string.")
                if not self._is_external_import(import_path):
                    self._validate_path_rules(import_path, "A2X_FILE_MAP.imports.path")
        if expected and seen != expected:
            missing = sorted(expected - seen)
            extra = sorted(seen - expected)
            raise ValueError(
                "A2X_FILE_MAP neodpovídá A2_STRUCTURE. "
                f"Chybí={missing}, navíc={extra}."
            )
        for entry in files:
            imports = entry.get("imports", [])
            if not isinstance(imports, list):
                continue
            for item in imports:
                if not isinstance(item, dict):
                    continue
                import_path = item.get("path")
                symbols = item.get("symbols")
                if not isinstance(import_path, str) or not isinstance(symbols, list):
                    continue
                if self._is_external_import(import_path):
                    continue
                if import_path not in exports_by_path:
                    raise ValueError(f"A2X_FILE_MAP importuje neznámý soubor {import_path}.")
                for symbol in symbols:
                    if symbol not in exports_by_path[import_path]:
                        raise ValueError(
                            f"A2X_FILE_MAP importuje neznámý symbol {symbol} z {import_path}."
                        )

    def _validate_a3_file(self, payload: Dict[str, Any]) -> None:
        self._validate_path_rules(payload.get("path"), "A3_FILE.path")
        self._validate_chunking(payload.get("chunking"), "A3_FILE.chunking")
        if not isinstance(payload.get("content"), str):
            raise ValueError("A3_FILE.content musí být string.")

    def _validate_b1_plan(self, payload: Dict[str, Any]) -> None:
        for key in ("context", "diagnosis", "change_plan", "missing_inputs"):
            if key not in payload:
                raise ValueError(f"B1_PLAN: chybí {key}.")
        context = payload["context"]
        self._require_keys(context, {"vector_store_ids", "assumed_root"}, "B1_PLAN.context")
        diagnosis = payload["diagnosis"]
        self._require_keys(diagnosis, {"summary", "evidence", "likely_root_causes"}, "B1_PLAN.diagnosis")
        change_plan = payload["change_plan"]
        self._require_keys(
            change_plan,
            {"goals", "files_to_modify", "files_to_add", "verification_steps"},
            "B1_PLAN.change_plan",
        )

    def _validate_b2_structure(self, payload: Dict[str, Any], assets: RequestAssets | None) -> None:
        touched = payload.get("touched_files")
        if not isinstance(touched, list):
            raise ValueError("B2_STRUCTURE.touched_files musí být list.")
        seen: set[str] = set()
        existing = {entry.path for entry in (assets.mirror_entries if assets else [])}
        for entry in touched:
            if not isinstance(entry, dict):
                raise ValueError("B2_STRUCTURE.touched_files obsahuje neplatnou položku.")
            path = entry.get("path")
            self._validate_path_rules(path, "B2_STRUCTURE.path")
            if path in seen:
                raise ValueError(f"B2_STRUCTURE duplicitní path {path}.")
            seen.add(path)
            action = entry.get("action")
            if action not in {"modify", "add"}:
                raise ValueError("B2_STRUCTURE.action musí být modify nebo add.")
            if action == "modify" and existing and path not in existing:
                raise ValueError(f"B2_STRUCTURE modify neexistuje ve store: {path}.")

    def _validate_b3_file(self, payload: Dict[str, Any], assets: RequestAssets | None) -> None:
        self._validate_path_rules(payload.get("path"), "B3_FILE.path")
        action = payload.get("action")
        if action not in {"modify", "add"}:
            raise ValueError("B3_FILE.action musí být modify nebo add.")
        if action == "modify" and assets:
            existing = {entry.path for entry in assets.mirror_entries}
            if existing and payload.get("path") not in existing:
                raise ValueError("B3_FILE modify neexistuje ve store.")
        self._validate_chunking(payload.get("chunking"), "B3_FILE.chunking")
        if not isinstance(payload.get("content"), str):
            raise ValueError("B3_FILE.content musí být string.")
        notes = payload.get("notes")
        if notes is not None and not isinstance(notes, list):
            raise ValueError("B3_FILE.notes musí být list.")

    def _validate_c_files(self, payload: Dict[str, Any]) -> None:
        project = payload.get("project")
        if not isinstance(project, dict):
            raise ValueError("C_FILES_ALL.project musí být objekt.")
        self._require_keys(project, {"name", "target_os", "runtime", "language"}, "C_FILES_ALL.project")
        files = payload.get("files")
        if not isinstance(files, list):
            raise ValueError("C_FILES_ALL.files musí být list.")
        seen: set[str] = set()
        for entry in files:
            if not isinstance(entry, dict):
                raise ValueError("C_FILES_ALL.files obsahuje neplatnou položku.")
            path = entry.get("path")
            self._validate_path_rules(path, "C_FILES_ALL.path")
            if path in seen:
                raise ValueError(f"C_FILES_ALL duplicitní path {path}.")
            seen.add(path)
            if not isinstance(entry.get("content"), str):
                raise ValueError("C_FILES_ALL.files.content musí být string.")
        build_run = payload.get("build_run")
        if not isinstance(build_run, dict):
            raise ValueError("C_FILES_ALL.build_run musí být objekt.")
        self._require_keys(build_run, {"prerequisites", "commands", "verification"}, "C_FILES_ALL.build_run")
        notes = payload.get("notes")
        if notes is not None and not isinstance(notes, list):
            raise ValueError("C_FILES_ALL.notes musí být list.")

    def _validate_c_script_expectation(self, payload: Dict[str, Any], ui_state: UiState) -> None:
        if not (ui_state.diagnostics.windows_out or ui_state.diagnostics.ssh_out):
            return
        files = payload.get("files") or []
        names = {Path(entry.get("path", "")).name.lower() for entry in files if isinstance(entry, dict)}
        if "readmerepair.txt" not in names:
            raise ValueError("C_FILES_ALL musí obsahovat readmerepair.txt.")
        script_exts = {".bat", ".cmd", ".ps1", ".sh"}
        has_script = False
        for entry in files:
            if not isinstance(entry, dict):
                continue
            suffix = Path(entry.get("path", "")).suffix.lower()
            if suffix in script_exts:
                has_script = True
                break
        if not has_script:
            raise ValueError("C_FILES_ALL musí obsahovat skript.")

    def _validate_script_expectation_in_structure(
        self,
        files: Sequence[Dict[str, Any]],
        ui_state: UiState,
        label: str,
    ) -> None:
        if not (ui_state.diagnostics.windows_out or ui_state.diagnostics.ssh_out):
            return
        names = {Path(entry.get("path", "")).name.lower() for entry in files if isinstance(entry, dict)}
        if "readmerepair.txt" not in names:
            raise ValueError(f"{label} musí obsahovat readmerepair.txt.")
        script_exts = {".bat", ".cmd", ".ps1", ".sh"}
        has_script = False
        for entry in files:
            if not isinstance(entry, dict):
                continue
            suffix = Path(entry.get("path", "")).suffix.lower()
            if suffix in script_exts:
                has_script = True
                break
        if not has_script:
            raise ValueError(f"{label} musí obsahovat skript.")

    def _validate_chunking(self, chunking: Any, label: str) -> None:
        if not isinstance(chunking, dict):
            raise ValueError(f"{label} musí být objekt.")
        required = {"max_lines", "chunk_index", "chunk_count", "has_more", "next_chunk_index"}
        self._require_keys(chunking, required, label)
        if chunking.get("max_lines") != MAX_CHUNK_LINES:
            raise ValueError(f"{label}.max_lines musí být {MAX_CHUNK_LINES}.")
        if not isinstance(chunking.get("chunk_index"), int):
            raise ValueError(f"{label}.chunk_index musí být int.")
        if not isinstance(chunking.get("chunk_count"), int):
            raise ValueError(f"{label}.chunk_count musí být int.")
        if not isinstance(chunking.get("has_more"), bool):
            raise ValueError(f"{label}.has_more musí být bool.")
        next_index = chunking.get("next_chunk_index")
        if next_index is not None and not isinstance(next_index, int):
            raise ValueError(f"{label}.next_chunk_index musí být int nebo null.")
        if chunking.get("has_more") and next_index is None:
            raise ValueError(f"{label}.next_chunk_index musí být vyplněn, pokud has_more=True.")

    def _validate_path_rules(self, path: Any, label: str) -> None:
        if not isinstance(path, str) or not path:
            raise ValueError(f"{label} musí být neprázdný string.")
        if path.startswith("/"):
            raise ValueError(f"{label} nesmí začínat '/'.")
        if ".." in path:
            raise ValueError(f"{label} nesmí obsahovat '..'.")
        if "\\" in path:
            raise ValueError(f"{label} nesmí obsahovat '\\\\'.")

    @staticmethod
    def _is_external_import(path: str) -> bool:
        lowered = (path or "").strip().lower()
        return lowered.startswith(
            (
                "external:",
                "stdlib:",
                "builtin:",
                "pip:",
                "npm:",
            )
        )

    @staticmethod
    def _build_export_index(files: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        for entry in files:
            exports = entry.get("exports") if isinstance(entry, dict) else None
            if not isinstance(exports, list):
                continue
            for export in exports:
                if not isinstance(export, dict):
                    continue
                name = export.get("name")
                if not isinstance(name, str) or not name:
                    continue
                index[name] = {
                    "path": entry.get("path"),
                    "kind": export.get("kind"),
                    "signature": export.get("signature"),
                }
        return index

    def _require_keys(self, payload: Dict[str, Any], keys: set[str], label: str) -> None:
        if not isinstance(payload, dict):
            raise ValueError(f"{label} musí být objekt.")
        for key in keys:
            if key not in payload:
                raise ValueError(f"{label} chybí {key}.")

    def execute(
        self,
        mode: str,
        ui_state: UiState,
        user_spec: str,
        attachments: Sequence[FileRecord],
        vector_store_ids: Sequence[str],
        *,
        response_id: Optional[str] = None,
        progress_callback: Optional[ProgressCallback] = None,
        stop_check: Optional[StopCheck] = None,
        request_snapshot: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        stop_check = stop_check or (lambda: False)
        start_time = time.time()
        refreshed = self._price_catalog.refresh_if_needed(force=self._settings.pricing_auto_refresh)
        if refreshed:
            self._log("Ceník byl aktualizován před během.")
        else:
            self._log(f"Ceník: {self._price_catalog.status_text()}")
        summary_steps: List[str] = []
        base_callback = progress_callback or (lambda *_: None)
        def progress_wrapper(message: str, ratio: float) -> None:
            self._last_progress_update = time.time()
            self._last_progress_ratio = ratio
            base_callback(message, ratio)
        progress_callback = progress_wrapper
        self._progress_callback = progress_wrapper
        self._ensure_not_cancelled(stop_check)
        self._timeline.clear()
        self._pricing_steps.clear()
        self._pricing_step_index = 0
        self._request_snapshot = request_snapshot or {}
        self._versing_snapshot_path = None
        run_context = self._start_timeline_entry("RUN", {"mode": mode})

        self._ui_state = ui_state
        if ui_state.out_dir:
            self._out_root = Path(ui_state.out_dir)
        else:
            self._out_root = self._root_dir / "OUT"
        create_dir(self._out_root)
        self._model_capabilities = self._determine_model_capabilities(ui_state.model)
        requested_vector_store_ids = list(vector_store_ids)
        response_id = response_id or self.generate_response_id(mode)
        self._response_id = response_id
        self._collect_diagnostics_if_needed(ui_state, response_id)
        assets = self._prepare_request_assets(mode, ui_state, attachments)
        vector_store_in_use = [assets.vector_store_id] if assets.vector_store_id else []
        self._maybe_create_versing_snapshot(ui_state)
        metadata = self._build_run_metadata(
            mode,
            user_spec,
            attachments,
            vector_store_in_use,
            ui_state,
            response_id,
        )
        metadata_path = log_run_metadata(self._run, metadata)
        self._register_log_entry(metadata_path, "run_metadata", {"mode": mode})

        manifest_context = {
            "attachments": [
                {
                    "file_id": record.file_id,
                    "filename": record.filename,
                    "purpose": record.purpose,
                    "size_bytes": record.size_bytes,
                }
                for record in attachments
            ],
            "vector_store_ids": vector_store_in_use,
            "mode": mode,
            "response_id": response_id,
            "project": ui_state.project_name or "Kaja",
            "run_id": self._run.run_id,
        }
        manifest_context["vector_store_requested"] = requested_vector_store_ids
        manifest_context["vector_store_enabled"] = bool(vector_store_in_use)
        manifest_context["capabilities"] = self._model_capabilities
        if self._diagnostic_packages:
            manifest_context["diagnostics_snapshot"] = {
                scope: {
                    "root": str(package.root),
                    "manifest": str(package.manifest_path),
                    "submission": str(package.submission_path),
                    "notes": package.notes,
                    "metadata": package.metadata,
                }
                for scope, package in self._diagnostic_packages.items()
            }
        if self._diagnostic_uploads:
            manifest_context["diagnostics_uploads"] = self._diagnostic_uploads

        if mode == "GENERATE":
            files = self._run_generate(user_spec, assets, ui_state, progress_callback, stop_check)
            summary_steps.extend(["A1", "A2", "A2X", "A3"])
        elif mode == "MODIFY":
            files = self._run_modify(user_spec, assets, ui_state, progress_callback, stop_check)
            summary_steps.extend(["B1", "B2", "B3"])
        elif mode == "QA":
            files = self._run_qa(user_spec, assets, ui_state, progress_callback, stop_check)
            summary_steps.append("QA")
        elif mode == "C":
            files = self._run_send_as_c(user_spec, assets, ui_state, progress_callback, stop_check)
            summary_steps.append("C")
        else:
            raise ValueError(f"Nedefinovaný režim pipeline: {mode}")
        hook_results = self._run_post_hooks(ui_state)
        final_response_id = self._response_id

        duration = time.time() - start_time
        total_cost, pricing_details = self._estimate_cost(
            mode,
            files,
            summary_steps,
            attachments,
            vector_store_in_use,
            user_spec,
            ui_state,
        )
        per_call_pricing = self._summarize_pricing_steps()
        actual_total = None
        totals = per_call_pricing.get("totals") if isinstance(per_call_pricing, dict) else None
        if isinstance(totals, dict):
            actual = totals.get("actual")
            if isinstance(actual, dict):
                actual_total = actual.get("total_cost")
        pricing_details["per_call_pricing"] = per_call_pricing
        pricing_details["run_estimated_total_cost"] = total_cost
        pricing_details["run_actual_total_cost"] = actual_total
        display_total = actual_total if isinstance(actual_total, (int, float)) else total_cost
        receipt = Receipt(
            run_id=self._run.run_id,
            project=ui_state.project_name or "Kaja",
            model=ui_state.model or "gpt-4o",
            mode=mode,
            response_id=final_response_id,
            total_cost=display_total,
            details_json=json.dumps(pricing_details, ensure_ascii=False),
            created_at=datetime.utcnow().isoformat(),
            verified_pricing=pricing_details.get("verified", False),
        )
        receipt_path = log_pricing_receipt(self._run, self._settings, receipt)
        self._register_log_entry(
            receipt_path,
            "receipt",
            {"total_cost": display_total},
        )
        manifest_context.update(
            {
                "response_id": final_response_id,
                "files_written": [str(path) for path in files],
                "duration_s": round(duration, 2),
                "steps": summary_steps,
                "total_cost": display_total,
                "total_cost_estimated": total_cost,
                "total_cost_actual": actual_total,
                "pricing_receipt": self._relative_log_path(receipt_path),
                "ui_state_log": str(self._relative_log_path(self._ui_state_log_path))
                if self._ui_state_log_path
                else None,
                "log_files": list(self._log_entries),
                "dry_run_summary": self._dry_run_summary,
                "dry_run_summary_log": str(self._relative_log_path(self._dry_run_summary_log_path))
                if self._dry_run_summary_log_path
                else None,
                "post_run_hooks": hook_results,
                "design_verification": {
                    "theme": "black-white",
                    "font_family": "Montserrat",
                    "rounded_corners": True,
                    "manifest_reference": "yolo-design/references/design-manifest.md",
                    "notes": "UI changes were applied under yolo-design rules (2.02.000–2.06.001).",
                },
                "pricing_details": pricing_details,
                "pricing_catalog": self._price_catalog.summary(),
            }
        )
        timeline_path = log_timeline(self._run, self._timeline)
        self._register_log_entry(
            timeline_path,
            "timeline",
            {"entries": len(self._timeline)},
        )
        timeline_ref = self._relative_log_path(timeline_path)
        manifest_context.update(
            {
                "timeline": self._timeline,
                "timeline_log": timeline_ref,
            }
        )
        if self._versing_snapshot_path:
            manifest_context["versing_snapshot"] = str(self._versing_snapshot_path)
        manifest_path = log_manifest(self._run, manifest_context, "run_manifest")
        self._register_log_entry(
            manifest_path,
            "manifest",
            {"manifest": "run_manifest"},
        )
        manifest_ref = self._relative_log_path(manifest_path)
        log_dir_ref = str(Path(self._run.log_dir).relative_to(self._root_dir))
        run_index_entry = {
            "run_id": self._run.run_id,
            "project": ui_state.project_name or "Kaja",
            "mode": mode,
            "response_id": final_response_id,
            "status": "completed",
            "start": datetime.utcfromtimestamp(start_time).isoformat(),
            "end": datetime.utcnow().isoformat(),
            "duration_s": round(duration, 3),
            "manifest": manifest_ref,
            "timeline": timeline_ref,
            "log_dir": log_dir_ref,
            "diagnostics": self._describe_diagnostics(ui_state),
        }
        index_path = log_run_index(self._root_dir, run_index_entry)
        self._register_log_entry(
            index_path,
            "run_index",
            {"run_id": self._run.run_id},
        )
        self._finish_timeline_entry(run_context, "completed", {"response_id": final_response_id})
        if isinstance(actual_total, (int, float)):
            self._log(
                f"Cena runu: {actual_total:.4f} USD (odhad {total_cost:.4f} USD)"
            )
        else:
            self._log(f"Cena runu: {total_cost:.4f} USD")
        progress_callback("Dokončeno", 1.0)
        return PipelineResult(
            mode=mode,
            run_id=self._run.run_id,
            response_id=final_response_id,
            files_written=files,
            log_messages=summary_steps,
            timeline=list(self._timeline),
            timeline_log=timeline_ref,
            manifest_log=manifest_ref,
            dry_run_summary=self._dry_run_summary,
            post_hook_results=hook_results,
        )

    def _run_generate(
        self,
        user_spec: str,
        assets: RequestAssets,
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím sekvenci A1 → A2 → A2X → A3")
        self._load_request_templates()
        progress_callback("A1: plán projektu", 0.1)
        self._ensure_not_cancelled(stop_check)
        dialog_content = self._prepare_dialog_content("A1", user_spec, ui_state)
        a1_payload = self._build_request_payload(
            "A1",
            {"<USER_SPEC>": dialog_content},
            assets,
            ui_state,
            include_mirror=False,
            include_diagnostics=False,
            include_attachments=True,
            dialog_label="ZADÁNÍ PROGRAMU",
            dialog_content=dialog_content,
        )
        a1_response = self._send_request("A1", a1_payload, ui_state, assets)
        a1_data = self._parse_json_response(a1_response, "A1_PLAN", assets=assets)
        progress_callback("A2: struktura souborů", 0.25)
        self._ensure_not_cancelled(stop_check)
        a2_previous = self._resolve_previous_response_id(ui_state, self._response_id)
        a2_payload = self._build_request_payload(
            "A2",
            {},
            assets,
            ui_state,
            previous_response_id=a2_previous,
            include_mirror=False,
            include_diagnostics=False,
            include_attachments=True,
        )
        a2_response = self._send_request("A2", a2_payload, ui_state, assets)
        a2_data = self._parse_json_response(a2_response, "A2_STRUCTURE", assets=assets)
        a2_response_id = self._response_id
        files = a2_data.get("files", [])
        self._validate_script_expectation_in_structure(files, ui_state, "A2_STRUCTURE")
        self._expected_a2_paths = [
            entry.get("path")
            for entry in files
            if isinstance(entry, dict) and isinstance(entry.get("path"), str)
        ]
        progress_callback("A2X: mapování API", 0.30)
        self._ensure_not_cancelled(stop_check)
        dialog_block = self._format_dialog_block("ZADÁNÍ PROGRAMU", dialog_content)
        a1_block = self._format_json_block("A1_PLAN", a1_data)
        a2_block = self._format_json_block("A2_STRUCTURE", a2_data)
        a2x_contract = {
            "contract": FILE_MAP_CONTRACT,
            "root": "string",
            "files": [
                {
                    "path": "string",
                    "purpose": "string",
                    "language": "string",
                    "exports": [
                        {
                            "name": "string",
                            "kind": "string",
                            "signature": "string",
                        }
                    ],
                    "imports": [
                        {
                            "path": "string",
                            "symbols": ["string"],
                        }
                    ],
                }
            ],
            "invariants": ["string"],
        }
        a2x_contract_text = json.dumps(a2x_contract, ensure_ascii=False)
        rules = [
            "A2_STRUCTURE je jediný seznam souborů (žádné nové soubory).",
            "Každý path z A2_STRUCTURE musí být v A2X_FILE_MAP přesně jednou.",
            "exports uvádí veřejné symboly; signature musí být doslovný text v cílovém jazyce.",
            "imports.path musí být path z A2_STRUCTURE; externí importy označ prefixem external:.",
            "imports.symbols musí odpovídat exportům cílového souboru.",
            "Nepoužívej duplicitní názvy exportů napříč soubory.",
        ]
        core_instructions = (
            "Jsi deterministický mapovač API mezi soubory. "
            "OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown ani další text. "
            f"KONTRAKT {FILE_MAP_CONTRACT}: {a2x_contract_text}. "
            "PRAVIDLA: " + " ".join(rules)
        )
        a2x_instructions = f"{dialog_block}\n\n{core_instructions}"
        a2x_input = (
            "VSTUPY PRO MAPOVÁNÍ:\n"
            f"{a1_block}\n\n{a2_block}\n\n"
            "VYGENERUJ A2X_FILE_MAP dle A1/A2. REDUNDANTNĚ KONTRAKT: "
            "vrať pouze JSON dle A2X_FILE_MAP.\n\n"
            f"{dialog_block}\n\nPRAVIDLA A KONTRAKT:\n{core_instructions}"
        )
        a2x_instructions, a2x_input = self._maybe_trim_prompt_texts(
            "A2X",
            a2x_instructions,
            a2x_input,
            ui_state,
        )
        a2x_instructions = self._build_instructions_text(
            a2x_instructions,
            assets,
            ui_state,
            include_mirror=False,
            include_diagnostics=False,
            include_design_standard=False,
        )
        a2x_input = self._build_input_text_with_assets(
            a2x_input,
            assets,
            ui_state,
            include_mirror=False,
            include_diagnostics=False,
        )
        a2x_payload: Dict[str, Any] = {
            "model": ui_state.model or "gpt-4o",
            "temperature": 0.0,
            "instructions": a2x_instructions,
            "input": self._build_input_parts(
                a2x_input,
                assets,
                include_attachments=True,
                include_mirror=False,
                include_diagnostics=False,
            ),
        }
        a2x_previous = self._resolve_previous_response_id(ui_state, a2_response_id)
        if a2x_previous:
            a2x_payload["previous_response_id"] = a2x_previous
        if not self._model_capabilities.get("supports_temperature", False):
            a2x_payload.pop("temperature", None)
        self._ensure_payload_within_limits("A2X", a2x_payload, ui_state)
        a2x_response = self._send_request("A2X", a2x_payload, ui_state, assets)
        a2x_data = self._parse_json_response(a2x_response, FILE_MAP_CONTRACT, assets=assets)
        file_map_entries = a2x_data.get("files", [])
        if not isinstance(file_map_entries, list):
            file_map_entries = []
        file_map_by_path: Dict[str, Dict[str, Any]] = {}
        for entry in file_map_entries:
            if not isinstance(entry, dict):
                continue
            path = entry.get("path")
            if isinstance(path, str):
                file_map_by_path[path] = entry
        export_index = self._build_export_index(file_map_entries)
        export_index_list = [
            {
                "name": name,
                "path": info.get("path"),
                "kind": info.get("kind"),
                "signature": info.get("signature"),
            }
            for name, info in sorted(export_index.items())
        ]
        export_index_block = self._format_json_block("EXPORT_INDEX", export_index_list)
        invariants_block = ""
        invariants = a2x_data.get("invariants")
        if isinstance(invariants, list) and invariants:
            invariants_block = self._format_json_block("A2X_INVARIANTS", invariants)
        progress_callback("A3: generování obsahu souborů", 0.35)
        written: List[Path] = []
        per_file_budget = 0.65 / max(len(files), 1)
        base_a3_blocks = [a1_block, a2_block, export_index_block]
        if invariants_block:
            base_a3_blocks.append(invariants_block)
        for index, file_spec in enumerate(files):
            path = file_spec.get("path") if isinstance(file_spec, dict) else ""
            if not isinstance(path, str) or not path:
                continue
            percent_base = 0.35 + index * per_file_budget
            file_map_entry = file_map_by_path.get(path)
            if not isinstance(file_map_entry, dict):
                raise ValueError(f"A2X_FILE_MAP neobsahuje mapu pro {path}.")
            file_map_block = self._format_json_block(
                f"A2X_FILE_MAP_FOR_PATH={path}",
                file_map_entry,
            )
            base_extra_blocks = list(base_a3_blocks)
            base_extra_blocks.append(file_map_block)
            attempt = 0
            missing_exports: List[str] = []
            while attempt < 2:
                chunk_index = None
                extra_blocks = list(base_extra_blocks)
                if attempt > 0 and missing_exports:
                    extra_blocks.append(
                        self._format_json_block(
                            "A3_VALIDATION_ERRORS",
                            {"path": path, "missing_exports": missing_exports},
                        )
                    )
                while True:
                    self._ensure_not_cancelled(stop_check)
                    suffix = f"CHUNK_INDEX={chunk_index}" if chunk_index is not None else ""
                    a3_payload = self._build_request_payload(
                        "A3",
                        {"<PATH_FROM_A2>": path},
                        assets,
                        ui_state,
                        previous_response_id=self._resolve_previous_response_id(
                            ui_state, a2_response_id
                        ),
                        include_mirror=False,
                        include_diagnostics=False,
                        include_attachments=True,
                        input_suffix=suffix,
                        extra_input_blocks=extra_blocks,
                    )
                    a3_response = self._send_request("A3", a3_payload, ui_state, assets)
                    a3_data = self._parse_json_response(a3_response, "A3_FILE", assets=assets)
                    if a3_data.get("path") != path:
                        raise ValueError(
                            f"A3_FILE vrátil jiný path: {a3_data.get('path')} != {path}"
                        )
                    chunk_meta = a3_data["chunking"]
                    chunk_percent = percent_base + (chunk_meta["chunk_index"] + 1) * (
                        per_file_budget / max(chunk_meta["chunk_count"], 1)
                    )
                    progress_callback(
                        f"A3: {path} chunk {chunk_meta['chunk_index'] + 1}/{chunk_meta['chunk_count']}",
                        min(chunk_percent, 0.99),
                    )
                    self._write_chunk(path, {"chunking": chunk_meta, "content": a3_data["content"]})
                    if not chunk_meta["has_more"]:
                        break
                    chunk_index = chunk_meta["next_chunk_index"]
                file_path = self._out_root / path
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                except OSError as exc:
                    raise ValueError(f"A3: nelze načíst {file_path}: {exc}") from exc
                missing_exports = self._missing_exports_in_content(path, content, file_map_entry)
                if missing_exports:
                    if attempt == 0:
                        self._reset_generated_file(path)
                        attempt += 1
                        continue
                    raise ValueError(
                        f"A3: {path} nesplňuje exporty z A2X_FILE_MAP: {missing_exports}"
                    )
                written.append(file_path)
                break
        return written

    def _run_modify(
        self,
        user_spec: str,
        assets: RequestAssets,
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím sekvenci B1 → B2 → B3")
        self._load_request_templates()
        progress_callback("B1: plán změn", 0.1)
        self._ensure_not_cancelled(stop_check)
        dialog_content = self._prepare_dialog_content("B1", user_spec, ui_state)
        b1_payload = self._build_request_payload(
            "B1",
            {"<USER_TASK>": dialog_content},
            assets,
            ui_state,
            include_mirror=True,
            include_diagnostics=True,
            include_attachments=True,
            dialog_label="ÚKOL",
            dialog_content=dialog_content,
        )
        b1_response = self._send_request("B1", b1_payload, ui_state, assets)
        b1_data = self._parse_json_response(b1_response, "B1_PLAN", assets=assets)
        progress_callback("B2: identifikace souborů", 0.25)
        self._ensure_not_cancelled(stop_check)
        b2_previous = self._resolve_previous_response_id(ui_state, self._response_id)
        b2_payload = self._build_request_payload(
            "B2",
            {},
            assets,
            ui_state,
            previous_response_id=b2_previous,
            include_mirror=True,
            include_diagnostics=True,
            include_attachments=True,
        )
        b2_response = self._send_request("B2", b2_payload, ui_state, assets)
        b2_data = self._parse_json_response(b2_response, "B2_STRUCTURE", assets=assets)
        b2_response_id = self._response_id
        touched_files = b2_data.get("touched_files", [])
        self._validate_script_expectation_in_structure(touched_files, ui_state, "B2_STRUCTURE")
        if self._settings.dry_run_modify:
            summary = self._build_dry_run_summary(touched_files, ui_state)
            self._log(f"Dry-run pro MODIFY připraven ({len(summary.get('files') or [])} souborů).")
            if self._dry_run_confirmation and not self._dry_run_confirmation(summary):
                self._log("Dry-run přerušena uživatelem.")
                raise PipelineCancelled()

        progress_callback("B3: aktualizace obsahu souborů", 0.35)
        modified: List[Path] = []
        per_file_budget = 0.65 / max(len(touched_files), 1)
        for index, file_spec in enumerate(touched_files):
            if not isinstance(file_spec, dict):
                continue
            path = file_spec.get("path")
            if not isinstance(path, str) or not path:
                continue
            action = file_spec.get("action") or "modify"
            percent_base = 0.35 + index * per_file_budget
            chunk_index = None
            while True:
                self._ensure_not_cancelled(stop_check)
                suffix = f"CHUNK_INDEX={chunk_index}" if chunk_index is not None else ""
                replacements = {
                    "<PATH_FROM_B2>": path,
                    "<modify|add>": action,
                }
                b3_payload = self._build_request_payload(
                    "B3",
                    replacements,
                    assets,
                    ui_state,
                    previous_response_id=self._resolve_previous_response_id(ui_state, b2_response_id),
                    include_mirror=True,
                    include_diagnostics=True,
                    include_attachments=True,
                    input_suffix=suffix,
                )
                b3_response = self._send_request("B3", b3_payload, ui_state, assets)
                b3_data = self._parse_json_response(b3_response, "B3_FILE", assets=assets)
                if b3_data.get("path") != path:
                    raise ValueError(f"B3_FILE vrátil jiný path: {b3_data.get('path')} != {path}")
                chunk_meta = b3_data["chunking"]
                chunk_percent = percent_base + (chunk_meta["chunk_index"] + 1) * (
                    per_file_budget / max(chunk_meta["chunk_count"], 1)
                )
                progress_callback(
                    f"B3: {path} chunk {chunk_meta['chunk_index'] + 1}/{chunk_meta['chunk_count']}",
                    min(chunk_percent, 0.99),
                )
                self._write_chunk(path, {"chunking": chunk_meta, "content": b3_data["content"]})
                if not chunk_meta["has_more"]:
                    break
                chunk_index = chunk_meta["next_chunk_index"]
            modified.append(self._out_root / path)
        return modified

    def _build_dry_run_summary(
        self,
        files: Sequence[Dict[str, str]],
        ui_state: UiState,
    ) -> Dict[str, Any]:
        entries: List[Dict[str, Any]] = []
        risks: List[Dict[str, Any]] = []
        for spec in files:
            rel_path = spec.get("path", "") if isinstance(spec, dict) else ""
            target = self._out_root / rel_path
            exists = target.exists()
            entries.append(
                {
                    "path": rel_path,
                    "absolute_path": str(target),
                    "existing": exists,
                    "purpose": spec.get("purpose") or spec.get("intent"),
                }
            )
            if exists:
                risks.append(
                    {
                        "path": rel_path,
                        "reason": "Soubor existuje a bude přepsán.",
                    }
                )
        payload = {
            "project": ui_state.project_name or "Kája",
            "response_id": self._response_id,
            "mode": ui_state.mode,
            "phase": "B2",
            "files": entries,
            "risks": risks,
            "generated_at": datetime.utcnow().isoformat(),
        }
        manifest_path = log_manifest(self._run, payload, "dry_run_summary")
        self._dry_run_summary_log_path = manifest_path
        self._register_log_entry(
            manifest_path,
            "dry_run_summary",
            {"phase": "B2"},
        )
        summary = {**payload, "log": self._relative_log_path(manifest_path)}
        self._dry_run_summary = summary
        return summary

    def _run_qa(
        self,
        user_spec: str,
        assets: RequestAssets,
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím QA požadavek")
        progress_callback("QA: kontrola odpovědi", 0.5)
        self._ensure_not_cancelled(stop_check)
        dialog_content = self._prepare_dialog_content("QA", user_spec, ui_state)
        dialog_block = self._format_dialog_block("ÚKOL", dialog_content)
        base_instructions = "QA režim: očekává se pouze textová odpověď, žádný soubor. Nepoužívej IN/OUT."
        base_input = f"ÚKOL: {dialog_content}\nOčekává se pouze textová odpověď, žádný soubor."
        qa_instructions = f"{base_instructions}\n\n{dialog_block}"
        qa_input = f"{base_input}\n\nPRAVIDLA A KONTRAKT:\n{base_instructions}"
        qa_instructions, qa_input = self._maybe_trim_prompt_texts(
            "QA",
            qa_instructions,
            qa_input,
            ui_state,
        )
        instructions = self._build_instructions_text(
            qa_instructions,
            assets,
            ui_state,
            include_mirror=False,
            include_diagnostics=False,
        )
        input_text = self._build_input_text_with_assets(
            qa_input,
            assets,
            ui_state,
            include_mirror=False,
            include_diagnostics=False,
        )
        request_payload: Dict[str, Any] = {
            "model": ui_state.model or "gpt-4o",
            "temperature": 0.2,
            "instructions": instructions,
            "input": self._build_input_parts(
                input_text,
                assets,
                include_attachments=True,
                include_mirror=False,
                include_diagnostics=False,
            ),
        }
        if not self._model_capabilities.get("supports_temperature", False):
            request_payload.pop("temperature", None)
        self._ensure_payload_within_limits("QA", request_payload, ui_state)
        previous = self._resolve_previous_response_id(ui_state, "")
        if previous:
            request_payload["previous_response_id"] = previous
        response = self._send_request("QA", request_payload, ui_state, assets)
        _ = self._extract_response_text(response)
        progress_callback("QA: dokončeno", 1.0)
        return []

    def _run_send_as_c(
        self,
        user_spec: str,
        assets: RequestAssets,
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím C variantu (Batch)")
        self._load_request_templates()
        progress_callback("C: dávkový export", 0.3)
        self._ensure_not_cancelled(stop_check)
        dialog_content = self._prepare_dialog_content("C", user_spec, ui_state)
        dialog_block = self._format_dialog_block("ZADÁNÍ PROGRAMU", dialog_content)
        core_instructions = (
            "OUTPUT: VRAŤ POUZE validní JSON. ŽÁDNÝ markdown, žádné komentáře, žádný další text.\n"
            f"KONTRAKT C_FILES_ALL:\n{self._c_contract_block}"
        )
        instructions = f"{dialog_block}\n{core_instructions}"
        input_text = (
            "Vrať všechny soubory najednou podle kontraktu C_FILES_ALL. "
            "REDUNDANTNÍ KONTRAKT: vrať pouze JSON dle C_FILES_ALL.\n"
            f"{dialog_block}\n\nPRAVIDLA A KONTRAKT:\n{core_instructions}"
        )
        script_notice = self._format_script_expectation(ui_state)
        if script_notice:
            instructions += f"\n\n{script_notice}"
            input_text += f"\n{script_notice}"
        instructions, input_text = self._maybe_trim_prompt_texts(
            "C",
            instructions,
            input_text,
            ui_state,
        )
        request_payload: Dict[str, Any] = {
            "model": ui_state.model or "gpt-4o",
            "temperature": 0.2,
            "instructions": instructions,
            "input": self._build_input_parts(
                input_text,
                assets,
                include_attachments=False,
                include_mirror=False,
                include_diagnostics=False,
            ),
        }
        if not self._model_capabilities.get("supports_temperature", False):
            request_payload.pop("temperature", None)
        self._ensure_payload_within_limits("C", request_payload, ui_state)
        batch_dir = Path(self._run.log_dir) / "batch"
        create_dir(batch_dir)
        input_jsonl_path = batch_dir / f"batch_input_{self._run.run_id}.jsonl"
        request_line = {
            "custom_id": f"c-{self._run.run_id}",
            "method": "POST",
            "url": "/v1/responses",
            "body": request_payload,
        }
        input_jsonl_path.write_text(
            json.dumps(request_line, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self._register_log_entry(input_jsonl_path, "batch_input")
        if not self._client:
            raise RuntimeError("OpenAI client není dostupný pro batch.")
        input_file_id = self._upload_file(input_jsonl_path, purpose="batch", scope="batch_input")
        if not input_file_id:
            raise RuntimeError("Nelze nahrát batch JSONL.")
        batch = self._client.create_batch_job(input_file_id=input_file_id)
        batch_id = batch.get("id") or batch.get("batch_id")
        if not batch_id:
            raise RuntimeError("Batch ID nebyl vytvořen.")
        start = time.time()
        status = batch.get("status", "unknown")
        while status not in {"completed", "failed", "expired", "canceled"}:
            if time.time() - start > self._settings.batch_timeout_sec:
                raise RuntimeError("Batch timeout.")
            time.sleep(self._settings.batch_poll_interval_sec)
            batch = self._client.retrieve_batch_job(batch_id)
            status = batch.get("status", "unknown")
            progress_callback(f"C: batch {status}", 0.3)
        if status != "completed":
            raise RuntimeError(f"Batch nedokončen: {status}")
        output_file_id = batch.get("output_file_id")
        error_file_id = batch.get("error_file_id")
        output_jsonl_path = None
        error_jsonl_path = None
        if output_file_id:
            output_bytes = self._client.download_file(output_file_id)
            output_jsonl_path = batch_dir / f"batch_output_{self._run.run_id}.jsonl"
            output_jsonl_path.write_bytes(output_bytes)
            self._register_log_entry(output_jsonl_path, "batch_output")
        if error_file_id:
            error_bytes = self._client.download_file(error_file_id)
            error_jsonl_path = batch_dir / f"batch_error_{self._run.run_id}.jsonl"
            error_jsonl_path.write_bytes(error_bytes)
            self._register_log_entry(error_jsonl_path, "batch_error")
        if not output_jsonl_path:
            raise RuntimeError("Batch output chybí.")
        responses: List[Dict[str, Any]] = []
        for line in output_jsonl_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if "response" in item:
                responses.append(item["response"])
            elif "error" in item:
                self._log(f"Batch error: {item['error']}")
        if not responses:
            raise RuntimeError("Batch nevrátil žádnou response.")
        response = responses[0]
        current_response_id = (
            response.get("id")
            or response.get("response_id")
            or response.get("run_id")
            or self._response_id
        )
        if update_response_id:
            self._response_id = current_response_id
        response_log = log_response(
            self._run,
            response,
            stage="C",
            project_name=ui_state.project_name or "Kaja",
            response_id=current_response_id,
        )
        self._register_log_entry(
            response_log,
            "response",
            {"stage": "C", "response_id": current_response_id},
        )
        try:
            self._record_pricing_step("C", request_payload, response, ui_state)
        except Exception as exc:
            self._log(f"Pricing step selhal (C): {exc}")
        response_text = self._extract_response_text(response)
        try:
            parsed_payload = self._coerce_json_payload(response_text, "C_FILES_ALL")
            self._validate_contract(parsed_payload, "C_FILES_ALL", None)
            self._validate_c_script_expectation(parsed_payload, ui_state)
        except Exception as exc:
            invalid_dir = self._out_root / "_invalid"
            create_dir(invalid_dir)
            invalid_path = invalid_dir / f"c_invalid_{self._run.run_id}.json"
            invalid_path.write_text(response_text, encoding="utf-8")
            self._log(f"C validace selhala: {exc}")
            raise
        written: List[Path] = []
        for entry in parsed_payload.get("files", []):
            path = entry.get("path")
            content = entry.get("content") or ""
            self._write_chunk(
                path,
                {
                    "chunking": {
                        "max_lines": MAX_CHUNK_LINES,
                        "chunk_index": 0,
                        "chunk_count": 1,
                        "has_more": False,
                        "next_chunk_index": None,
                    },
                    "content": content,
                },
            )
            written.append(self._out_root / path)
        progress_callback("C: dokončeno", 1.0)
        return written

    def _determine_model_capabilities(self, model: str | None) -> Dict[str, Any]:
        capabilities = {
            "supports_vector_store": False,
            "supports_file_search": False,
            "supports_temperature": False,
            "resolved": False,
            "source": "defaults",
        }
        if not model or not self._client:
            return capabilities
        if hasattr(self._client, "get_model_capabilities"):
            try:
                resolved = self._client.get_model_capabilities(model, probe=True)
            except Exception as exc:
                self._log(f"Nelze načíst metadata modelu {model}: {exc}")
                return capabilities
            if isinstance(resolved, dict) and resolved:
                capabilities.update(resolved)
                return capabilities
        try:
            info = self._client.retrieve_model(model)
        except Exception as exc:
            self._log(f"Nelze načíst metadata modelu {model}: {exc}")
            return capabilities
        if not info:
            return capabilities
        caps = set()
        for key in ("capabilities", "tools", "supported_tools"):
            values = info.get(key)
            if isinstance(values, list):
                caps.update(str(item).lower() for item in values if isinstance(item, str))
        param_flags = set()
        for key in ("supported_parameters", "parameters"):
            values = info.get(key)
            if isinstance(values, list):
                param_flags.update(
                    str(item).lower() for item in values if isinstance(item, str)
                )
        supports_vector = bool({"vector_store", "tool_vector_store"} & caps)
        supports_file_search = bool({"file_search", "tool_file_search"} & caps)
        supports_temperature = False
        if param_flags:
            supports_temperature = "temperature" in param_flags
        resolved = bool(
            caps
            or param_flags
            or any(
                key in info
                for key in (
                    "capabilities",
                    "supported_tools",
                    "tools",
                    "tool_types",
                    "features",
                    "supported_parameters",
                    "parameters",
                )
            )
        )
        capabilities.update(
            {
                "supports_vector_store": supports_vector,
                "supports_file_search": supports_file_search,
                "supports_temperature": supports_temperature,
                "resolved": resolved,
                "source": info.get("id") or model,
            }
        )
        return capabilities

    def _describe_diagnostics(self, ui_state: UiState) -> List[str]:
        diagnostics = []
        if ui_state.diagnostics.windows_in:
            diagnostics.append("WINDOWS_IN")
        if ui_state.diagnostics.windows_out:
            diagnostics.append("WINDOWS_OUT")
        if ui_state.diagnostics.ssh_in:
            diagnostics.append("SSH_IN")
        if ui_state.diagnostics.ssh_out:
            diagnostics.append("SSH_OUT")
        return diagnostics

    def _collect_diagnostics_if_needed(self, ui_state: UiState, response_id: str) -> None:
        diagnostics_list = self._describe_diagnostics(ui_state)
        needs_windows = ui_state.diagnostics.windows_in or ui_state.diagnostics.windows_out
        needs_ssh = ui_state.diagnostics.ssh_in or ui_state.diagnostics.ssh_out
        if not (needs_windows or needs_ssh):
            return
        diag_context = self._start_timeline_entry("DIAGNOSTICS", {"scopes": diagnostics_list})
        diag_status = "completed"
        diag_errors: List[str] = []
        try:
            if needs_windows:
                try:
                    package = collect_windows_diagnostics(
                        base_out=self._out_root,
                        source_root=self._root_dir,
                        project=ui_state.project_name or "Kája",
                        response_id=response_id,
                        diagnostics=diagnostics_list,
                        settings=self._settings,
                    )
                    self._diagnostic_packages["windows"] = package
                    self._register_log_entry(
                        package.manifest_path,
                        "diagnostics_manifest",
                        {"scope": "windows"},
                    )
                    self._register_log_entry(
                        package.submission_path,
                        "diagnostics_submission",
                        {"scope": "windows"},
                    )
                    self._log(f"Windows diagnostika: {package.root}")
                except Exception as exc:
                    diag_status = "partial"
                    diag_errors.append(f"windows: {exc}")
                    self._log(f"Diagnostický sběr (Windows) selhal: {exc}")
            if needs_ssh:
                try:
                    package = collect_ssh_diagnostics(
                        base_out=self._out_root,
                        source_root=self._root_dir,
                        project=ui_state.project_name or "Kája",
                        response_id=response_id,
                        diagnostics=diagnostics_list,
                        settings=self._settings,
                        ssh_options=ui_state.ssh,
                    )
                    self._diagnostic_packages["ssh"] = package
                    self._register_log_entry(
                        package.manifest_path,
                        "diagnostics_manifest",
                        {"scope": "ssh"},
                    )
                    self._register_log_entry(
                        package.submission_path,
                        "diagnostics_submission",
                        {"scope": "ssh"},
                    )
                    self._log(f"SSH diagnostika: {package.root}")
                except Exception as exc:
                    diag_status = "partial"
                    diag_errors.append(f"ssh: {exc}")
                    self._log(f"Diagnostický sběr (SSH) selhal: {exc}")
        finally:
            diag_ids: Dict[str, Any] = {"scopes": diagnostics_list}
            if diag_errors:
                diag_ids["errors"] = diag_errors
            self._finish_timeline_entry(diag_context, diag_status, diag_ids)

    def _build_run_metadata(
        self,
        mode: str,
        user_spec: str,
        attachments: Sequence[FileRecord],
        vector_store_ids: Sequence[str],
        ui_state: UiState,
        response_id: str,
    ) -> Dict[str, Any]:
        metadata = {
            "project": ui_state.project_name or "Kája",
            "mode": mode,
            "model": ui_state.model or "gpt-4o",
            "response_id": response_id,
            "user_spec": user_spec.strip(),
            "attachments": [
                {
                    "file_id": record.file_id,
                    "filename": record.filename,
                    "purpose": record.purpose,
                    "size_bytes": record.size_bytes,
                }
                for record in attachments
            ],
            "vector_store_ids": list(vector_store_ids),
            "diagnostics": self._describe_diagnostics(ui_state),
            "captured_at": datetime.utcnow().isoformat(),
        }
        if self._diagnostic_packages:
            metadata["diagnostics_snapshot"] = {
                scope: {
                    "root": str(package.root),
                    "manifest": str(package.manifest_path),
                    "submission": str(package.submission_path),
                    "notes": package.notes,
                    "metadata": package.metadata,
                }
                for scope, package in self._diagnostic_packages.items()
            }
        if self._diagnostic_uploads:
            metadata["diagnostics_uploads"] = self._diagnostic_uploads
        metadata["pricing_catalog"] = self._price_catalog.summary()
        return metadata

    def _estimate_cost(
        self,
        mode: str,
        files: Sequence[Path],
        summary_steps: List[str],
        attachments: Sequence[FileRecord],
        vector_store_ids: Sequence[str],
        user_spec: str,
        ui_state: UiState,
    ) -> Tuple[float, Dict[str, Any]]:
        attachment_bytes = sum(record.size_bytes or 0 for record in attachments)
        input_tokens = max(1, len(user_spec) // 4 + attachment_bytes // 200)
        files_info: List[Dict[str, Any]] = []
        output_bytes = 0
        for path in files:
            size = self._path_size(path)
            output_bytes += size
            files_info.append({"path": str(path), "size": size})
        output_tokens = max(1, output_bytes // 4 + len(files) * 5)
        storage_gb = output_bytes / (1024 ** 3)
        storage_days = storage_gb
        vector_files = len(vector_store_ids)
        rates = self._price_catalog.get_rates(ui_state.model)
        input_cost = input_tokens * rates["input_token_rate"]
        output_cost = output_tokens * rates["output_token_rate"]
        vector_cost = vector_files * rates["vector_store_file_rate"]
        storage_cost = storage_days * rates["storage_gb_day"]
        file_api_cost = len(files) * rates["file_api_rate"]
        tool_cost = 0 * rates["tool_call_rate"]
        raw_total = input_cost + output_cost + vector_cost + storage_cost + file_api_cost + tool_cost
        discount = rates.get("batch_discount", 1.0) if mode == "C" else 1.0
        total = round(raw_total * discount, 6)
        usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "storage_bytes": output_bytes,
            "storage_gb": storage_gb,
            "storage_days": storage_days,
            "vector_store_files": vector_files,
            "attachments_bytes": attachment_bytes,
            "attachments": [record.filename for record in attachments],
            "files": files_info,
        }
        pricing_details: Dict[str, Any] = {
            "mode": mode,
            "model": ui_state.model or "gpt-4o",
            "summary_steps": summary_steps,
            "usage": usage,
            "vector_store_ids": list(vector_store_ids),
            "cost_breakdown": {
                "input_cost": input_cost,
                "output_cost": output_cost,
                "vector_store_cost": vector_cost,
                "storage_cost": storage_cost,
                "file_api_cost": file_api_cost,
                "tool_cost": tool_cost,
                "discount_factor": discount,
            },
            "total_cost": total,
            "pricing_summary": self._price_catalog.summary(),
            "status": self._price_catalog.status_text(),
            "verified": self._price_catalog.verified(),
            "computed_at": datetime.utcnow().isoformat(),
        }
        return total, pricing_details

    def _summarize_pricing_steps(self) -> Dict[str, Any]:
        steps = list(self._pricing_steps)
        estimated_input_tokens = sum(step["estimated"]["input_tokens"] for step in steps if step.get("estimated"))
        estimated_output_tokens = sum(step["estimated"]["output_tokens"] for step in steps if step.get("estimated"))
        estimated_total_cost = sum(step["estimated"]["total_cost"] for step in steps if step.get("estimated"))
        actual_steps = [step for step in steps if step.get("actual")]
        actual_summary: Dict[str, Any] | None = None
        if actual_steps:
            actual_input_tokens = sum(step["actual"]["input_tokens"] for step in actual_steps if step.get("actual"))
            actual_output_tokens = sum(step["actual"]["output_tokens"] for step in actual_steps if step.get("actual"))
            actual_total_cost = sum(step["actual"]["total_cost"] for step in actual_steps if step.get("actual"))
            actual_summary = {
                "input_tokens": actual_input_tokens,
                "output_tokens": actual_output_tokens,
                "total_cost": round(actual_total_cost, 6),
                "steps_with_usage": len(actual_steps),
            }
        coverage = round(len(actual_steps) / len(steps), 3) if steps else 0.0
        return {
            "steps": steps,
            "totals": {
                "estimated": {
                    "input_tokens": estimated_input_tokens,
                    "output_tokens": estimated_output_tokens,
                    "total_cost": round(estimated_total_cost, 6),
                },
                "actual": actual_summary,
                "coverage": coverage,
            },
            "notes": "Odhad pouziva char/4; realne ceny z response.usage.",
        }

    def _path_size(self, path: Path) -> int:
        try:
            return path.stat().st_size
        except OSError:
            return 0

    def _simulate_structure(self, user_spec: str, *, for_modify: bool = False) -> List[Dict[str, str]]:
        base = _slugify(user_spec.split()[0] if user_spec.strip() else "kaja")
        files = [
            {
                "path": f"{base}/core/runtime.py",
                "purpose": "Entry point runtime orchestrator",
                "language": "python",
                "generated_in_phase": "A3" if not for_modify else "B3",
            },
            {
                "path": f"{base}/core/pipeline.py",
                "purpose": "Plní úkoly A/B pipeline",
                "language": "python",
                "generated_in_phase": "A3" if not for_modify else "B3",
            },
            {
                "path": f"{base}/docs/README.md",
                "purpose": "Popis projektu a zvoleného režimu",
                "language": "markdown",
                "generated_in_phase": "A3" if not for_modify else "B3",
            },
        ]
        return files

    def _generate_file_content(
        self, file_spec: Dict[str, str], user_spec: str, ui_state: UiState, *, modify: bool = False
    ) -> str:
        header = f"# {file_spec['purpose']}\n# Vytvořeno pro {ui_state.project_name or 'Kája'}\n"
        if file_spec["path"].endswith(".py"):
            body = [
                "def run():",
                "    from datetime import datetime",
                f"    print('Projekt: {user_spec.strip() or 'Kája'}')",
                f"    print('Režim: {'MODIFY' if modify else 'GENERATE'}')",
                "    print('Toto je simulovaný obsah souboru vyrobený pipeline.')",
                "",
                "if __name__ == '__main__':",
                "    run()",
            ]
            return header + "\n".join(body)
        return header + "\n".join(
            [
                f"- speciﬁkace: {user_spec.strip() or 'kompletní program'}",
                f"- režim: {ui_state.mode}",
                "- Tento soubor vznikl jako součást simulované pipeline verze.",
            ]
        )

    def _write_chunk(self, rel_path: str, chunk: Dict[str, Any]) -> None:
        rel_path_obj = Path(rel_path)
        buffer_key = str(rel_path_obj)
        self._buffers.setdefault(buffer_key, []).append(chunk["content"])
        chunk_meta = chunk["chunking"]
        self._log(f"chunk {chunk_meta['chunk_index'] + 1}/{chunk_meta['chunk_count']} pro {rel_path}")
        if not chunk_meta["has_more"]:
            self._flush_file(rel_path_obj)

    def _flush_file(self, rel_path: Path) -> None:
        target = self._out_root / rel_path
        create_dir(target.parent)
        content = "".join(self._buffers.get(str(rel_path), []))
        bytes_content = content.encode("utf-8")
        prev_size: Optional[int] = None
        prev_hash: Optional[str] = None
        if target.exists():
            previous_bytes = target.read_bytes()
            prev_size = len(previous_bytes)
            prev_hash = hashlib.sha256(previous_bytes).hexdigest()
        target.write_bytes(bytes_content)
        new_size = len(bytes_content)
        new_hash = hashlib.sha256(bytes_content).hexdigest()
        snapshot_path = log_file_snapshot(self._run, rel_path, content)
        self._register_log_entry(
            snapshot_path,
            "file_snapshot",
            {"path": str(rel_path)},
        )
        action = "overwrite" if prev_size is not None else "create"
        operation_path = log_file_operation(
            self._run,
            {
                "action": action,
                "path": str(rel_path),
                "absolute_path": str(target),
                "source_path": str(target) if prev_size is not None else None,
                "target_path": str(target),
                "size_before": prev_size,
                "size_after": new_size,
                "hash_before": prev_hash,
                "hash_after": new_hash,
                "project": self._ui_state.project_name if self._ui_state else "",
                "response_id": self._response_id,
                "stage": self._ui_state.mode if self._ui_state else "",
            },
        )
        self._register_log_entry(
            operation_path,
            "file_operation",
            {"action": action},
        )
        self._log(f"Uloženo {target}")
        self._buffers.pop(str(rel_path), None)

    def _reset_generated_file(self, rel_path: str) -> None:
        rel_path_obj = Path(rel_path)
        self._buffers.pop(str(rel_path_obj), None)
        target = self._out_root / rel_path_obj
        if target.exists():
            target.unlink()

    def _missing_exports_in_content(
        self,
        rel_path: str,
        content: str,
        file_map_entry: Dict[str, Any] | None,
    ) -> List[str]:
        if not isinstance(file_map_entry, dict):
            return []
        exports = file_map_entry.get("exports", [])
        if not isinstance(exports, list):
            return []
        missing: List[str] = []
        for export in exports:
            if not isinstance(export, dict):
                continue
            signature = export.get("signature")
            name = export.get("name")
            expected = None
            if isinstance(signature, str) and signature.strip():
                expected = signature.strip()
            elif isinstance(name, str) and name.strip():
                expected = name.strip()
            if not expected:
                continue
            if expected not in content:
                missing.append(expected)
        if missing:
            self._log(f"A3 validace {rel_path}: chybí exporty {missing}.")
        return missing

    def _ensure_not_cancelled(self, stop_check: StopCheck) -> None:
        self._watchdog_check()
        if stop_check():
            self._log("Pipeline zrušena uživatelem")
            raise PipelineCancelled()

    def _watchdog_check(self) -> None:
        elapsed = time.time() - self._last_progress_update
        if elapsed > self._watchdog_interval:
            if time.time() - self._last_watchdog_log > self._watchdog_interval:
                self._log("Watchdog: krok trvá déle než očekávaný interval.")
                self._last_watchdog_log = time.time()
            self._last_progress_update = time.time()

    def _maybe_create_versing_snapshot(self, ui_state: UiState) -> None:
        if not ui_state.versing_enabled:
            return
        target_path = ui_state.in_dir or ui_state.out_dir
        if not target_path:
            self._log("VERSING: IN/OUT adresář není nastaven.")
            return
        root_dir = Path(target_path)
        if not root_dir.is_dir():
            self._log(f"VERSING: cílový adresář neexistuje ({root_dir}).")
            return
        timestamp = datetime.utcnow().strftime("%d%m%Y%H%M")
        snapshot_name = f"{root_dir.name}{timestamp}"
        temp_snapshot = root_dir.parent / snapshot_name
        if temp_snapshot.exists():
            shutil.rmtree(temp_snapshot)

        def _ignore(dirpath: str, names: Sequence[str]) -> List[str]:
            current = Path(dirpath)
            filtered: List[str] = []
            for name in names:
                candidate = current / name
                if (
                    name.lower() in {"venv", ".venv", "log"}
                    or is_versing_dir(candidate, root_dir.name)
                ):
                    filtered.append(name)
            return filtered

        try:
            shutil.copytree(root_dir, temp_snapshot, ignore=_ignore)
            final_snapshot = root_dir / snapshot_name
            if final_snapshot.exists():
                shutil.rmtree(final_snapshot)
            temp_snapshot.rename(final_snapshot)
            self._log(f"VERSING snapshot vytvořen: {final_snapshot}")
            payload = {
                "action": "versing_snapshot",
                "path": str(final_snapshot),
                "project": ui_state.project_name or "Kája",
                "response_id": self._response_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
            operation_path = log_file_operation(self._run, payload)
            self._register_log_entry(
                operation_path,
                "file_operation",
                {"action": "versing_snapshot"},
            )
            self._versing_snapshot_path = final_snapshot
        except Exception as exc:
            self._log(f"VERSING selhal: {exc}")

    def _run_post_hooks(self, ui_state: UiState) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        context = {
            "project": ui_state.project_name or "Kája",
            "response_id": self._response_id,
            "stage": ui_state.mode,
        }
        for command in self._settings.local_post_hooks:
            text = command.strip()
            if not text:
                continue
            record = self._execute_local_hook(text)
            record.update(context)
            record = self._log_hook_result(record)
            self._log(f"Post-run hook (local) '{text}' -> {record['status']}")
            results.append(record)
        for command in self._settings.ssh_post_hooks:
            text = command.strip()
            if not text:
                continue
            record = self._execute_ssh_hook(text, ui_state.ssh)
            record.update(context)
            record = self._log_hook_result(record)
            self._log(f"Post-run hook (ssh) '{text}' -> {record['status']}")
            results.append(record)
        return results

    def _execute_local_hook(self, command: str) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        try:
            completed = subprocess.run(command, shell=True, capture_output=True, text=True)
            status = "success" if completed.returncode == 0 else "failed"
            return {
                "kind": "local",
                "command": command,
                "status": status,
                "exit_code": completed.returncode,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
                "timestamp": timestamp,
            }
        except Exception as exc:
            return {
                "kind": "local",
                "command": command,
                "status": "error",
                "exit_code": None,
                "stdout": "",
                "stderr": str(exc),
                "timestamp": timestamp,
                "reason": str(exc),
            }

    def _execute_ssh_hook(self, command: str, ssh: SshOptions) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        if not ssh.host:
            return {
                "kind": "ssh",
                "command": command,
                "status": "skipped",
                "exit_code": None,
                "stdout": "",
                "stderr": "",
                "timestamp": timestamp,
                "reason": "SSH host není nakonfigurován.",
            }
        ssh_cmd: List[str] = ["ssh", "-o", "BatchMode=yes", "-p", str(ssh.port or 22)]
        if ssh.key_path:
            ssh_cmd.extend(["-i", ssh.key_path])
        ssh_target = f"{ssh.user or 'root'}@{ssh.host}"
        ssh_cmd.extend([ssh_target, command])
        if ssh.password:
            sshpass = shutil.which("sshpass")
            if not sshpass:
                return {
                    "kind": "ssh",
                    "command": command,
                    "status": "skipped",
                    "exit_code": None,
                    "stdout": "",
                    "stderr": "",
                    "timestamp": timestamp,
                    "reason": "sshpass není dostupný pro password autentizaci.",
                }
            ssh_cmd = [sshpass, "-p", ssh.password] + ssh_cmd
        try:
            completed = subprocess.run(ssh_cmd, capture_output=True, text=True)
            status = "success" if completed.returncode == 0 else "failed"
            return {
                "kind": "ssh",
                "command": command,
                "executed": " ".join(ssh_cmd),
                "status": status,
                "exit_code": completed.returncode,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
                "timestamp": timestamp,
            }
        except Exception as exc:
            return {
                "kind": "ssh",
                "command": command,
                "status": "error",
                "exit_code": None,
                "stdout": "",
                "stderr": str(exc),
                "timestamp": timestamp,
                "reason": str(exc),
            }

    def _log_hook_result(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        log_path = log_hook_execution(self._run, payload)
        self._register_log_entry(
            log_path,
            "hook",
            {
                "kind": payload.get("kind"),
                "command": payload.get("command"),
                "stage": payload.get("stage"),
            },
        )
        payload["log"] = self._relative_log_path(log_path)
        return payload

    @staticmethod
    def _generate_response_id(mode: str) -> str:
        suffix = uuid.uuid4().hex[:6]
        return f"{mode}_{suffix}"

    def _log(self, message: str) -> None:
        self._logger(message)

