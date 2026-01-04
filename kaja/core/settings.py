from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Settings:
    db_path: str
    log_max_runs: int = 100
    log_max_size_mb: int = 500
    retry_max_attempts: int = 5
    retry_max_delay_sec: int = 30
    pricing_url: str = ""
    pricing_cache_ttl_min: int = 1440
    pricing_auto_refresh: bool = False
    mask_secrets: bool = False
    encrypt_logs: bool = False
    batch_poll_interval_sec: int = 30
    batch_timeout_sec: int = 3600
    default_model: str = ""
    default_temperature: float = 0.2
    admin_username: str = ""
    admin_password: str = ""
    diagnostics_acknowledged: bool = False
    ssh_host: str = ""
    ssh_port: int = 22
    ssh_user: str = "root"
    ssh_key_path: str = ""
    ssh_password: str = ""
    allow_extensions_in: List[str] = field(default_factory=list)
    deny_extensions_in: List[str] = field(default_factory=list)
    allow_paths_in: List[str] = field(default_factory=list)
    deny_paths_in: List[str] = field(default_factory=list)
    allow_extensions_diag: List[str] = field(default_factory=list)
    deny_extensions_diag: List[str] = field(default_factory=list)
    allow_paths_diag: List[str] = field(default_factory=list)
    deny_paths_diag: List[str] = field(default_factory=list)
    secret_scan_enabled: bool = True
    allow_sensitive_uploads: bool = False
    log_encryption_key: str = ""
    panic_wipe_include_logs: bool = False
    dry_run_modify: bool = False
    local_post_hooks: List[str] = field(default_factory=list)
    ssh_post_hooks: List[str] = field(default_factory=list)


class SettingsStore:
    def __init__(self, root_dir: Path) -> None:
        self._path = root_dir / "settings.json"

    @property
    def path(self) -> Path:
        return self._path

    def _default_settings(self) -> Settings:
        return Settings(db_path=str(self._path.parent / "kaja.db"))

    def _coerce_settings(self, raw: Dict[str, Any]) -> Settings:
        payload: Dict[str, Any] = {}
        for field in fields(Settings):
            if field.name in raw:
                payload[field.name] = raw[field.name]
        if not payload.get("db_path"):
            payload["db_path"] = str(self._path.parent / "kaja.db")
        return Settings(**payload)

    def load(self) -> Settings:
        if not self._path.exists():
            settings = self._default_settings()
            self.save(settings)
            return settings
        raw: Dict[str, Any] = {}
        try:
            with self._path.open("r", encoding="utf-8") as handle:
                raw = json.load(handle)
            if not isinstance(raw, dict):
                raise ValueError("settings.json is not a JSON object")
            settings = self._coerce_settings(raw)
        except Exception:
            settings = self._default_settings()
        if settings.__dict__ != raw:
            self.save(settings)
        return settings

    def save(self, settings: Settings) -> None:
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(settings.__dict__, handle, indent=2, ensure_ascii=False)
