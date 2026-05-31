#!/usr/bin/env python3
"""
Shared config loader for the content-agent workspace.

Runtime rule:
- config.yaml / config.json is user state.
- config.example.yaml is only a template fallback.
- Skills should read personalized settings from config, not hard-coded markdown.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = ROOT_DIR / "config.yaml"
CONFIG_JSON_PATH = ROOT_DIR / "config.json"
EXAMPLE_CONFIG_PATH = ROOT_DIR / "config.example.yaml"


class ConfigError(RuntimeError):
    pass


def _load_yaml_with_pyyaml(path: Path) -> dict[str, Any] | None:
    try:
        import yaml  # type: ignore
    except Exception:
        return None
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def _load_yaml_with_ruby(path: Path) -> dict[str, Any] | None:
    script = (
        "require 'yaml'; require 'json'; "
        "puts JSON.generate(YAML.load_file(ARGV[0]))"
    )
    try:
        result = subprocess.run(
            ["ruby", "-e", script, str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    return json.loads(result.stdout or "{}")


def _load_yaml(path: Path) -> dict[str, Any]:
    data = _load_yaml_with_pyyaml(path)
    if data is not None:
        return data
    data = _load_yaml_with_ruby(path)
    if data is not None:
        return data
    raise ConfigError(
        f"Cannot parse {path}. Install PyYAML, provide config.json, or run in an environment with Ruby."
    )


def load_config(allow_example: bool = False) -> dict[str, Any]:
    if CONFIG_PATH.exists():
        return _load_yaml(CONFIG_PATH)
    if CONFIG_JSON_PATH.exists():
        return json.loads(CONFIG_JSON_PATH.read_text(encoding="utf-8"))
    if allow_example and EXAMPLE_CONFIG_PATH.exists():
        return _load_yaml(EXAMPLE_CONFIG_PATH)
    raise ConfigError(
        "No user config found. Create config.yaml via onboarding or the local config editor."
    )


def get_path(data: dict[str, Any], path: str, default: Any = None) -> Any:
    cursor: Any = data
    for key in path.split("."):
        if not isinstance(cursor, dict) or key not in cursor:
            return default
        cursor = cursor[key]
    return cursor


def get_route(config: dict[str, Any], route_key: str) -> dict[str, Any]:
    routes = get_path(config, "storage.routes", {}) or {}
    route = routes.get(route_key)
    if not isinstance(route, dict):
        raise ConfigError(f"Missing storage route: {route_key}")
    return route


def get_workspace(config: dict[str, Any], workspace_id: str) -> dict[str, Any]:
    workspaces = get_path(config, "storage.workspaces", []) or []
    for workspace in workspaces:
        if isinstance(workspace, dict) and workspace.get("id") == workspace_id:
            return workspace
    raise ConfigError(f"Missing storage workspace: {workspace_id}")


def resolve_route(config: dict[str, Any], route_key: str) -> dict[str, Any]:
    route = get_route(config, route_key)
    workspace = get_workspace(config, route.get("workspace_id", ""))
    base_path = workspace.get("base_path") or ""
    route_path = route.get("path") or ""
    return {
        "route_key": route_key,
        "provider": workspace.get("provider"),
        "workspace_id": route.get("workspace_id"),
        "workspace_external_id": workspace.get("external_id"),
        "provider_target_id": route.get("provider_target_id"),
        "workspace_base_path": base_path,
        "path": route_path or base_path,
        "resolved_local_path": resolve_local_path(base_path, route_path) if workspace.get("provider") in {"local", "obsidian"} else None,
        "create_mode": route.get("create_mode"),
        "default_title_pattern": route.get("default_title_pattern"),
        "description": route.get("description"),
    }


def resolve_local_path(base_path: str, route_path: str = "") -> str:
    base = Path(base_path or ".")
    if not base.is_absolute():
        base = ROOT_DIR / base
    target = base / route_path if route_path else base
    return str(target.resolve())


def hot_tracker_config(config: dict[str, Any]) -> dict[str, Any]:
    return get_path(config, "hot_tracker", {}) or {}


def video_processing_config(config: dict[str, Any]) -> dict[str, Any]:
    return get_path(config, "video_processing", {}) or {}
