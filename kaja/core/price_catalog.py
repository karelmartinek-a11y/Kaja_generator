from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

from .settings import Settings

DEFAULT_PRICE_TABLE: Dict[str, Any] = {
    "models": {
        "default": {
            "input_token_rate": 0.000002,
            "output_token_rate": 0.0000025,
            "vector_store_file_rate": 0.0001,
            "vector_store_gb_rate": 0.0004,
            "file_api_rate": 0.00005,
        },
        "gpt-4o": {
            "input_token_rate": 0.0000025,
            "output_token_rate": 0.000003,
            "vector_store_file_rate": 0.00012,
            "vector_store_gb_rate": 0.00045,
            "file_api_rate": 0.00006,
        },
        "gpt-4o-mini": {
            "input_token_rate": 0.0000018,
            "output_token_rate": 0.000002,
            "vector_store_file_rate": 0.000085,
            "vector_store_gb_rate": 0.00035,
            "file_api_rate": 0.00004,
        },
    },
    "storage_gb_day": 0.00001,
    "tool_call_rate": 0.00002,
    "batch_discount": 1.0,
    "source": "defaults",
    "last_refreshed": None,
    "verified": False,
}


class PriceCatalog:
    def __init__(self, cache_path: Path, settings: Settings) -> None:
        self._cache_path = cache_path
        self._settings = settings
        self._data = self._load_cache()
        self._last_error: str | None = None

    def _load_cache(self) -> Dict[str, Any]:
        if self._cache_path.exists():
            try:
                data = json.loads(self._cache_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return dict(DEFAULT_PRICE_TABLE)

    def _save_cache(self) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache_path.write_text(json.dumps(self._data, ensure_ascii=False, indent=2), encoding="utf-8")

    def refresh(self) -> bool:
        url = self._settings.pricing_url
        if not url:
            self._last_error = "Pricing URL není nastaven"
            self._data["source"] = "defaults"
            self._data["verified"] = False
            self._data["last_refreshed"] = None
            self._save_cache()
            return False
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                raw = response.read()
            remote = json.loads(raw.decode("utf-8"))
            if isinstance(remote, dict):
                merged = dict(DEFAULT_PRICE_TABLE)
                remote_models = remote.get("models")
                if isinstance(remote_models, dict):
                    merged_models = dict(DEFAULT_PRICE_TABLE["models"])
                    merged_models.update(remote_models)
                    merged["models"] = merged_models
                for key, value in remote.items():
                    if key == "models":
                        continue
                    merged[key] = value
                merged["source"] = url
                merged["last_refreshed"] = datetime.utcnow().isoformat()
                merged["verified"] = True
                self._data = merged
                self._last_error = None
                self._save_cache()
                return True
        except (urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
            self._last_error = str(exc)
        except Exception as exc:  # pragma: no cover - best effort
            self._last_error = str(exc)
        self._data["source"] = url
        self._data["verified"] = False
        self._data["last_refreshed"] = self._data.get("last_refreshed")
        self._save_cache()
        return False

    def refresh_if_needed(self, *, force: bool = False) -> bool:
        if force or self.is_stale():
            return self.refresh()
        return False

    def is_stale(self) -> bool:
        last = self._data.get("last_refreshed")
        if not last:
            return True
        try:
            refreshed = datetime.fromisoformat(last)
        except ValueError:
            return True
        ttl = timedelta(minutes=max(1, self._settings.pricing_cache_ttl_min))
        return datetime.utcnow() - refreshed > ttl

    def get_rates(self, model: str | None) -> Dict[str, float]:
        normalized = (model or "default").lower()
        models = self._data.get("models", {})
        rates = models.get(normalized) or models.get("default") or DEFAULT_PRICE_TABLE["models"]["default"]
        storage_rate = float(self._data.get("storage_gb_day", DEFAULT_PRICE_TABLE["storage_gb_day"]))
        tool_rate = float(self._data.get("tool_call_rate", DEFAULT_PRICE_TABLE["tool_call_rate"]))
        batch_discount = float(self._data.get("batch_discount", DEFAULT_PRICE_TABLE["batch_discount"]))
        return {
            **rates,
            "storage_gb_day": storage_rate,
            "tool_call_rate": tool_rate,
            "batch_discount": batch_discount,
        }

    def summary(self) -> Dict[str, Any]:
        return {
            "source": self._data.get("source", "defaults"),
            "last_refreshed": self._data.get("last_refreshed"),
            "verified": bool(self._data.get("verified")),
            "status": self.status_text(),
            "error": self._last_error,
        }

    def status_text(self) -> str:
        if not self._data.get("verified"):
            return "Ceník offline / odhad"
        if self.is_stale():
            return "Ceník starý"
        return "Ceník aktuální"

    def verified(self) -> bool:
        return bool(self._data.get("verified"))

    def last_error(self) -> str | None:
        return self._last_error

    def model_rate_table(self) -> Dict[str, Dict[str, float]]:
        models = self._data.get("models") or DEFAULT_PRICE_TABLE["models"]
        default_model = DEFAULT_PRICE_TABLE["models"]["default"]
        result: Dict[str, Dict[str, float]] = {}
        for name, rates in models.items():
            entry = dict(default_model)
            if isinstance(rates, dict):
                entry.update(rates)
            result[name] = entry
        return result
