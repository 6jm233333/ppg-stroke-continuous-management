from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _expand_env(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _expand_env(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(v) for v in obj]
    if isinstance(obj, str):
        return os.path.expandvars(obj)
    return obj


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON or YAML configuration and expand environment variables."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    elif path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required for YAML configuration files.") from exc
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    else:
        raise ValueError(f"Unsupported config extension: {path.suffix}")

    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a mapping.")
    return _expand_env(data)


def require_path(config: dict[str, Any], *keys: str, must_exist: bool = True) -> Path:
    """Read a nested path from config and optionally require it to exist."""
    node: Any = config
    for key in keys:
        node = node[key]
    path = Path(str(node))
    if must_exist and not path.exists():
        raise FileNotFoundError(path)
    return path


def ensure_dir(path: str | Path) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_json(obj: dict[str, Any], path: str | Path) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
