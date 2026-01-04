from __future__ import annotations

import argparse
from pathlib import Path

from kaja.core.settings import SettingsStore


def ensure_settings_file(root_dir: Path, *, force: bool = False) -> Path:
    root_dir = Path(root_dir).resolve()
    store = SettingsStore(root_dir)
    settings = store.load()
    if force:
        store.save(settings)
    return store.path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or refresh settings.json with default values."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Project root directory containing settings.json.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rewrite settings.json even if it already exists.",
    )
    args = parser.parse_args()
    path = ensure_settings_file(Path(args.root), force=args.force)
    print(f"settings.json ready: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
