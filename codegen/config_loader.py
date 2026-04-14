from __future__ import annotations

import json
import re
from pathlib import Path

from codegen.constants import PACKAGE_KEYS
from codegen.models import GeneratorConfig
from codegen.utils import (
    discover_base_package,
    normalize_request_prefix,
    sanitize_package_segment,
)


class ConfigError(ValueError):
    pass


def load_config(config_path: Path) -> GeneratorConfig:
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    project_module = resolve_project_module(config_path, data)
    packages = (
        data.get("packages", {}) if isinstance(data.get("packages", {}), dict) else {}
    )

    return GeneratorConfig(
        config_path=config_path,
        project_module=project_module,
        base_package=resolve_base_package(data, project_module),
        base_entity_name=str(data.get("base_entity_name", "BaseEntity")).strip()
        or "BaseEntity",
        base_entity_package=str(
            data.get("base_entity_package", "common.entity")
        ).strip()
        or "common.entity",
        request_prefix=normalize_request_prefix(
            str(data.get("request_prefix", data.get("api_prefix", "")))
        ),
        ignore_fields=normalize_ignore_fields(data.get("ignore_fields", [])),
        entity_package=str(packages.get("entity", "entity")).strip() or "entity",
        mapper_package=str(packages.get("mapper", "mapper")).strip() or "mapper",
        service_package=str(packages.get("service", "service")).strip() or "service",
        service_impl_package=str(packages.get("service_impl", "service.impl")).strip()
        or "service.impl",
        controller_package=str(packages.get("controller", "controller")).strip()
        or "controller",
        dto_package=str(packages.get("dto", "dto")).strip() or "dto",
        vo_package=str(packages.get("vo", "vo")).strip() or "vo",
        overwrite_existing=bool(data.get("overwrite_existing", False)),
    )


def resolve_project_module(config_path: Path, data: dict) -> Path:
    raw_value = str(data.get("project_module", "")).strip()
    if not raw_value:
        raise ConfigError("config.json must define project_module")

    module_path = Path(raw_value)
    if module_path.is_absolute():
        return module_path.resolve()
    return (config_path.parent / module_path).resolve()


def resolve_base_package(data: dict, project_module: Path) -> str:
    for key in PACKAGE_KEYS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    discovered = discover_base_package(project_module)
    if discovered:
        return discovered

    parts = [segment for segment in re.split(r"[-_.]+", project_module.name) if segment]
    normalized = ".".join(sanitize_package_segment(segment) for segment in parts)
    return f"com.generated.{normalized or 'module'}"


def normalize_ignore_fields(value: object) -> list[str]:
    if isinstance(value, list):
        items = [str(item).strip() for item in value]
    else:
        items = [item.strip() for item in str(value).split(",")]
    return [item for item in items if item]
