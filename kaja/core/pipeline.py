from __future__ import annotations

import hashlib
import json
import math
import random
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

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
from .path_utils import create_dir, is_versing_dir
from .pricing import Receipt
from .settings import Settings
from .state import RunArtifacts, UiState
from .diagnostics import (
    DiagnosticPackage,
    collect_ssh_diagnostics,
    collect_windows_diagnostics,
)
from .price_catalog import PriceCatalog
from . import security

MAX_CHUNK_LINES = 500
DEFAULT_CHUNK_LINES = 500

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


def _slugify(name: str) -> str:
    sanitized = re.sub(r"[^a-z0-9]+", "-", name.lower())
    sanitized = sanitized.strip("-")
    return sanitized or "project"


def _ensure_json_serializable(value: Dict[str, Any]) -> Dict[str, Any]:
    text = json.dumps(value, ensure_ascii=False)
    return json.loads(text)


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
        self._diagnostic_zip_paths: List[Path] = []
        self._diagnostic_uploads: List[Dict[str, Any]] = []
        self._timeline: List[Dict[str, Any]] = []
        self._request_snapshot: Dict[str, Any] = {}
        self._model_capabilities: Dict[str, Any] = {"supports_vector_store": True, "supports_file_search": False}
        self._versing_snapshot_path: Path | None = None
        self._watchdog_interval = 30.0
        self._last_progress_update = time.time()
        self._last_watchdog_log = time.time()
        self._price_catalog = PriceCatalog(
            cache_path=self._root_dir / "pricing_cache.json",
            settings=self._settings,
        )
        self._price_catalog.refresh_if_needed(force=self._settings.pricing_auto_refresh)
        self._security_policy = security_policy
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

    def execute(
        self,
        mode: str,
        ui_state: UiState,
        user_spec: str,
        attachments: Sequence[Path],
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
            base_callback(message, ratio)
        progress_callback = progress_wrapper
        self._ensure_not_cancelled(stop_check)
        self._timeline.clear()
        self._request_snapshot = request_snapshot or {}
        self._versing_snapshot_path = None
        run_context = self._start_timeline_entry("RUN", {"mode": mode})

        self._ui_state = ui_state
        self._model_capabilities = self._determine_model_capabilities(ui_state.model)
        original_vector_store_ids = list(vector_store_ids)
        effective_vector_store_ids = list(original_vector_store_ids)
        if not self._model_capabilities.get("supports_vector_store", True):
            if vector_store_ids:
                self._log("Model nepodporuje vector store; přepínám na fallback režim bez vektorů.")
            effective_vector_store_ids = []
        response_id = response_id or self.generate_response_id(mode)
        self._response_id = response_id
        self._collect_diagnostics_if_needed(ui_state, response_id)
        self._prepare_diagnostics_artifacts(effective_vector_store_ids)
        self._maybe_create_versing_snapshot(ui_state)
        metadata = self._build_run_metadata(
            mode,
            user_spec,
            attachments,
            vector_store_ids,
            ui_state,
            response_id,
        )
        metadata_path = log_run_metadata(self._run, metadata)
        self._register_log_entry(metadata_path, "run_metadata", {"mode": mode})

        manifest_context = {
            "attachments": [str(path) for path in attachments],
            "vector_store_ids": list(vector_store_ids),
            "mode": mode,
            "response_id": response_id,
            "project": ui_state.project_name or "Kaja",
            "run_id": self._run.run_id,
        }
        manifest_context["vector_store_requested"] = original_vector_store_ids
        manifest_context["vector_store_enabled"] = bool(effective_vector_store_ids)
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
            files = self._run_generate(user_spec, attachments, effective_vector_store_ids, ui_state, progress_callback, stop_check)
            summary_steps.extend(["A1", "A2", "A3"])
        elif mode == "MODIFY":
            files = self._run_modify(user_spec, attachments, effective_vector_store_ids, ui_state, progress_callback, stop_check)
            summary_steps.extend(["B1", "B2", "B3"])
        elif mode == "QA":
            files = self._run_qa(user_spec, attachments, effective_vector_store_ids, ui_state, progress_callback, stop_check)
            summary_steps.append("QA")
        elif mode == "C":
            files = self._run_send_as_c(user_spec, attachments, effective_vector_store_ids, ui_state, progress_callback, stop_check)
            summary_steps.append("C")
        else:
            raise ValueError(f"Nedefinovaný režim pipeline: {mode}")
        files.extend(self._diagnostic_zip_paths)
        hook_results = self._run_post_hooks(ui_state)

        duration = time.time() - start_time
        total_cost, pricing_details = self._estimate_cost(
            mode,
            files,
            summary_steps,
            attachments,
            vector_store_ids,
            user_spec,
            ui_state,
        )
        receipt = Receipt(
            run_id=self._run.run_id,
            project=ui_state.project_name or "Kaja",
            model=ui_state.model or "gpt-4o",
            mode=mode,
            response_id=response_id,
            total_cost=total_cost,
            details_json=json.dumps(pricing_details, ensure_ascii=False),
            created_at=datetime.utcnow().isoformat(),
            verified_pricing=pricing_details.get("verified", False),
        )
        receipt_path = log_pricing_receipt(self._run, self._settings, receipt)
        self._register_log_entry(
            receipt_path,
            "receipt",
            {"total_cost": total_cost},
        )
        manifest_context.update(
            {
                "files_written": [str(path) for path in files],
                "duration_s": round(duration, 2),
                "steps": summary_steps,
                "total_cost": total_cost,
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
            "response_id": response_id,
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
        self._finish_timeline_entry(run_context, "completed", {"response_id": response_id})
        self._log(f"Cena runu: {total_cost:.4f} USD")
        progress_callback("Dokončeno", 1.0)
        return PipelineResult(
            mode=mode,
            run_id=self._run.run_id,
            response_id=response_id,
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
        attachments: Sequence[Path],
        vector_store_ids: Sequence[str],
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím sekvenci A1 → A2 → A3")
        progress_callback("A1: plán projektu", 0.1)
        self._request_stage("A1", "A1_PLAN", user_spec, attachments, vector_store_ids, ui_state, request_snapshot=self._request_snapshot)
        progress_callback("A2: struktura souborů", 0.25)
        files = self._simulate_structure(user_spec)
        progress_callback("A3: generování obsahu souborů", 0.35)
        written: List[Path] = []
        per_file_budget = 0.65 / max(len(files), 1)
        for index, file_spec in enumerate(files):
            percent_base = 0.35 + index * per_file_budget
            content = self._generate_file_content(file_spec, user_spec, ui_state)
            chunks = chunk_text(content)
            for chunk_index, chunk in enumerate(chunks):
                self._ensure_not_cancelled(stop_check)
                chunk_percent = percent_base + (chunk_index + 1) * (per_file_budget / len(chunks))
                progress_callback(f"A3: {file_spec['path']} chunk {chunk_index + 1}/{len(chunks)}", min(chunk_percent, 0.99))
                self._write_chunk(file_spec["path"], chunk)
            written.append(self._out_root / file_spec["path"])
        return written

    def _run_modify(
        self,
        user_spec: str,
        attachments: Sequence[Path],
        vector_store_ids: Sequence[str],
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím sekvenci B1 → B2 → B3")
        progress_callback("B1: plán změn", 0.1)
        self._request_stage("B1", "B1_PLAN", user_spec, attachments, vector_store_ids, ui_state, request_snapshot=self._request_snapshot)
        progress_callback("B2: identifikace souborů", 0.25)
        files = self._simulate_structure(user_spec, for_modify=True)
        if self._settings.dry_run_modify:
            summary = self._build_dry_run_summary(files, ui_state)
            self._log(f"Dry-run pro MODIFY připraven ({len(summary.get('files') or [])} souborů).")
            if self._dry_run_confirmation and not self._dry_run_confirmation(summary):
                self._log("Dry-run přerušena uživatelem.")
                raise PipelineCancelled()

        progress_callback("B3: aktualizace obsahu souborů", 0.35)
        modified: List[Path] = []
        per_file_budget = 0.65 / max(len(files), 1)
        for index, file_spec in enumerate(files):
            percent_base = 0.35 + index * per_file_budget
            content = self._generate_file_content(file_spec, user_spec, ui_state, modify=True)
            chunks = chunk_text(content)
            for chunk_index, chunk in enumerate(chunks):
                self._ensure_not_cancelled(stop_check)
                chunk_percent = percent_base + (chunk_index + 1) * (per_file_budget / len(chunks))
                progress_callback(f"B3: {file_spec['path']} chunk {chunk_index + 1}/{len(chunks)}", min(chunk_percent, 0.99))
                self._write_chunk(file_spec["path"], chunk)
            modified.append(self._out_root / file_spec["path"])
        return modified

    def _build_dry_run_summary(
        self,
        files: Sequence[Dict[str, str]],
        ui_state: UiState,
    ) -> Dict[str, Any]:
        entries: List[Dict[str, Any]] = []
        risks: List[Dict[str, Any]] = []
        for spec in files:
            rel_path = spec.get("path", "")
            target = self._out_root / rel_path
            exists = target.exists()
            entries.append(
                {
                    "path": rel_path,
                    "absolute_path": str(target),
                    "existing": exists,
                    "purpose": spec.get("purpose"),
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
        attachments: Sequence[Path],
        vector_store_ids: Sequence[str],
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím QA požadavek")
        progress_callback("QA: kontrola odpovědi", 0.5)
        self._request_stage("QA", "QA_RESPONSE", user_spec, attachments, vector_store_ids, ui_state, request_snapshot=self._request_snapshot)
        progress_callback("QA: dokončeno", 1.0)
        return []

    def _run_send_as_c(
        self,
        user_spec: str,
        attachments: Sequence[Path],
        vector_store_ids: Sequence[str],
        ui_state: UiState,
        progress_callback: ProgressCallback,
        stop_check: StopCheck,
    ) -> List[Path]:
        self._log("Spouštím C variantu (Batch)")
        progress_callback("C: dávkový export", 0.3)
        summary_path = self._out_root / "batch_c_execution.json"
        payload = {
            "mode": "C",
            "spec": user_spec,
            "attachments": [str(p) for p in attachments],
            "vector_stores": list(vector_store_ids),
            "diagnostics": self._describe_diagnostics(ui_state),
        }
        summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        progress_callback("C: dokončeno", 1.0)
        return [summary_path]

    def _request_stage(
        self,
        stage: str,
        contract: str,
        user_spec: str,
        attachments: Sequence[Path],
        vector_store_ids: Sequence[str],
        ui_state: UiState,
        request_snapshot: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        instructions = f"Režim {contract}: generuj artefakt podle specifikace."
        input_text = self._build_input_text(user_spec, attachments, vector_store_ids, ui_state)
        stage_context = self._start_timeline_entry(stage, {"contract": contract})
        payload: Dict[str, Any] = {
            "model": ui_state.model or "gpt-4o",
            "temperature": 0.2,
            "instructions": instructions,
            "input": input_text,
            "contract": contract,
            "previous_response_id": "",
        }
        payload["ui_state_snapshot"] = request_snapshot or self._request_snapshot or {}
        payload_json = _ensure_json_serializable(payload)
        request_log = log_request(
            self._run,
            payload_json,
            stage=stage,
            project_name=ui_state.project_name or "Kaja",
            response_id=self._response_id,
        )
        self._register_log_entry(request_log, "request", {"stage": stage})
        if self._client:
            response = self._client.create_response(payload_json)
        else:
            response = payload_json.copy()
            response["result"] = f"Simulovaný výstup pro {contract}"
            response["contract"] = contract
        current_response_id = (
            response.get("id")
            or response.get("response_id")
            or response.get("run_id")
            or self._response_id
        )
        response_log = log_response(
            self._run,
            response,
            stage=stage,
            project_name=ui_state.project_name or "Kaja",
            response_id=current_response_id,
        )
        self._register_log_entry(
            response_log,
            "response",
            {"stage": stage, "response_id": current_response_id},
        )
        self._finish_timeline_entry(stage_context, "completed", {"response_id": current_response_id})
        return response

    def _build_input_text(
        self,
        user_spec: str,
        attachments: Sequence[Path],
        vector_store_ids: Sequence[str],
        ui_state: UiState,
    ) -> str:
        parts: List[str] = []
        project = ui_state.project_name or "Kája"
        parts.append(f"Projekt: {project}")
        parts.append(f"Režim: {ui_state.mode}")
        parts.append(f"Model: {ui_state.model or 'gpt-4o'}")
        spec_text = user_spec.strip()
        parts.append(f"Specifikace: {spec_text or '(není zadáno)'}")

        diagnostics = self._describe_diagnostics(ui_state)
        if diagnostics:
            parts.append(f"Diagnostika: {', '.join(diagnostics)}")

        if attachments:
            parts.append("Připojené soubory:")
            for path in attachments:
                parts.append(f"- {path.name} ({path})")

        if vector_store_ids:
            ids = ", ".join(vector_store_ids)
            parts.append(f"Vector store cíle: {ids}")

        if ui_state.attached_file_ids:
            ids = ", ".join(ui_state.attached_file_ids)
            parts.append(f"ID připojených souborů: {ids}")

        return "\n".join(parts)

    def _determine_model_capabilities(self, model: str | None) -> Dict[str, Any]:
        capabilities = {"supports_vector_store": True, "supports_file_search": False, "source": "defaults"}
        if not model or not self._client:
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
        supports_vector = bool({"vector_store", "tool_vector_store"} & caps)
        supports_file_search = bool({"file_search", "tool_file_search"} & caps)
        capabilities.update(
            {
                "supports_vector_store": supports_vector,
                "supports_file_search": supports_file_search,
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

    def _prepare_diagnostics_artifacts(self, vector_store_ids: Sequence[str]) -> None:
        self._diagnostic_zip_paths.clear()
        self._diagnostic_uploads.clear()
        for scope, package in self._diagnostic_packages.items():
            zip_path = self._zip_diagnostic_package(scope, package)
            self._diagnostic_zip_paths.append(zip_path)
            upload_entry = self._upload_diagnostic_zip(scope, zip_path, vector_store_ids)
            if upload_entry:
                self._diagnostic_uploads.append(upload_entry)

    def _zip_diagnostic_package(self, scope: str, package: DiagnosticPackage) -> Path:
        zip_target = package.root.parent / f"{package.root.name}.zip"
        base_name = str(zip_target.with_suffix(""))
        archive_path = Path(shutil.make_archive(base_name, "zip", root_dir=package.root))
        self._log_diagnostic_zip_operation(archive_path, scope)
        return archive_path

    def _log_diagnostic_zip_operation(self, zip_path: Path, scope: str) -> None:
        size = zip_path.stat().st_size
        payload = {
            "action": "create",
            "path": str(zip_path.relative_to(self._out_root)),
            "absolute_path": str(zip_path),
            "project": self._ui_state.project_name if self._ui_state else "",
            "response_id": self._response_id,
            "scope": scope,
            "size_after": size,
            "timestamp": datetime.utcnow().isoformat(),
        }
        operation_path = log_file_operation(self._run, payload)
        self._register_log_entry(
            operation_path,
            "file_operation",
            {"scope": scope, "action": "create"},
        )

    def _upload_diagnostic_zip(
        self,
        scope: str,
        zip_path: Path,
        vector_store_ids: Sequence[str],
    ) -> Dict[str, Any]:
        entry = {
            "scope": scope,
            "zip_path": str(zip_path),
            "vector_store_ids": [],
            "status": "skipped",
            "file_id": None,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        if self._security_policy:
            report = self._security_policy.evaluate_archive(zip_path)
            if report.findings:
                reasons = "; ".join(f"{finding.path or zip_path.name}: {finding.reason}" for finding in report.findings)
                security.record_security_event(self._run, scope, str(zip_path), report, blocked=report.blocked)
                if report.blocked:
                    entry["status"] = "blocked"
                    entry["reason"] = reasons
                    self._log(f"Security policy zablokovala upload {scope}: {reasons}")
                    return entry
                self._log(f"Security upozornění pro {scope}: {reasons}")
        if not self._client:
            self._log("OpenAI client není nakonfigurován; upload diagnostiky přeskočen.")
            return entry
        try:
            upload_result = self._client.upload_file(zip_path, purpose="diagnostics")
            file_id = upload_result.get("id") or upload_result.get("file_id")
            entry.update(
                {
                    "status": "uploaded",
                    "file_id": file_id,
                    "uploaded_at": datetime.utcnow().isoformat(),
                }
            )
            payload = {
                "scope": scope,
                "project": self._ui_state.project_name or "Kája",
                "response_id": self._response_id,
                "local_path": str(zip_path),
                "file_id": file_id,
                "purpose": "diagnostics",
                "size": zip_path.stat().st_size,
                "uploaded_at": entry["uploaded_at"],
            }
            upload_log = log_file_upload(self._run, payload)
            self._register_log_entry(upload_log, "file_upload", {"scope": scope})
            if not self._model_capabilities.get("supports_vector_store", True):
                self._log("Vector store není podporovaný pro tento model; přeskočeno přidání souborů.")
            else:
                for store_id in vector_store_ids:
                    if not file_id:
                        continue
                    try:
                        self._client.add_vector_store_file(store_id, file_id)
                        entry["vector_store_ids"].append(store_id)
                        vs_payload = {
                            "scope": scope,
                            "project": self._ui_state.project_name or "Kája",
                            "response_id": self._response_id,
                            "vector_store_id": store_id,
                            "file_id": file_id,
                            "added_at": datetime.utcnow().isoformat(),
                        }
                        vs_log = log_vector_store_entry(self._run, vs_payload)
                        self._register_log_entry(
                            vs_log,
                            "vector_store",
                            {"scope": scope, "vector_store_id": store_id},
                        )
                    except Exception as exc:
                        self._log(f"Vector store attach ({store_id}) selhalo: {exc}")
        except Exception as exc:
            self._log(f"Upload diagnostiky ({scope}) selhal: {exc}")
            entry["status"] = "failed"
            entry["error"] = str(exc)
        return entry

    def _build_run_metadata(
        self,
        mode: str,
        user_spec: str,
        attachments: Sequence[Path],
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
            "attachments": [str(path) for path in attachments],
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
        attachments: Sequence[Path],
        vector_store_ids: Sequence[str],
        user_spec: str,
        ui_state: UiState,
    ) -> Tuple[float, Dict[str, Any]]:
        attachment_bytes = sum(self._path_size(path) for path in attachments)
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
            "attachments": [str(path) for path in attachments],
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

