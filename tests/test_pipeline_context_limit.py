from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from kaja.core.pipeline import PipelineExecutor
from kaja.core.settings import Settings
from kaja.core.state import RunArtifacts, UiState


def _make_executor(tmp_path: Path) -> PipelineExecutor:
    tmp_path.mkdir(parents=True, exist_ok=True)
    pricing_cache = tmp_path / "pricing_cache.json"
    pricing_cache.write_text(
        json.dumps(
            {
                "source": "tests",
                "verified": False,
                "last_refreshed": datetime.utcnow().isoformat(),
                "models": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    log_dir = tmp_path / "LOG"
    log_dir.mkdir(parents=True, exist_ok=True)
    artifacts = RunArtifacts(run_id="RUN_TEST", log_dir=str(log_dir))
    settings = Settings(db_path=str(tmp_path / "kaja.db"), pricing_cache_ttl_min=999999)
    return PipelineExecutor(tmp_path, artifacts, lambda *_: None, settings=settings)


def test_model_context_limit_supports_gpt_5_1(tmp_path: Path) -> None:
    executor = _make_executor(tmp_path)
    assert executor._model_context_limit("gpt-5.1") >= 32768


def test_maybe_trim_prompt_texts_keeps_a2x_payload_under_gpt_5_1(tmp_path: Path) -> None:
    executor = _make_executor(tmp_path)
    ui_state = UiState(model="gpt-5.1")
    # ~10k tokens worth of input (rough estimate = chars/4).
    input_text = "X" * (10_000 * 4)
    instructions = "A2X test instructions"
    out_instructions, out_input = executor._maybe_trim_prompt_texts(
        "A2X",
        instructions,
        input_text,
        ui_state,
    )
    assert out_instructions == instructions
    assert out_input == input_text

