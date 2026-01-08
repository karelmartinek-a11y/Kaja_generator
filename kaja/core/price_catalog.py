from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

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

OFFICIAL_OPENAI_PRICING_URL = "https://openai.com/pricing"


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
        url = self._settings.pricing_url.strip() or OFFICIAL_OPENAI_PRICING_URL
        remote = self._fetch_remote_pricing(url)
        if not remote:
            self._data['source'] = url
            self._data['verified'] = False
            self._data['last_refreshed'] = datetime.utcnow().isoformat()
            self._save_cache()
            return False
        merged = self._merge_remote(remote)
        merged['source'] = url
        merged['last_refreshed'] = datetime.utcnow().isoformat()
        merged['verified'] = True
        self._data = merged
        self._last_error = None
        self._save_cache()
        return True

    def _merge_remote(self, remote: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(DEFAULT_PRICE_TABLE)
        remote_models = remote.get('models')
        if isinstance(remote_models, dict):
            base_models = dict(DEFAULT_PRICE_TABLE['models'])
            base_models.update(remote_models)
            merged['models'] = base_models
        for key, value in remote.items():
            if key == 'models':
                continue
            merged[key] = value
        return merged

    def _fetch_remote_pricing(self, url: str) -> Optional[Dict[str, Any]]:
        if not url:
            self._last_error = "Pricing URL není nastaveno."
            return None
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Kaja/1.0)",
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        }
        try:
            response = httpx.get(url, timeout=15.0, headers=headers, follow_redirects=True)
            response.raise_for_status()
            if self._is_json_response(response):
                return response.json()
            return self._extract_pricing_from_html(response.text)
        except (httpx.HTTPError, httpx.RequestError, ValueError) as exc:
            self._last_error = str(exc)
        return None

    def _is_json_response(self, response: httpx.Response) -> bool:
        content_type = (response.headers.get('content-type') or '').lower()
        return 'application/json' in content_type or response.text.lstrip().startswith('{')

    def _extract_pricing_from_html(self, html: str) -> Optional[Dict[str, Any]]:
        match = re.search(r"({\s*\"models\".*})", html, re.DOTALL)
        if not match:
            return None
        candidate = match.group(1)
        balance = 0
        end = 0
        for idx, ch in enumerate(candidate):
            if ch == '{':
                balance += 1
            elif ch == '}':
                balance -= 1
                if balance == 0:
                    end = idx + 1
                    break
        if balance != 0:
            return None
        try:
            return json.loads(candidate[:end])
        except json.JSONDecodeError:
            return None

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
