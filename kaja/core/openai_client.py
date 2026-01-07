from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _normalize_capability_entries(value: Any) -> List[str]:
    items: List[str] = []
    if value is None:
        return items
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        for key in ("type", "name", "id"):
            entry = value.get(key)
            if isinstance(entry, str):
                items.append(entry)
        for key, entry in value.items():
            if isinstance(entry, bool):
                if entry:
                    items.append(str(key))
            elif isinstance(entry, (list, tuple, set, dict)):
                items.extend(_normalize_capability_entries(entry))
        return items
    if isinstance(value, (list, tuple, set)):
        for entry in value:
            items.extend(_normalize_capability_entries(entry))
    return items


def _collect_capability_flags(info: Dict[str, Any], keys: Iterable[str]) -> List[str]:
    flags: List[str] = []
    for key in keys:
        value = info.get(key)
        flags.extend(_normalize_capability_entries(value))
    return [item.strip().lower() for item in flags if isinstance(item, str)]

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    OpenAI = None


class OpenAIClient:
    def __init__(self, api_key: str) -> None:
        if OpenAI is None:
            raise RuntimeError("openai library is not available")
        self._client = OpenAI(api_key=api_key)

    def list_models(self) -> List[str]:
        models = self._client.models.list()
        return [model.id for model in models.data]

    def create_response(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self._client.responses.create(**payload)
        return response.model_dump()

    def upload_file(self, path: Path, purpose: str) -> Dict[str, Any]:
        with path.open("rb") as handle:
            response = self._client.files.create(file=handle, purpose=purpose)
        return response.model_dump()

    def list_files(self) -> List[Dict[str, Any]]:
        response = self._client.files.list()
        return [item.model_dump() for item in response.data]

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        response = self._client.files.delete(file_id)
        return response.model_dump()

    def list_vector_stores(self) -> List[Dict[str, Any]]:
        response = self._client.vector_stores.list()
        return [item.model_dump() for item in response.data]

    def retrieve_vector_store(self, store_id: str) -> Dict[str, Any]:
        response = self._client.vector_stores.retrieve(store_id)
        return response.model_dump()

    def update_vector_store_expiration(self, store_id: str, expires_at: str) -> Dict[str, Any]:
        response = self._client.vector_stores.update(store_id, expires_at=expires_at)
        return response.model_dump()

    def list_vector_store_files(self, store_id: str) -> List[Dict[str, Any]]:
        response = self._client.vector_stores.files.list(vector_store_id=store_id)
        return [item.model_dump() for item in response.data]

    def remove_vector_store_file(self, store_id: str, file_id: str) -> Dict[str, Any]:
        response = self._client.vector_stores.files.delete(vector_store_id=store_id, file_id=file_id)
        return response.model_dump()

    def add_vector_store_file(
        self,
        store_id: str,
        file_id: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        files_api = self._client.vector_stores.files
        if attributes:
            try:
                response = files_api.create(
                    vector_store_id=store_id,
                    file_id=file_id,
                    attributes=attributes,
                )
                return response.model_dump()
            except TypeError:
                pass
        response = files_api.create(vector_store_id=store_id, file_id=file_id)
        return response.model_dump()

    def create_vector_store(self, name: str) -> Dict[str, Any]:
        response = self._client.vector_stores.create(name=name)
        return response.model_dump()

    def retrieve_model(self, model_id: str) -> Dict[str, Any]:
        if not model_id:
            return {}
        models_api = getattr(self._client, "models", None)
        if not models_api:
            return {}
        try:
            response = models_api.retrieve(model_id=model_id)
            return response.model_dump()
        except AttributeError:
            return {}
        except Exception:
            raise

    def get_model_capabilities(self, model_id: str) -> Dict[str, Any]:
        defaults = {
            "supports_temperature": False,
            "supports_file_search": False,
            "supports_vector_store": False,
            "supported_tools": [],
            "supported_parameters": [],
            "resolved": False,
            "source": model_id or "defaults",
        }
        info = self.retrieve_model(model_id)
        if not info:
            return defaults
        tool_flags = _collect_capability_flags(
            info,
            ("supported_tools", "tools", "tool_types", "capabilities", "features"),
        )
        param_flags = _collect_capability_flags(
            info,
            ("supported_parameters", "parameters", "capabilities"),
        )
        supports_temperature = False
        if param_flags:
            supports_temperature = "temperature" in param_flags
        else:
            capabilities_blob = info.get("capabilities")
            if isinstance(capabilities_blob, dict) and "temperature" in capabilities_blob:
                supports_temperature = bool(capabilities_blob.get("temperature"))
        supports_file_search = bool({"file_search", "tool_file_search"} & set(tool_flags))
        supports_vector_store = bool({"vector_store", "tool_vector_store"} & set(tool_flags))
        resolved = bool(
            tool_flags
            or param_flags
            or any(
                key in info
                for key in (
                    "capabilities",
                    "supported_tools",
                    "tools",
                    "tool_types",
                    "features",
                    "supported_parameters",
                    "parameters",
                )
            )
        )
        return {
            "supports_temperature": supports_temperature,
            "supports_file_search": supports_file_search,
            "supports_vector_store": supports_vector_store,
            "supported_tools": sorted(set(tool_flags)),
            "supported_parameters": sorted(set(param_flags)),
            "resolved": resolved,
            "source": info.get("id") or model_id,
        }

    def list_batch_jobs(self) -> List[Dict[str, Any]]:
        for attr in ("batch_jobs", "batches", "jobs"):
            manager = getattr(self._client, attr, None)
            if manager is None:
                continue
            try:
                response = manager.list()
                items = getattr(response, "data", [])
                return [item.model_dump() for item in items]
            except AttributeError:
                continue
            except Exception:
                break
        return []

    def create_batch_job(
        self,
        input_file_id: str,
        *,
        endpoint: str = "/v1/responses",
        completion_window: str = "24h",
    ) -> Dict[str, Any]:
        for attr in ("batches", "batch_jobs", "jobs"):
            manager = getattr(self._client, attr, None)
            if manager is None:
                continue
            try:
                response = manager.create(
                    input_file_id=input_file_id,
                    endpoint=endpoint,
                    completion_window=completion_window,
                )
                return response.model_dump()
            except TypeError:
                try:
                    response = manager.create(
                        input_file_id=input_file_id,
                        endpoint=endpoint,
                    )
                    return response.model_dump()
                except TypeError:
                    continue
            except AttributeError:
                continue
        raise RuntimeError("Batch API is not available in the OpenAI client")

    def retrieve_batch_job(self, batch_id: str) -> Dict[str, Any]:
        for attr in ("batches", "batch_jobs", "jobs"):
            manager = getattr(self._client, attr, None)
            if manager is None:
                continue
            try:
                response = manager.retrieve(batch_id)
                return response.model_dump()
            except AttributeError:
                continue
        raise RuntimeError("Batch API is not available in the OpenAI client")

    def download_file(self, file_id: str) -> bytes:
        try:
            response = self._client.files.content(file_id)
        except AttributeError:
            response = self._client.files.retrieve_content(file_id)
        if hasattr(response, "read"):
            return response.read()
        if isinstance(response, bytes):
            return response
        content = getattr(response, "content", None)
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")
        return bytes(content or b"")
