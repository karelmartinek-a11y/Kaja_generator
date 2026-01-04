from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, List

VERSING_SUFFIX_RE = re.compile(r"^(.+)(\d{12})$")


def is_versing_dir(path: Path, root_name: str) -> bool:
    if not path.is_dir():
        return False
    match = VERSING_SUFFIX_RE.match(path.name)
    if not match:
        return False
    return match.group(1) == root_name


def iter_files(root: Path, exclude_names: Iterable[str], root_name: str) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [
            name for name in dirnames
            if name not in exclude_names and not is_versing_dir(current / name, root_name)
        ]
        for filename in filenames:
            files.append(current / filename)
    return files


def create_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
