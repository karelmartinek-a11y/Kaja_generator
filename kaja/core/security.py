from __future__ import annotations

import base64
import fnmatch
import json
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence

from .settings import Settings

from .log_manager import log_file_operation
from .state import RunArtifacts

SENSITIVE_KEYWORDS = [
    "secret",
    "token",
    "password",
    "apikey",
    "api_key",
    "key",
    "credential",
    "private key",
    "ssh",
]

SENSITIVE_BASE64_HEADERS = [
    "-----BEGIN PRIVATE KEY",
    "-----BEGIN RSA PRIVATE KEY",
    "-----BEGIN EC PRIVATE KEY",
]

DEFAULT_SECRET_TIMEOUT = 4096


@dataclass
class SecurityFinding:
    path: str
    reason: str
    severity: str = "warning"


@dataclass
class SecurityReport:
    findings: List[SecurityFinding] = field(default_factory=list)
    allow_sensitive_uploads: bool = False

    @property
    def blocked(self) -> bool:
        return bool(self.findings) and not self.allow_sensitive_uploads


@dataclass
class SecurityPolicy:
    context: str
    allow_extensions: List[str]
    deny_extensions: List[str]
    allow_paths: List[str]
    deny_paths: List[str]
    secret_scan_enabled: bool
    allow_sensitive_uploads: bool

    def __post_init__(self) -> None:
        self._allow_ext_patterns = self._compile_extension_patterns(self.allow_extensions)
        self._deny_ext_patterns = self._compile_extension_patterns(self.deny_extensions)
        self._allow_path_patterns = self._compile_path_patterns(self.allow_paths)
        self._deny_path_patterns = self._compile_path_patterns(self.deny_paths)

    @staticmethod
    def _compile_extension_patterns(items: Iterable[str]) -> List[str]:
        patterns: List[str] = []
        for item in items:
            normalized = item.strip().lower()
            if not normalized:
                continue
            if any(ch in normalized for ch in "*?"):
                patterns.append(normalized)
                continue
            ext = normalized.lstrip(".")
            if not ext:
                continue
            patterns.append(f"*.{ext}")
        return patterns

    @staticmethod
    def _compile_path_patterns(items: Iterable[str]) -> List[str]:
        patterns: List[str] = []
        for item in items:
            normalized = item.strip().lower()
            if not normalized:
                continue
            patterns.append(normalized.replace("\\", "/"))
        return patterns

    @staticmethod
    def _match_patterns(value: str, patterns: Sequence[str]) -> bool:
        if not patterns:
            return False
        target = value.lower().replace("\\", "/")
        for pattern in patterns:
            if fnmatch.fnmatch(target, pattern):
                return True
        return False

    def _evaluate_entry(self, path_str: str, ext: str) -> List[SecurityFinding]:
        findings: List[SecurityFinding] = []
        if self._match_patterns(path_str, self._deny_path_patterns):
            findings.append(SecurityFinding(path=path_str, reason="Path prohibited by deny list"))
        elif self._allow_path_patterns and not self._match_patterns(path_str, self._allow_path_patterns):
            findings.append(SecurityFinding(path=path_str, reason="Path not listed in allow list"))
        if ext:
            if self._match_patterns(ext, self._deny_ext_patterns):
                findings.append(SecurityFinding(path=path_str, reason="Extension prohibited by deny list"))
            elif self._allow_ext_patterns and not self._match_patterns(ext, self._allow_ext_patterns):
                findings.append(SecurityFinding(path=path_str, reason="Extension not listed in allow list"))
        return findings

    def _scan_text(self, text: str) -> List[str]:
        matches: List[str] = []
        lowered = text.lower()
        for keyword in SENSITIVE_KEYWORDS:
            if keyword in lowered:
                matches.append(keyword)
        for header in SENSITIVE_BASE64_HEADERS:
            if header.lower() in lowered:
                matches.append(header)
        return matches

    def _inspect_content(self, handle) -> List[SecurityFinding]:
        if not self.secret_scan_enabled:
            return []
        sample = handle.read(DEFAULT_SECRET_TIMEOUT)
        if not sample:
            return []
        try:
            text = sample.decode("utf-8", errors="ignore")
        except Exception:
            return []
        keywords = self._scan_text(text)
        findings = []
        for keyword in set(keywords):
            findings.append(SecurityFinding(path="", reason=f"Sensitive content detected: {keyword}"))
        return findings

    def evaluate_path(self, path: Path) -> SecurityReport:
        normalized_path = str(path).replace("\\", "/").lower()
        ext = path.suffix.lower()
        findings = self._evaluate_entry(normalized_path, ext)
        if self.secret_scan_enabled and path.is_file():
            try:
                with path.open("rb") as handle:
                    content_findings = self._inspect_content(handle)
                    for finding in content_findings:
                        finding.path = normalized_path
                    findings.extend(content_findings)
            except OSError:
                findings.append(SecurityFinding(path=normalized_path, reason="Failed to access file for scanning"))
        return SecurityReport(findings=findings, allow_sensitive_uploads=self.allow_sensitive_uploads)

    def evaluate_archive(self, archive_path: Path) -> SecurityReport:
        findings: List[SecurityFinding] = []
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    entry_path = info.filename.replace("\\", "/")
                    ext = Path(entry_path).suffix.lower()
                    entry_findings = self._evaluate_entry(entry_path.lower(), ext)
                    if entry_findings:
                        for finding in entry_findings:
                            finding.path = entry_path
                        findings.extend(entry_findings)
                    if self.secret_scan_enabled:
                        try:
                            with archive.open(info) as handle:
                                content_findings = self._inspect_content(handle)
                                for finding in content_findings:
                                    finding.path = entry_path
                                findings.extend(content_findings)
                        except OSError:
                            findings.append(SecurityFinding(path=entry_path, reason="Unable to read zipped file for scanning"))
        except zipfile.BadZipFile:
            findings.append(SecurityFinding(path=str(archive_path), reason="Archive is corrupted"))
        return SecurityReport(findings=findings, allow_sensitive_uploads=self.allow_sensitive_uploads)


def policy_from_settings(settings, context: str) -> SecurityPolicy:
    prefix = "diag" if context == "diagnostics" else "in"
    allow_ext = getattr(settings, f"allow_extensions_{prefix}", []) or []
    deny_ext = getattr(settings, f"deny_extensions_{prefix}", []) or []
    allow_paths = getattr(settings, f"allow_paths_{prefix}", []) or []
    deny_paths = getattr(settings, f"deny_paths_{prefix}", []) or []
    return SecurityPolicy(
        context=context,
        allow_extensions=allow_ext,
        deny_extensions=deny_ext,
        allow_paths=allow_paths,
        deny_paths=deny_paths,
        secret_scan_enabled=settings.secret_scan_enabled,
        allow_sensitive_uploads=settings.allow_sensitive_uploads,
    )


def record_security_event(
    run: RunArtifacts, scope: str, target_path: str, report: SecurityReport, *, blocked: bool
) -> None:
    payload = {
        "action": "security_blocked" if blocked else "security_warning",
        "scope": scope,
        "target": target_path,
        "findings": [finding.__dict__ for finding in report.findings],
        "blocked": blocked,
    }
    log_file_operation(run, payload)
    security_dir = Path(run.log_dir) / "security"
    security_dir.mkdir(parents=True, exist_ok=True)
    events_path = security_dir / "events.json"
    try:
        existing = []
        if events_path.exists():
            existing = json.loads(events_path.read_text(encoding="utf-8"))
        existing.append(payload)
        events_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
