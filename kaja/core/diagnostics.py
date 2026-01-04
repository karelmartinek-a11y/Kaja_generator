from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Set, Tuple

from .settings import Settings
from .state import SshOptions

try:
    import paramiko
except ImportError:  # pragma: no cover - optional dependency
    paramiko = None


@dataclass
class DiagnosticPackage:
    root: Path
    manifest_path: Path
    submission_path: Path
    metadata: Dict[str, Any]
    notes: List[str]


FOLDER_OVERVIEW = {
    "system": "OS, build, PATH, environment",
    "registry": "Authoritative Windows configuration",
    "filesystem": "Actual files, Python installs, venvs",
    "hardware": "Hardware inventory",
    "storage": "Disk, volumes, SMART",
    "drivers": "Driver and PnP details",
    "processes_services": "Processes, services, startup scheme",
    "network": "Adapters, DNS, routing, firewall",
    "security": "Security posture, policies, certificates",
    "python": "Runtime Python diagnostics",
    "devtools": "Toolchain versions",
    "virtualization": "Hypervisor/features state",
    "wsl": "WSL enumerations",
    "logs": "Event logs and reliability data",
    "checksums": "SHA256 digests of the package",
}


UBUNTU_FOLDER_OVERVIEW = {
    "system": "OS release, kernel, timezone, sysctl and systemd health",
    "hardware": "CPU, memory, firmware and hardware identifiers",
    "storage": "Block devices, mounts and SMART hints",
    "network": "Interfaces, routes, DNS and listening sockets",
    "firewall": "UFW, iptables and nft rules",
    "users_permissions": "User/group inventory, sudoers and umask",
    "processes_services": "Processes, services and startup unit state",
    "packages": "dpkg/apt/snap inventory for key packages",
    "web": "Web roots, asset sizes and headers",
    "nginx": "NGINX binary, config tree and validations",
    "app": "Application directories, units and conf/env hints",
    "python": "Interpreter and pip inventory",
    "database": "PostgreSQL services and configs",
    "certs": "Certificate locations and expiry reports",
    "cron_webhooks": "Crontabs and cron directory listings",
    "logs": "Journal, syslog, auth and kernel tails",
    "virtualization_containers": "Docker/container overview",
    "checksums": "SHA256 digests of captured files",
}

SSH_COMMANDS = [
    ("system/os_release.txt", "cat /etc/os-release", "OS release metadata"),
    ("system/uname.txt", "uname -a", "Kernel and build info"),
    ("system/uptime.txt", "uptime && who -b", "Uptime and last boot"),
    ("system/locale_timezone.txt", "locale && timedatectl", "Locale and timezone"),
    ("system/hostname_hosts.txt", "hostnamectl && cat /etc/hosts && cat /etc/hostname", "Hostname and hosts"),
    ("system/sysctl_all.txt", "sysctl -a", "Sysctl settings"),
    ("system/limits_summary.txt", "ulimit -a && ls /etc/security/limits.conf /etc/security/limits.d 2>/dev/null", "Limits summary"),
    ("system/systemd_failed_units.txt", "systemctl --failed", "Systemd failed units"),
    ("system/systemd_running_units.txt", "systemctl list-units --type=service --state=running", "Running services"),
    ("system/journal_boot_errors.txt", "journalctl -b -p err..alert --no-pager", "Boot errors"),
    ("system/env_root_sanitized.txt", "env | grep -v -E '(PASS|KEY|SECRET|TOKEN|PASSWORD)'", "Sanitized env"),
    ("hardware/cpu.txt", "lscpu", "CPU details"),
    ("hardware/memory_modules.txt", "dmidecode -t memory", "Memory modules"),
    ("hardware/memory_summary.txt", "free -h", "Memory summary"),
    ("storage/volumes.txt", "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE", "Volume map"),
    ("storage/mount_points.txt", "mount | column -t", "Mount table"),
    ("storage/smart_status.txt", "if command -v smartctl >/dev/null 2>&1; then for dev in /dev/sd?; do smartctl -H \"$dev\"; done; else echo 'smartctl missing'; fi", "SMART health"),
    ("network/ipconfig_all.txt", "ip addr", "Interface addresses"),
    ("network/adapters_details.txt", "ip link", "Adapter details"),
    ("network/dns_client_config.txt", "resolvectl status || systemd-resolve --status || cat /etc/resolv.conf", "DNS config"),
    ("network/hosts_file.txt", "cat /etc/hosts", "Hosts file"),
    ("network/routes.txt", "ip route", "Routing table"),
    ("network/listening_sockets.txt", "ss -tunlp", "Listening sockets"),
    ("firewall/ufw_status.txt", "ufw status verbose", "UFW status"),
    ("firewall/iptables_rules.txt", "iptables -S && iptables -L -n -v", "iptables rules"),
    ("firewall/nft_ruleset.txt", "nft list ruleset", "nft ruleset"),
    ("users_permissions/users_groups.txt", "getent passwd && getent group", "Users and groups"),
    ("users_permissions/sudoers_listing.txt", "cat /etc/sudoers && ls /etc/sudoers.d 2>/dev/null", "Sudoers metadata"),
    ("users_permissions/umask.txt", "umask", "Current umask"),
    ("processes_services/process_list.txt", "ps -ef", "Process list"),
    ("processes_services/services_state.txt", "systemctl list-units --type=service --all", "Service states"),
    ("processes_services/startup_items.txt", "systemctl list-unit-files --state=enabled", "Startup units"),
    ("packages/dpkg_list.txt", "dpkg -l", "Installed packages"),
    ("packages/apt_policy_key_pkgs.txt", "apt-cache policy nginx openssl python3 certbot postgresql redis", "Key package policy"),
    ("packages/snap_list.txt", "snap list", "Snap packages"),
    ("web/web_root_overview.txt", "find /var/www /srv/www -maxdepth 3 -type d -print 2>/dev/null", "Web roots"),
    ("web/static_assets_sizes.csv", "du -h --max-depth=2 /var/www /srv/www 2>/dev/null | sort -hr", "Top asset sizes"),
    ("web/web_server_headers_hint.txt", "curl -I http://127.0.0.1 2>&1 || true", "Local headers"),
    ("nginx/nginx_version.txt", "nginx -V", "NGINX version"),
    ("nginx/nginx_test.txt", "nginx -t", "NGINX config test"),
    ("nginx/nginx_conf_tree.txt", "find /etc/nginx -maxdepth 4 -print 2>/dev/null", "NGINX config tree"),
    ("app/app_dirs_overview.txt", "find /srv /opt /var/www ~/apps -maxdepth 2 -type d -print 2>/dev/null", "App directories"),
    ("app/systemd_units_related.txt", "systemctl list-unit-files | grep -E 'gunicorn|uvicorn|celery|worker' || true", "App units"),
    ("app/app_env_files_found.txt", "find /srv /opt /var/www ~/apps -type f \\( -name '*.env' -o -name 'config*.yml' -o -name 'settings.py' \\) -print -exec ls -l {} \\; 2>/dev/null", "App env/config files"),
    ("python/where_python.txt", "which python && which python3", "Interpreter location"),
    ("python/py_launcher_list.txt", "python3 -m pip --version && pip3 --version", "Pip versions"),
    ("python/interpreters_inventory.csv", "python3 -c \\\"import json,sys; print(json.dumps({'python': sys.executable, 'paths': sys.path}))\\\"", "Interpreter inventory"),
    ("database/postgres_version.txt", "psql --version", "Postgres version"),
    ("database/postgres_service_status.txt", "systemctl status postgresql --no-pager", "Postgres service"),
    ("database/postgres_conf_locations.txt", "find /etc/postgresql -name 'postgresql.conf' -o -name 'pg_hba.conf' -print 2>/dev/null", "Postgres config"),
    ("certs/cert_locations.txt", "find /etc/letsencrypt /etc/ssl /etc/pki -maxdepth 3 -type f \\( -name '*.pem' -o -name '*.crt' \\) -print 2>/dev/null", "Certificate files"),
    ("certs/certbot_status.txt", "certbot certificates || echo 'certbot missing'", "Certbot certificates"),
    ("certs/cert_expiry_report.txt", "for cert in /etc/letsencrypt/live/*/cert.pem; do echo CERT: $cert; openssl x509 -enddate -noout -in \\\"$cert\\\"; done 2>/dev/null", "Cert expiry"),
    ("cron_webhooks/crontab_root.txt", "crontab -l", "Root crontab"),
    ("cron_webhooks/crontab_users_listing.txt", "ls /var/spool/cron/crontabs 2>/dev/null", "User crontabs"),
    ("cron_webhooks/system_cron_dirs_tree.txt", "ls /etc/cron.* 2>/dev/null", "Cron directories"),
    ("logs/journal_nginx_last500.txt", "journalctl -u nginx -n 500 --no-pager", "NGINX journal tail"),
    ("logs/journal_app_last500.txt", "journalctl -n 500 --no-pager", "General journal tail"),
    ("logs/journal_db_last500.txt", "journalctl -u postgresql -n 500 --no-pager", "DB journal tail"),
    ("logs/syslog_tail.txt", "tail -n 200 /var/log/syslog", "Syslog tail"),
    ("logs/auth_log_tail.txt", "tail -n 200 /var/log/auth.log", "Auth log tail"),
    ("logs/kernel_log_tail.txt", "journalctl -k -n 400 --no-pager", "Kernel log tail"),
    ("virtualization_containers/docker_info.txt", "docker info", "Docker info"),
    ("virtualization_containers/docker_ps.txt", "docker ps -a", "Docker containers"),
    ("virtualization_containers/docker_compose_files_found.txt", "find /srv /opt /etc -name 'docker-compose*.yml' -print 2>/dev/null", "Docker Compose files"),
]


