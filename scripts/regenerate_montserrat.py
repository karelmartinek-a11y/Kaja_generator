"""Regenerate the static Montserrat Regular/Bold files that the UI ships with.

The source variable font lives under `fonts-repo/ofl/montserrat`. This helper copies
that file for the regular weight and rewrites the metadata needed for the bold
weight so both glyph sets can be registered by PySide6.

Requires `fonttools` (`pip install fonttools`).
"""
from pathlib import Path
from shutil import copy2

from fontTools.ttLib import TTFont

SOURCE = Path("fonts-repo/ofl/montserrat/Montserrat[wght].ttf")
if not SOURCE.exists():
    raise SystemExit(
        f"Source font {SOURCE} not found. Populate `fonts-repo` (e.g., from Google Fonts) before regenerating."
    )

target_dir = Path("resources")
target_dir.mkdir(exist_ok=True)

copy2(SOURCE, target_dir / "montserrat_regular.ttf")

font = TTFont(str(SOURCE))
os2 = font["OS/2"]
os2.usWeightClass = 700
os2.fsSelection |= 0x20
os2.fsSelection &= ~0x40
head = font["head"]
head.macStyle |= 0x1
replacements = {
    1: "BOLD",
    2: "Montserrat",
    4: "Montserrat BOLD",
    6: "Montserrat-Bold",
}
for record in font["name"].names:
    text = replacements.get(record.nameID)
    if not text:
        continue
    try:
        encoding = record.getEncoding()
    except LookupError:
        encoding = "utf-16-be"
    record.string = text.encode(encoding)

font.save(target_dir / "montserrat_bold.ttf")
print("Regenerated Montserrat regular and bold fonts in resources/.")
