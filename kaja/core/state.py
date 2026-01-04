from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DiagnosticsOptions:
    windows_in: bool = False
    windows_out: bool = False
    ssh_in: bool = False
    ssh_out: bool = False


@dataclass
class SshOptions:
    host: str = ""
    user: str = "root"
    key_path: str = ""
    password: str = ""
    port: int = 22


@dataclass
class UiState:
    project_name: str = ""
    prompt_text: str = ""
    in_dir: str = ""
    out_dir: str = ""
    versing_enabled: bool = False
    mode: str = "GENERATE"
    response_id: str = ""
    model: str = ""
    send_as_c: bool = False
    diagnostics: DiagnosticsOptions = field(default_factory=DiagnosticsOptions)
    ssh: SshOptions = field(default_factory=SshOptions)
    attached_file_ids: List[str] = field(default_factory=list)


@dataclass
class FileRecord:
    file_id: str
    filename: str
    purpose: str
    size_bytes: int


@dataclass
class VectorStoreRecord:
    store_id: str
    name: str
    expires_at: Optional[str]


@dataclass
class RunArtifacts:
    run_id: str
    log_dir: str