def _current_timestamp() -> str:
    return datetime.utcnow().strftime("%Y%m%d-%H%M%S")


def _is_windows() -> bool:
    return platform.system().lower().startswith("win")


def _is_admin() -> bool:
    if not _is_windows():
        return False
    try:
        import ctypes

        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


class DiagnosticsCollector:
    def __init__(
        self,
        *,
        base_out: Path,
        source_root: Path,
        project: str,
        response_id: str,
        diagnostics: Sequence[str],
        settings: Settings,
    ):
        self.base_out = base_out
        self.source_root = source_root
        self.project = project
        self.response_id = response_id
        self.diagnostics = list(diagnostics)
        self.settings = settings
        self.timestamp = _current_timestamp()
        self.root = base_out / f"Diag_{self.timestamp}"
        self.records: List[Dict[str, Any]] = []
        self.notes: List[str] = []
        self.actions: List[str] = []

    def collect(self) -> DiagnosticPackage:
        self.root.mkdir(parents=True, exist_ok=True)
        self._collect_system()
        self._collect_registry()
        self._collect_filesystem()
        self._collect_python()
        self._collect_processes_services()
        self._collect_network()
        self._collect_security()
        self._collect_hardware()
        self._collect_storage()
        self._collect_drivers()
        self._collect_devtools()
        self._collect_virtualization()
        self._collect_wsl()
        self._collect_logs()
        self._write_readme()
        self._write_changelog()
        self._write_checksums()
        manifest_path = self._write_manifest()
        submission_path = self._write_submission(manifest_path)
        metadata = {
            "project": self.project,
            "response_id": self.response_id,
            "captured_at": datetime.utcnow().isoformat(),
            "run_as_admin": _is_admin(),
            "notes": self.notes,
        }
        return DiagnosticPackage(
            root=self.root,
            manifest_path=manifest_path,
            submission_path=submission_path,
            metadata=metadata,
            notes=self.notes.copy(),
        )

    def _ensure_parent(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    def _record_file(self, path: Path, description: str) -> None:
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        rel = str(path.relative_to(self.root).as_posix())
        self.records.append(
            {"path": rel, "description": description, "size": size}
        )

    def _write_text(self, rel_path: str, description: str, content: str) -> Path:
        target = self.root / rel_path
        self._ensure_parent(target)
        target.write_text(content, encoding="utf-8", errors="ignore")
        self.actions.append(f"Wrote {rel_path}")
        self._record_file(target, description)
        return target

    def _run_command(
        self,
        rel_path: str,
        description: str,
        command: Sequence[str] | str,
        *,
        shell: bool = False,
        env: Dict[str, str] | None = None,
    ) -> Path:
        target = self.root / rel_path
        self._ensure_parent(target)
        try:
            result = subprocess.run(
                command if not shell else str(command),
                capture_output=True,
                text=True,
                shell=shell,
                env=env,
                encoding="utf-8",
                errors="replace",
            )
            output = result.stdout or result.stderr or ""
            if result.returncode != 0:
                note = f"{description}: exit {result.returncode}"
                self.notes.append(note)
                output = f"{output}\n\n{note}"
        except FileNotFoundError as exc:
            output = f"Command not found: {command}\n{exc}"
            self.notes.append(f"{description}: {exc}")
        target.write_text(output, encoding="utf-8", errors="ignore")
        self.actions.append(f"{description}: {_render_command(command)}")
        self._record_file(target, description)
        return target

    def _write_placeholder(
        self, rel_path: str, description: str, note: str | None = None
    ) -> Path:
        detail = note or "Data not available."
        content = (
            f"{description}\n\nERROR: {detail}\nGenerated at {datetime.utcnow().isoformat()}."
        )
        return self._write_text(rel_path, description, content)

    def _write_checksums(self) -> None:
        target = self.root / "checksums" / "sha256.txt"
        self._ensure_parent(target)
        lines: List[str] = []
        for record in self.records:
            path = self.root / record["path"]
            digest = hashlib.sha256()
            try:
                digest.update(path.read_bytes())
            except OSError:
                digest = hashlib.sha256(b"")
            lines.append(f"{digest.hexdigest()}  {record['path']}")
        target.write_text("\n".join(lines), encoding="utf-8")
        self._record_file(target, "SHA256 checksums")

    def _write_readme(self) -> None:
        summary = [
            "# README_problem",
            "",
            f"Project: {self.project}",
            f"Response ID: {self.response_id}",
            f"Captured at: {datetime.utcnow().isoformat()}",
            "",
            "## Snapshot intent",
            "This folder contains a Windows diagnostic snapshot generated by Kája according to the FULL Windows Diagnostics specification.",
            "",
            "## Scope",
            "- System overview",
            "- Registry and filesystem inventory",
            "- Python, tooling, network, security, hardware, and log information",
            "",
            "## Notes",
            *([f"- {note}" for note in self.notes] or ["- No notes recorded."]),
        ]
        self._write_text("README_problem.md", "Diagnostic README", "\n".join(summary))

    def _write_changelog(self) -> None:
        if self.actions:
            entries = "\n".join(f"{idx+1}. {action}" for idx, action in enumerate(self.actions[-50:], start=1))
        else:
            entries = "No actions recorded."
        self._write_text(
            "CHANGELOG_last_actions.txt",
            "Changelog of sequential actions",
            entries,
        )

    def _write_manifest(self) -> Path:
        manifest_path = self.root / "MANIFEST.md"
        entries = "\n".join(
            f"- {folder}/ \u2013 {desc}" for folder, desc in FOLDER_OVERVIEW.items()
        )
        files_table = "\n".join(
            f"| {record['path']} | {record['description']} | {record['size']} |"
            for record in self.records
        )
        total_size = sum(record["size"] for record in self.records)
        lines = [
            "# Diagnostic Manifest",
            "",
            f"Generated at: {datetime.utcnow().isoformat()}",
            f"Machine: {platform.node()}",
            f"User: {os.getlogin()}",
            f"PowerShell: {'Available' if _is_windows() else 'Unavailable'}",
            f"Run as Administrator: {'YES' if _is_admin() else 'NO'}",
            "",
            "## Folder Overview",
            entries,
            "",
            "## Files",
            "| File | Description | Size |",
            "|------|-------------|------|",
            files_table or "| (none) | | |",
            "",
            "## Notes",
            "- " + "\n- ".join(self.notes) if self.notes else "- No notes.",
            "",
            "## Integrity",
            f"Total files: {len(self.records)}",
            f"Total size: {total_size} bytes",
            "Optional checksums: checksums/sha256.txt",
        ]
        manifest_path.write_text("\n".join(lines), encoding="utf-8")
        self._record_file(manifest_path, "Diagnostic manifest")
        json_path = self.root / "MANIFEST.json"
        manifesto = {
            "generated_at": datetime.utcnow().isoformat(),
            "machine": platform.node(),
            "user": os.getlogin(),
            "folders": FOLDER_OVERVIEW,
            "files": self.records,
            "notes": self.notes,
            "integrity": {
                "total_files": len(self.records),
                "total_size": total_size,
                "checksums": "checksums/sha256.txt",
            },
        }
        json_path.write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")
        self._record_file(json_path, "Diagnostic manifest (JSON)")
        return manifest_path

    def _write_submission(self, manifest_path: Path) -> Path:
        submission_path = self.root / "submission.json"
        payload = {
            "project": self.project,
            "response_id": self.response_id,
            "manifest": str(manifest_path.name),
            "root": str(self.root.name),
            "notes": self.notes,
            "actions": self.actions,
        }
        submission_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self._record_file(submission_path, "Submission payload")
        return submission_path

    def _collect_system(self) -> None:
        sys_dir = "system"
        self._run_command(f"{sys_dir}/systeminfo.txt", "OS, build, hotfixes, hardware", ["systeminfo"])
        self._run_command(f"{sys_dir}/os_build.txt", "OS edition, build, UBR", ["wmic", "os", "get", "Caption,Version,BuildNumber"])
        self._run_command(f"{sys_dir}/windows_updates_hotfixes.txt", "Installed hotfixes", ["wmic", "qfe", "list", "brief"])
        self._run_command(f"{sys_dir}/timezone_locale.txt", "Timezone and locale", ["tzutil", "/g"])
        self._run_command(
            f"{sys_dir}/uptime_boot.txt",
            "System uptime and boot info",
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "(Get-Uptime).ToString(); Get-CimInstance Win32_OperatingSystem | Select-Object Caption,LastBootUpTime,LastBootUpTimeLocal | Format-List",
            ],
        )
        self._run_command(f"{sys_dir}/power_settings.txt", "Power configuration", ["powercfg", "/query"])
        self._collect_group_policy_html(sys_dir)
        run_context = [
            f"Project: {self.project}",
            f"Response ID: {self.response_id}",
            f"Python: {sys.executable}",
            f"Timestamp: {datetime.utcnow().isoformat()}",
        ]
        self._write_text(f"{sys_dir}/run_context.txt", "Runtime context summary", "\n".join(run_context))
        self._collect_env_files()

    def _collect_env_files(self) -> None:
        sys_dir = "system"
        if _is_windows():
            self._run_command(
                f"{sys_dir}/env_machine.txt",
                "Machine environment variables",
                ["reg", "query", r"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"],
            )
            self._run_command(
                f"{sys_dir}/env_user.txt",
                "User environment variables",
                ["reg", "query", r"HKCU\\Environment"],
            )
        path_values = os.environ.get("PATH", "").split(os.pathsep)
        self._write_text(f"{sys_dir}/path_effective_process.txt", "Effective PATH", "\n".join(path_values))
        machine_path = self._gather_registry_path(r"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment")
        user_path = self._gather_registry_path(r"HKCU\\Environment")
        diff = self._render_path_diff(machine_path, user_path, path_values)
        self._write_text(f"{sys_dir}/path_diff_analysis.txt", "PATH diff analysis", diff)

    def _collect_group_policy_html(self, sys_dir: str) -> None:
        target = self.root / f"{sys_dir}/group_policy_summary.html"
        self._ensure_parent(target)
        try:
            result = subprocess.run(
                ["gpresult", "/H", str(target)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode != 0:
                self.notes.append(f"gpresult exit {result.returncode}")
        except FileNotFoundError as exc:
            self.notes.append(f"gpresult missing: {exc}")
            target.write_text(f"gpresult failed: {exc}", encoding="utf-8", errors="ignore")
        else:
            self.actions.append("gpresult /H")
        self._record_file(target, "Group policy summary (HTML)")

    def _gather_registry_path(self, key: str) -> List[str]:
        if not _is_windows():
            return []
        try:
            result = subprocess.run(
                ["reg", "query", key],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError:
            return []
        paths = []
        for line in result.stdout.splitlines():
            if line.strip().startswith("Path"):
                parts = line.split()
                if parts:
                    paths.append(parts[-1])
        return paths

    def _render_path_diff(self, machine: List[str], user: List[str], runtime: List[str]) -> str:
        lines = []
        lines.append("Runtime PATH entries:")
        lines.extend(runtime or ["(none)"])
        lines.append("")
        lines.append("Machine PATH entries:")
        lines.extend(machine or ["(not available)"])
        lines.append("")
        lines.append("User PATH entries:")
        lines.extend(user or ["(not available)"])
        return "\n".join(lines)

    def _collect_registry(self) -> None:
        reg_dir = "registry"
        keys = [
            (r"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment", "env_machine.reg"),
            (r"HKCU\\Environment", "env_user.reg"),
            (r"HKLM\\SOFTWARE\\Python\\PythonCore", "python_core_hklm.reg"),
            (r"HKLM\\SOFTWARE\\WOW6432Node\\Python\\PythonCore", "python_core_hklm_wow6432.reg"),
            (r"HKCU\\SOFTWARE\\Python\\PythonCore", "python_core_hkcu.reg"),
            (r"HKLM\\SOFTWARE\\Python\\PyLauncher", "pylauncher_hklm.reg"),
            (r"HKCU\\SOFTWARE\\Python\\PyLauncher", "pylauncher_hkcu.reg"),
            (r"HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\python.exe", "app_paths_python_hklm.reg"),
            (r"HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\python.exe", "app_paths_python_hkcu.reg"),
        ]
        for key, rel in keys:
            self._export_registry(key, f"{reg_dir}/{rel}", f"Registry export {key}")
        self._run_command(
            f"{reg_dir}/windowsapps_execution_aliases.txt",
            "WindowsApps execution aliases",
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "if (Test-Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths') {Get-ChildItem 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\App Paths' | ForEach-Object { $_.Name; Get-ItemProperty -Path $_.PSPath | Format-List } } else { 'App Paths registry key missing' }",
            ],
        )
        self._run_command(
            f"{reg_dir}/file_associations_python.reg",
            "Python file associations",
            [
                "cmd",
                "/c",
                "assoc .py && assoc .pyw && ftype Python.File && ftype Python.NoConFile",
            ],
        )
        uninstall_command = (
            "Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* "
            "-ErrorAction SilentlyContinue | Where-Object DisplayName | Sort-Object DisplayName | Format-Table DisplayName,DisplayVersion,Publisher -AutoSize; "
            "Get-ItemProperty HKLM:\\Software\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* "
            "-ErrorAction SilentlyContinue | Where-Object DisplayName | Sort-Object DisplayName | Format-Table DisplayName,DisplayVersion,Publisher -AutoSize"
        )
        self._run_command(
            f"{reg_dir}/uninstall_inventory.txt",
            "Installed Python / runtime inventory",
            [
                "powershell",
                "-NoProfile",
                "-Command",
                uninstall_command,
            ],
        )

    def _export_registry(self, key: str, rel_path: str, description: str) -> None:
        full_path = self.root / rel_path
        self._ensure_parent(full_path)
        try:
            result = subprocess.run(
                ["reg", "export", key, str(full_path), "/y"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode != 0:
                self.notes.append(f"{description} failed with exit {result.returncode}")
        except FileNotFoundError as exc:
            self.notes.append(f"{description}: {exc}")
            full_path.write_text(f"{exc}", encoding="utf-8", errors="ignore")
        finally:
            self.actions.append(description)
            self._record_file(full_path, description)

    def _collect_filesystem(self) -> None:
        fs_dir = "filesystem"
        self._write_python_executables_report(fs_dir)
        self._write_python_install_dirs_tree(fs_dir)
        self._write_project_requirements(fs_dir)
        self._write_userprofile_tree(fs_dir)
        self._write_userprofile_top_sizes(fs_dir)
        self._write_appdata_tree(fs_dir)
        self._write_appdata_top_sizes(fs_dir)
        self._write_known_folders_locations(fs_dir)
        self._write_onedrive_status_hint(fs_dir)
        venvs = self._discover_venvs()
        self._write_venv_candidates(fs_dir, venvs)
        summary_dir = self.root / f"{fs_dir}/venv_tree_summaries"
        for index, venv in enumerate(venvs, start=1):
            name = venv.name or f"venv_{index}"
            content = self._tree_listing(venv, max_depth=2)
            self._write_text(
                f"{fs_dir}/venv_tree_summaries/venv_{name}.txt",
                f"Structure for {venv}",
                content,
            )

    def _write_python_executables_report(self, fs_dir: str) -> None:
        executables = self._list_python_executable_paths()
        lines: List[str] = ["Python executables discovered from PATH and runtime:"]
        if not executables:
            lines.append("(none found)")
        else:
            for path in executables:
                lines.append(str(path))
        content = "\n".join(lines)
        self._write_text(
            f"{fs_dir}/python_executables_found.txt",
            "Python executables found in PATH",
            content,
        )

    def _write_python_install_dirs_tree(self, fs_dir: str) -> None:
        directories = self._gather_python_install_dirs()
        lines: List[str] = []
        if not directories:
            lines.append("No Python install directories detected.")
        else:
            for directory in directories:
                lines.append(f"Root: {directory}")
                lines.append(self._tree_listing(directory, max_depth=2))
                lines.append("")
        content = "\n".join(lines).strip()
        if not content:
            content = "No Python install directories detected."
        self._write_text(
            f"{fs_dir}/python_install_dirs_tree.txt",
            "Tree summary of discovered Python installs",
            content,
        )

    def _write_project_requirements(self, fs_dir: str) -> None:
        matches = sorted(self.source_root.rglob("*requirements*.txt"))
        if not matches:
            content = "No requirements files found."
        else:
            entries: List[str] = []
            for path in matches:
                size = path.stat().st_size if path.exists() else 0
                entries.append(f"{path.relative_to(self.source_root)} ({size} bytes)")
            content = "\n".join(entries)
        self._write_text(
            f"{fs_dir}/project_requirements_found.txt",
            "Requirements files found",
            content,
        )

    def _write_userprofile_tree(self, fs_dir: str) -> None:
        profile = Path.home()
        content = self._tree_listing(profile, max_depth=3)
        if not content:
            content = f"Unable to enumerate {profile}"
        else:
            content = f"Root: {profile}\n{content}"
        self._write_text(
            f"{fs_dir}/userprofile_tree_depth3.txt",
            "USERPROFILE tree depth 3",
            content,
        )

    def _write_userprofile_top_sizes(self, fs_dir: str) -> None:
        profile = Path.home()
        content = self._describe_directory_sizes(profile)
        self._write_text(
            f"{fs_dir}/userprofile_top_sizes.csv",
            "USERPROFILE top-level sizes",
            content,
        )

    def _write_appdata_tree(self, fs_dir: str) -> None:
        roaming = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        locallow = Path.home() / "AppData" / "LocalLow"
        entries = [
            ("AppData\\Roaming", roaming, "appdata_roaming_tree_depth4.txt"),
            ("AppData\\Local", local, "appdata_local_tree_depth4.txt"),
            ("AppData\\LocalLow", locallow, "appdata_locallow_tree_depth4.txt"),
        ]
        for label, path, filename in entries:
            lines: List[str] = [f"Section: {label}"]
            if path.exists():
                lines.append(self._tree_listing(path, max_depth=4))
            else:
                lines.append(f"Path missing: {path}")
            content = "\n".join(lines)
            self._write_text(
                f"{fs_dir}/{filename}",
                f"{label} directory tree",
                content,
            )

    def _write_appdata_top_sizes(self, fs_dir: str) -> None:
        roaming = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        locallow = Path.home() / "AppData" / "LocalLow"
        sections = [
            ("APPDATA", roaming),
            ("LOCALAPPDATA", local),
            ("AppData\\LocalLow", locallow),
        ]
        lines: List[str] = []
        for label, path in sections:
            lines.append(f"--- {label} ---")
            description = self._describe_directory_sizes(path)
            lines.append(description)
        content = "\n".join(lines)
        self._write_text(
            f"{fs_dir}/appdata_top_sizes.csv",
            "AppData directory sizes",
            content,
        )

    def _write_known_folders_locations(self, fs_dir: str) -> None:
        folders = [
            "Desktop",
            "Documents",
            "Downloads",
            "Pictures",
            "Music",
            "Videos",
            "Links",
            "Saved Games",
        ]
        lines: List[str] = []
        for name in folders:
            path = Path.home() / name
            status = "exists" if path.exists() else "missing"
            lines.append(f"{name}: {path} ({status})")
        content = "\n".join(lines)
        self._write_text(
            f"{fs_dir}/known_folders_locations.txt",
            "Known folder locations",
            content,
        )

    def _write_onedrive_status_hint(self, fs_dir: str) -> None:
        hints: List[str] = []
        for var in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
            value = os.environ.get(var)
            if value:
                exists = Path(value).exists()
                hints.append(f"{var}: {value} (exists: {exists})")
        default_path = Path.home() / "OneDrive"
        hints.append(f"Default path check: {default_path} (exists: {default_path.exists()})")
        content = "\n".join(hints)
        self._write_text(
            f"{fs_dir}/onedrive_status_hint.txt",
            "OneDrive status hint",
            content,
        )

    def _write_venv_candidates(self, fs_dir: str, venvs: List[Path]) -> None:
        lines: List[str] = []
        if not venvs:
            lines.append("No virtual environments discovered.")
        else:
            for index, venv in enumerate(venvs, start=1):
                try:
                    size = self._compute_dir_size(venv, max_depth=1)
                except OSError:
                    size = 0
                lines.append(f"{index}. {venv} ({size} bytes approx.)")
        content = "\n".join(lines)
        self._write_text(
            f"{fs_dir}/venv_candidates_found.txt",
            "Virtual environments detected on disk",
            content,
        )

    def _list_python_executable_paths(self) -> List[Path]:
        seen: Set[str] = set()
        executables: List[Path] = []
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        for segment in path_dirs:
            if not segment:
                continue
            directory = Path(segment)
            if not directory.is_dir():
                continue
            for child in directory.iterdir():
                if not child.is_file():
                    continue
                name = child.name.lower()
                if name.startswith("python") and name.endswith(".exe"):
                    resolved = child.resolve()
                    if str(resolved) not in seen:
                        executables.append(resolved)
                        seen.add(str(resolved))
                if name == "py.exe":
                    resolved = child.resolve()
                    if str(resolved) not in seen:
                        executables.append(resolved)
                        seen.add(str(resolved))
        try:
            runtime_exec = Path(sys.executable).resolve()
            seen.add(str(runtime_exec))
            if runtime_exec not in executables:
                executables.append(runtime_exec)
        except Exception:
            pass
        python_prefix = Path(sys.prefix).resolve()
        if python_prefix.exists() and python_prefix not in executables:
            executables.append(python_prefix)
        executables_sorted = sorted(set(executables))
        return executables_sorted

    def _gather_python_install_dirs(self) -> List[Path]:
        executables = self._list_python_executable_paths()
        directories: Set[Path] = set()
        for exe in executables:
            directories.add(exe if exe.is_dir() else exe.parent)
        prefix = Path(sys.prefix).resolve()
        if prefix.exists():
            directories.add(prefix)
        return sorted(directories)

    def _describe_directory_sizes(self, base: Path, *, limit: int = 10) -> str:
        if not base.exists():
            return f"{base} missing"
        entries: List[Tuple[str, int]] = []
        for entry in base.iterdir():
            if not entry.is_dir():
                continue
            try:
                size = self._compute_dir_size(entry, max_depth=3)
            except OSError:
                size = 0
            entries.append((entry.name, size))
        if not entries:
            return "(no subdirectories found)"
        entries.sort(key=lambda item: item[1], reverse=True)
        lines = [f"{name}: {size} bytes" for name, size in entries[:limit]]
        return "\n".join(lines)

    def _compute_dir_size(self, root: Path, *, max_depth: int | None = None) -> int:
        total = 0
        if not root.exists():
            return 0
        root_parts = len(root.parts)
        for dirpath, dirnames, filenames in os.walk(root):
            rel_depth = len(Path(dirpath).parts) - root_parts
            if max_depth is not None and rel_depth > max_depth:
                dirnames[:] = []
                continue
            for filename in filenames:
                try:
                    file_path = Path(dirpath) / filename
                    total += file_path.stat().st_size
                except OSError:
                    continue
        return total

    def _discover_venvs(self) -> List[Path]:
        candidates: List[Path] = []
        search_roots = [self.source_root, Path.home()]
        for root in search_roots:
            if not root.exists():
                continue
            for path in root.rglob("pyvenv.cfg"):
                candidates.append(path.parent)
                if len(candidates) >= 5:
                    break
        return candidates

    def _tree_listing(self, root: Path, *, max_depth: int, prefix: str = "") -> str:
        lines = []
        def walker(current: Path, depth: int, indent: str) -> None:
            if depth > max_depth:
                return
            if not current.exists():
                return
            entries = sorted(current.iterdir(), key=lambda p: p.name)
            for entry in entries:
                lines.append(f"{indent}- {entry.name}")
                if entry.is_dir():
                    walker(entry, depth + 1, indent + "  ")
        walker(root, 0, prefix)
        return "\\n".join(lines) or "(empty)"

    def _collect_python(self) -> None:
        py_dir = "python"
        self._run_command(f"{py_dir}/where_python.txt", "where python executables", ["where", "python"])
        self._run_command(f"{py_dir}/py_launcher_list.txt", "py launcher list", ["py", "-0p"])
        self._run_command(f"{py_dir}/python_version_default.txt", "Default python version", ["python", "--version"])
        self._run_command(f"{py_dir}/pip_version_default.txt", "Default pip version", ["pip", "--version"])
        self._run_command(f"{py_dir}/pip_list_default.txt", "Pip list (default)", ["pip", "list"])
        self._run_command(f"{py_dir}/pip_freeze_default.txt", "Pip freeze (default)", ["pip", "freeze"])
        self._run_command(f"{py_dir}/pip_debug_default.txt", "Pip debug", ["pip", "debug", "--verbose"])
        self._run_command(f"{py_dir}/pip_config_all.txt", "Pip config list", ["pip", "config", "list"])
        sys_path = subprocess.run(
            [sys.executable, "-c", "import json, sys; print(json.dumps(sys.path))"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self._write_text(f"{py_dir}/python_sys_path.json", "Python sys.path", sys_path.stdout)
        site_packages = subprocess.run(
            [sys.executable, "-c", "import site, json; print(json.dumps(site.getsitepackages()))"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self._write_text(f"{py_dir}/python_site_packages.txt", "Site packages locations", site_packages.stdout)
        platform_info = subprocess.run(
            [sys.executable, "-c", "import platform, json; print(json.dumps({'platform': platform.platform(), 'implementation': platform.python_implementation(), 'version': platform.python_version()}))"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self._write_text(f"{py_dir}/python_platform.json", "Platform information", platform_info.stdout)
        venvs = self._discover_venvs()
        for venv in venvs:
            python_exec = venv / "Scripts" / "python.exe" if _is_windows() else venv / "bin" / "python"
            if not python_exec.exists():
                continue
            env = os.environ.copy()
            env["VIRTUAL_ENV"] = str(venv)
            result = subprocess.run(
                [str(python_exec), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )
            relative = venv.name or "venv"
            content = result.stdout or result.stderr or ""
            self._write_text(f"{py_dir}/venv_reports/{relative}__report.json", f"Venv report for {relative}", content)

    def _collect_processes_services(self) -> None:
        self._run_command("processes_services/process_list.txt", "Process list", ["tasklist"])
        self._run_command("processes_services/services_state.txt", "Service query", ["sc", "query", "state=", "all"])
        self._run_command("processes_services/startup_items.txt", "Startup items", ["wmic", "startup", "list", "full"])
        self._run_command("processes_services/scheduled_tasks_summary.txt", "Scheduled tasks", ["schtasks", "/Query", "/FO", "LIST", "/V"])

    def _collect_network(self) -> None:
        self._run_command("network/ipconfig_all.txt", "IP configuration", ["ipconfig", "/all"])
        self._run_command("network/adapters_details.txt", "Adapter details", ["netsh", "interface", "ipv4", "show", "interfaces"])
        self._run_command("network/dns_client_config.txt", "DNS cache", ["ipconfig", "/displaydns"])
        hosts_path = Path(r"C:\Windows\System32\drivers\etc\hosts")
        if hosts_path.exists():
            try:
                content = hosts_path.read_text(encoding="utf-8", errors="replace")
                self._write_text("network/hosts_file.txt", "Hosts file", content)
            except OSError as exc:
                self._write_placeholder(
                    "network/hosts_file.txt",
                    "Hosts file",
                    f"Failed to read {hosts_path}: {exc}",
                )
        else:
            self._write_placeholder(
                "network/hosts_file.txt",
                "Hosts file",
                f"Missing file: {hosts_path}",
            )
        self._run_command("network/routes.txt", "Route print", ["route", "print"])
        self._run_command("network/netstat_ano.txt", "Netstat -ano", ["netstat", "-ano"])
        self._run_command("network/firewall_profiles.txt", "Firewall profiles", ["netsh", "advfirewall", "show", "allprofiles"])
        firewall_export = self.root / "network" / "firewall_rules_export.wfw"
        result = subprocess.run(
            ["netsh", "advfirewall", "export", str(firewall_export)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if firewall_export.exists():
            self._record_file(firewall_export, "Exported firewall rules")
        else:
            detail = f"netsh advfirewall export failed (exit {result.returncode})."
            if result.stdout:
                detail += f"\nstdout: {result.stdout.strip()}"
            if result.stderr:
                detail += f"\nstderr: {result.stderr.strip()}"
            self._write_placeholder(
                "network/firewall_rules_export.wfw",
                "Firewall rules export",
                detail,
            )
        self._run_command("network/winhttp_proxy.txt", "WinHTTP proxy", ["netsh", "winhttp", "show", "proxy"])
        self._run_command("network/internet_proxy_user.txt", "Internet Explorer proxy settings", ["reg", "query", r"HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings"])
        self._run_command("network/wifi_profiles.txt", "Wireless profiles", ["netsh", "wlan", "show", "profiles"])

    def _collect_security(self) -> None:
        self._run_command("security/defender_status.txt", "Defender status", ["powershell", "-NoProfile", "-Command", "Get-MpComputerStatus | Format-List"])
        self._run_command("security/applocker_effective.txt", "AppLocker effective policy", ["powershell", "-NoProfile", "-Command", "Get-AppLockerPolicy -Effective | Format-List"])
        self._run_command("security/uac_settings.txt", "UAC settings", ["powershell", "-NoProfile", "-Command", "Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"])
        self._run_command("security/certificates_machine_summary.txt", "Machine certificates", ["powershell", "-NoProfile", "-Command", "Get-ChildItem Cert:\\LocalMachine\\My | Format-List -Property FriendlyName,Subject,NotAfter"])

    def _collect_hardware(self) -> None:
        self._run_command("hardware/cpu.txt", "CPU details", ["wmic", "cpu", "get", "Name,NumberOfCores,MaxClockSpeed"])
        self._run_command("hardware/memory_modules.txt", "Memory modules", ["wmic", "memorychip", "list", "full"])
        self._run_command("hardware/memory_summary.txt", "Memory summary", ["systeminfo"])
        self._run_command("hardware/motherboard_bios.txt", "Motherboard / BIOS", ["wmic", "baseboard", "get", "Manufacturer,Product,Version"])
        self._run_command("hardware/gpu_adapters.txt", "GPU adapters", ["wmic", "path", "win32_VideoController", "get", "Name"])
        self._run_command("hardware/monitors_displays.txt", "Monitor and display info", ["powershell", "-NoProfile", "-Command", "Get-CimInstance -Namespace root\\wmi -ClassName WmiMonitorID | Format-List"])

    def _collect_storage(self) -> None:
        self._run_command("storage/volumes.txt", "Logical volumes", ["wmic", "logicaldisk", "get", "Name,FileSystem,Size,FreeSpace"])
        self._run_command("storage/mount_points.txt", "Mount points", ["mountvol"])
        self._run_command("storage/smart_status.txt", "Disk SMART status", ["wmic", "diskdrive", "get", "Status"])
        self._run_command("storage/disk_performance_counters.txt", "Disk performance counters", ["typeperf", "-sc", "1", "\\PhysicalDisk(_Total)\\Disk Transfers/sec"])

    def _collect_drivers(self) -> None:
        self._run_command("drivers/driverquery_verbose.txt", "Driverquery verbose", ["driverquery", "/v"])
        self._run_command("drivers/pnp_devices.txt", "PnP devices", ["wmic", "path", "Win32_PnPEntity", "get", "Name,Status"])
        self._run_command("drivers/problem_devices.txt", "Problem devices", ["pnputil", "/enum-devices", "/problem"])
        self._run_command("drivers/signed_drivers.txt", "Installed signed drivers", ["powershell", "-NoProfile", "-Command", "Get-WindowsDriver -Online | Format-List"])

    def _collect_devtools(self) -> None:
        self._run_command("devtools/git_version.txt", "Git version", ["git", "--version"])
        self._run_command("devtools/node_version.txt", "Node.js version", ["node", "--version"])
        self._run_command("devtools/dotnet_info.txt", "dotnet info", ["dotnet", "--info"])
        vcpp_cmd = (
            "Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\VisualStudio\\SxS\\VC7 -ErrorAction SilentlyContinue "
            "| Format-List; "
            "Get-ItemProperty HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\VisualStudio\\SxS\\VC7 -ErrorAction SilentlyContinue "
            "| Format-List"
        )
        self._run_command(
            "devtools/vcpp_runtimes.txt",
            "VC++ redistributables",
            ["powershell", "-NoProfile", "-Command", vcpp_cmd],
        )

    def _collect_virtualization(self) -> None:
        self._run_command(
            "virtualization/hyperv_state.txt",
            "Hyper-V feature state",
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-WindowsOptionalFeature -Online | Where-Object FeatureName -like 'Microsoft-Hyper-V*' | Format-List",
            ],
        )
        self._run_command(
            "virtualization/virtual_machine_platform.txt",
            "Virtual Machine Platform state",
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-WindowsOptionalFeature -Online | Where-Object FeatureName -like 'VirtualMachinePlatform' | Format-List",
            ],
        )
        self._run_command(
            "virtualization/windows_features.txt",
            "Windows optional features",
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-WindowsOptionalFeature -Online | Format-Table FeatureName,State -AutoSize",
            ],
        )

    def _collect_wsl(self) -> None:
        self._run_command("wsl/wsl_status.txt", "WSL status", ["wsl", "--status"])
        self._run_command(
            "wsl/wsl_list_verbose.txt",
            "WSL distro list verbose",
            ["wsl", "--list", "--verbose"],
        )
        self._run_command(
            "wsl/wsl_versions.txt",
            "WSL online versions",
            ["wsl", "--list", "--online"],
        )

    def _collect_logs(self) -> None:
        self._run_command("logs/eventlog_system_last200.txt", "System event log tail", ["wevtutil", "qe", "System", "/c:200", "/rd:true", "/f:text"])
        self._run_command("logs/eventlog_application_last200.txt", "Application event log tail", ["wevtutil", "qe", "Application", "/c:200", "/rd:true", "/f:text"])
        self._run_command("logs/eventlog_security_last50.txt", "Security event log tail", ["wevtutil", "qe", "Security", "/c:50", "/rd:true", "/f:text"])
        self._run_command("logs/wer_crash_list.txt", "Windows error reporting", ["wevtutil", "qe", "System", "/q:\"*[System[Provider[@Name='Windows Error Reporting']]]\"", "/c:50", "/f:text"])
        self._run_command("logs/reliability_monitor_summary.txt", "Reliability history", ["powershell", "-NoProfile", "-Command", "Get-ReliabilityHistory -MaxEvents 20"])
        self._write_windows_setup_logs_hint()

    def _write_windows_setup_logs_hint(self) -> None:
        windows_dir = Path(os.environ.get("windir", "C:\\Windows"))
        panther_dir = windows_dir / "Panther"
        lines: List[str] = [
            f"Windows directory: {windows_dir}",
            f"Panther directory: {panther_dir}",
        ]
        if panther_dir.exists():
            logs = sorted(panther_dir.glob("*.log"))
            if logs:
                for log_path in logs:
                    try:
                        size = log_path.stat().st_size
                        lines.append(f"{log_path.name}: {size} bytes")
                    except OSError:
                        lines.append(f"{log_path.name}: (unreadable)")
            else:
                lines.append("No .log files discovered in Panther.")
            diag_dir = panther_dir / "DiagOutputDir"
            if diag_dir.exists():
                lines.append("DiagOutputDir contents:")
                for entry in sorted(diag_dir.iterdir()):
                    lines.append(f" - {entry.name}")
        else:
            lines.append("Panther path is missing; check C:\\Windows\\Panther for setup logs.")
        lines.append("Collect setupact.log, setuperr.log, diagwrn.log or similar files to include them in the manifest.")
        self._write_text(
            "logs/windows_setup_logs_hint.txt",
            "Hint to Windows setup logs",
            "\n".join(lines),
        )


def _render_command(command: Sequence[str] | str) -> str:
    if isinstance(command, str):
        return command
    return " ".join(str(part) for part in command)


class SshDiagnosticsCollector:
    def __init__(
        self,
        *,
        base_out: Path,
        source_root: Path,
        project: str,
        response_id: str,
        diagnostics: Sequence[str],
        settings: Settings,
        ssh_options: SshOptions,
    ):
        self.base_out = base_out
        self.source_root = source_root
        self.project = project
        self.response_id = response_id
        self.diagnostics = list(diagnostics)
        self.settings = settings
        self.ssh_options = ssh_options
        self.timestamp = _current_timestamp()
        self.root = base_out / f"Diag_SSH_{self.timestamp}"
        self.records: List[Dict[str, Any]] = []
        self.notes: List[str] = []
        self.actions: List[str] = []
        self.remote_root = ""

    def collect(self) -> DiagnosticPackage:
        self.root.mkdir(parents=True, exist_ok=True)
        client = self._connect()
        remote_root = ""
        try:
            remote_root = self._run_remote_script(client)
            sftp = client.open_sftp()
            try:
                self._download_remote_directory(sftp, remote_root, self.root)
            finally:
                sftp.close()
            self.actions.append(f"Downloaded SSH snapshot from {remote_root}")
        finally:
            if remote_root:
                client.exec_command(f"rm -rf '{remote_root}'")
            client.close()
        self.remote_root = remote_root
        self._write_readme()
        self._write_changelog()
        self._write_checksums()
        manifest_path = self._write_manifest()
        submission_path = self._write_submission(manifest_path)
        metadata = {
            "project": self.project,
            "response_id": self.response_id,
            "captured_at": datetime.utcnow().isoformat(),
            "ssh_target": {
                "host": self.ssh_options.host,
                "port": self.ssh_options.port,
                "user": self.ssh_options.user,
                "remote_root": remote_root,
            },
            "diagnostics": self.diagnostics,
            "notes": self.notes,
            "actions": self.actions,
        }
        return DiagnosticPackage(
            root=self.root,
            manifest_path=manifest_path,
            submission_path=submission_path,
            metadata=metadata,
            notes=self.notes.copy(),
        )

    def _connect(self):
        if paramiko is None:
            raise RuntimeError("paramiko is required for SSH diagnostics")
        host = self.ssh_options.host
        if not host:
            raise ValueError("SSH host is required")
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs = {
            "hostname": host,
            "port": self.ssh_options.port or 22,
            "username": self.ssh_options.user or "root",
            "allow_agent": False,
            "look_for_keys": False,
            "timeout": 30,
        }
        if self.ssh_options.key_path:
            kwargs["key_filename"] = self.ssh_options.key_path
        elif self.ssh_options.password:
            kwargs["password"] = self.ssh_options.password
        else:
            kwargs["look_for_keys"] = True
        client.connect(**kwargs)
        return client

    def _run_remote_script(self, client):
        script = self._build_remote_script()
        stdin, stdout, stderr = client.exec_command("bash -s")
        stdin.write(script)
        stdin.channel.shutdown_write()
        stdout_text = stdout.read().decode("utf-8", errors="replace")
        stderr_text = stderr.read().decode("utf-8", errors="replace")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            self.notes.append(f"SSH collector exit {exit_status}")
        if stderr_text.strip():
            self.notes.append(f"SSH stderr: {stderr_text.strip()[:512]}")
        remote_root = self._extract_remote_root(stdout_text)
        if not remote_root:
            remote_root = self._extract_remote_root(stderr_text)
        if not remote_root:
            raise RuntimeError("Remote root path could not be determined")
        return remote_root

    def _build_remote_script(self) -> str:
        lines = [
            "#!/usr/bin/env bash",
            "set -o pipefail",
            "set +e",
            'timestamp=$(date +%Y%m%d-%H%M%S)',
            'remote_root="/root/Diag_${timestamp}"',
            'mkdir -p "$remote_root"',
        ]
        for rel, command, _desc in SSH_COMMANDS:
            parent = os.path.dirname(rel)
            if parent:
                lines.append(f'mkdir -p "$remote_root/{parent}"')
            lines.append(f'({command}) > "$remote_root/{rel}" 2>&1')
        lines.append('echo "REMOTE_ROOT=$remote_root"')
        return "\n".join(lines)

    def _extract_remote_root(self, output: str) -> str:
        for line in output.splitlines():
            if line.startswith("REMOTE_ROOT="):
                return line.split("=", 1)[1].strip()
        return ""

    def _download_remote_directory(self, sftp, remote_path: str, local_path: Path) -> None:
        local_path.mkdir(parents=True, exist_ok=True)
        for entry in sftp.listdir_attr(remote_path):
            remote_item = f"{remote_path}/{entry.filename}"
            target = local_path / entry.filename
            if stat.S_ISDIR(entry.st_mode):
                self._download_remote_directory(sftp, remote_item, target)
                continue
            self._ensure_parent(target)
            try:
                sftp.get(remote_item, str(target))
                self.actions.append(f"Downloaded {remote_item}")
                self._record_file(target, f"SSH capture of {remote_item}")
            except Exception as exc:
                self.notes.append(f"Failed to download {remote_item}: {exc}")

    def _ensure_parent(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

    def _record_file(self, path: Path, description: str) -> None:
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        rel = str(path.relative_to(self.root).as_posix())
        self.records.append({"path": rel, "description": description, "size": size})

    def _write_text(self, rel_path: str, description: str, content: str) -> Path:
        target = self.root / rel_path
        self._ensure_parent(target)
        target.write_text(content, encoding="utf-8", errors="ignore")
        self.actions.append(f"Wrote {rel_path}")
        self._record_file(target, description)
        return target

    def _write_readme(self) -> None:
        entries = [
            "# README_problem",
            "",
            f"Project: {self.project}",
            f"Response ID: {self.response_id}",
            f"Captured at: {datetime.utcnow().isoformat()}",
            "",
            "## Snapshot intent",
            "This folder contains a Ubuntu web server diagnostic snapshot generated by Kája.",
            "",
            "## SSH Target",
            f"- Host: {self.ssh_options.host}",
            f"- Port: {self.ssh_options.port}",
            f"- User: {self.ssh_options.user}",
            "",
            "## Notes",
            *([f"- {note}" for note in self.notes] or ["- No notes recorded."]),
        ]
        self._write_text("README_problem.md", "SSH diagnostic README", "\n".join(entries))

    def _write_changelog(self) -> None:
        if self.actions:
            entries = "\n".join(f"{idx+1}. {action}" for idx, action in enumerate(self.actions[-50:], start=1))
        else:
            entries = "No actions recorded."
        self._write_text(
            "CHANGELOG_last_actions.txt",
            "Changelog of sequential actions",
            entries,
        )

    def _write_checksums(self) -> None:
        target = self.root / "checksums" / "sha256.txt"
        self._ensure_parent(target)
        lines: List[str] = []
        for record in self.records:
            path = self.root / record["path"]
            digest = hashlib.sha256()
            try:
                digest.update(path.read_bytes())
            except OSError:
                digest = hashlib.sha256(b"")
            lines.append(f"{digest.hexdigest()}  {record['path']}")
        target.write_text("\n".join(lines), encoding="utf-8")
        self._record_file(target, "SHA256 checksums")

    def _write_manifest(self) -> Path:
        manifest_path = self.root / "MANIFEST.md"
        entries = "\n".join(f"- {folder}/ – {desc}" for folder, desc in UBUNTU_FOLDER_OVERVIEW.items())
        files_table = "\n".join(f"| {record['path']} | {record['description']} | {record['size']} |" for record in self.records)
        total_size = sum(record["size"] for record in self.records)
        lines = [
            "# Diagnostic Manifest",
            "",
            f"Generated at: {datetime.utcnow().isoformat()}",
            f"Machine: {self.ssh_options.host or 'ubuntu'}",
            f"User: {self.ssh_options.user}",
            f"Remote root: {self.remote_root}",
            f"Run as root: YES",
            "",
            "## Folder Overview",
            entries,
            "",
            "## Files",
            "| File | Description | Size |",
            "|------|-------------|------|",
            files_table or "| (none) | | |",
            "",
            "## Notes",
            "- " + "\n- ".join(self.notes) if self.notes else "- No notes.",
            "",
            "## Integrity",
            f"Total files: {len(self.records)}",
            f"Total size: {total_size} bytes",
            "Optional checksums: checksums/sha256.txt",
        ]
        manifest_path.write_text("\n".join(lines), encoding="utf-8")
        self._record_file(manifest_path, "Diagnostic manifest")
        json_path = self.root / "MANIFEST.json"
        manifesto = {
            "generated_at": datetime.utcnow().isoformat(),
            "machine": self.ssh_options.host or "ubuntu",
            "user": self.ssh_options.user,
            "folders": UBUNTU_FOLDER_OVERVIEW,
            "files": self.records,
            "notes": self.notes,
            "integrity": {
                "total_files": len(self.records),
                "total_size": total_size,
                "checksums": "checksums/sha256.txt",
            },
        }
        json_path.write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")
        self._record_file(json_path, "Diagnostic manifest (JSON)")
        return manifest_path

    def _write_submission(self, manifest_path: Path) -> Path:
        submission_path = self.root / "submission.json"
        payload = {
            "project": self.project,
            "response_id": self.response_id,
            "manifest": str(manifest_path.name),
            "root": str(self.root.name),
            "notes": self.notes,
            "actions": self.actions,
            "ssh_target": {
                "host": self.ssh_options.host,
                "port": self.ssh_options.port,
                "user": self.ssh_options.user,
                "remote_root": self.remote_root,
            },
        }
        submission_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        self._record_file(submission_path, "Submission payload")
        return submission_path


def collect_ssh_diagnostics(
    *,
    base_out: Path,
    source_root: Path,
    project: str,
    response_id: str,
    diagnostics: Sequence[str],
    settings: Settings,
    ssh_options: SshOptions,
) -> DiagnosticPackage:
    collector = SshDiagnosticsCollector(
        base_out=base_out,
        source_root=source_root,
        project=project or "Kája",
        response_id=response_id,
        diagnostics=diagnostics,
        settings=settings,
        ssh_options=ssh_options,
    )
    return collector.collect()


def collect_windows_diagnostics(
    *,
    base_out: Path,
    source_root: Path,
    project: str,
    response_id: str,
    diagnostics: Sequence[str],
    settings: Settings,
) -> DiagnosticPackage:
    collector = DiagnosticsCollector(
        base_out=base_out,
        source_root=source_root,
        project=project or "Kája",
        response_id=response_id,
        diagnostics=diagnostics,
        settings=settings,
    )
    return collector.collect()
