from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .config import AppConfig


class JSONStorage:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.config.data_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.config.data_dir / name

    def read(self, name: str, default: Any) -> Any:
        path = self._path(name)
        if not path.exists():
            self.write(name, default)
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, name: str, payload: Any) -> None:
        path = self._path(name)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def append_operational(self, entry: dict[str, Any]) -> list[dict[str, Any]]:
        data = self.read("operational.json", [])
        data.append(entry)
        self.write("operational.json", data)
        return data

    def update_chemicals(self, chemicals: list[dict[str, Any]]) -> None:
        self.write("chemicals.json", chemicals)

    def append_consumption(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        data = self.read("consumption.json", [])
        timestamp = datetime.utcnow().isoformat()
        for item in items:
            data.append({"timestamp": timestamp, **item})
        self.write("consumption.json", data)
        return data
