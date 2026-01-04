from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    def add_vector_store_file(self, store_id: str, file_id: str) -> Dict[str, Any]:
        response = self._client.vector_stores.files.create(vector_store_id=store_id, file_id=file_id)
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
