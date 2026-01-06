# Deterministic Audit – 2026-01-06

## Entry point
- `main.py`: registers `Montserrat` (Regular + Bold) from `resources/` before `QApplication` spins (2.04.000) and keeps the bootstrap monochrome while respecting the header/panel requirements from 5.01.000‑5.04.000.

## UI runtime
- `kaja/ui/main_window.py`: rebuilt the header block (program name + version, left-aligned config row with EXIT on the right, status row with thermometer, ETA, percent, time/date) and the workspace sections so every section has the mandated rounded border, white lem spacing, black background, and uppercase titles (2.02.000‑2.05.000, 3.01.000‑3.02.000, 4.02.000‑4.03.000, 5.02.000‑5.04.000, 6.02.000‑6.05.000, 8.00.000). Global stylesheet now enforces the monochrome palette and interactive-state colors for buttons/switches/checks.
- `kaja/ui/dialogs/{api_key,settings,pricing,progress}.py`: these modules reuse the manifest stylesheet so their controls retain the same visual contract. Progress handling now updates the new status bar and keeps the palette deterministic.
- `kaja/ui/flow_layout.py` and `kaja/ui/section_card.py`: flow helpers were audited to ensure they only host the newly styled section widgets without introducing extra colors or decorations.

## Core modules
- `kaja/core/pipeline.py` and `kaja/core/pricing.py`: orchestrate runs and capture receipt/catalog data referenced by the UI.
- `kaja/core/settings.py`, `state.py`, `security.py`, `diagnostics.py`, `log_manager.py`, `path_utils.py`, `openai_client.py`, `diagnostics.py`: handle persistence, security policy enforcement, diagnostics, and OpenAI integration without UI duties.
- `kaja/core/price_catalog.py`, `pricing.py`: keep the stored catalog in sync with the pricing dialog and log contracts.

## Assets
- `resources/montserrat_regular.ttf` and `resources/montserrat_bold.ttf`: include the required Montserrat fonts inside the repo so no system or CDN font loading is necessary (2.04.000).

## Verification
- Ran `python -m compileall kaja` to ensure each module parses cleanly and the deterministic UI can start without syntax errors.
