from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = BASE_DIR / "backend" / "config.json"
DEFAULT_DATA_DIR = BASE_DIR / "data"


@dataclass
class AppConfig:
    data_dir: Path
    dp_threshold: float = 15.0


def load_config() -> AppConfig:
    data_dir = Path(os.getenv("DATA_DIR")) if os.getenv("DATA_DIR") else None
    if data_dir:
        return AppConfig(data_dir=data_dir)

    if CONFIG_PATH.exists():
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return AppConfig(data_dir=Path(payload.get("data_dir", DEFAULT_DATA_DIR)))

    return AppConfig(data_dir=DEFAULT_DATA_DIR)


def save_config(config: AppConfig) -> None:
    CONFIG_PATH.write_text(
        json.dumps({"data_dir": str(config.data_dir), "dp_threshold": config.dp_threshold}, indent=2),
        encoding="utf-8",
    )
