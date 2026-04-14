from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from codegen.constants import KNOWN_PACKAGE_SUFFIXES


def snake_to_pascal(value: str) -> str:
    return "".join(part.capitalize() for part in re.split(r"[_\-.]+", value) if part)


def snake_to_camel(value: str) -> str:
    pascal = snake_to_pascal(value)
    return lower_first(pascal)


def lower_first(value: str) -> str:
    if not value:
        return value
    return value[0].lower() + value[1:]


def sanitize_package_segment(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "", value).lower()
    return cleaned or "module"


def package_to_path(package_name: str) -> Path:
    return Path(*package_name.split(".")) if package_name else Path()


def render_imports(imports: Iterable[str]) -> str:
    normalized = sorted({item for item in imports if item})
    return "\n".join(f"import {item};" for item in normalized)


def getter_name(field_name: str) -> str:
    return f"get{field_name[0].upper()}{field_name[1:]}" if field_name else "get"


def normalize_request_prefix(value: str) -> str:
    if not value:
        return ""
    prefix = value.strip().strip("/")
    return f"/{prefix}" if prefix else ""


def build_request_path(prefix: str, segment: str) -> str:
    normalized_prefix = normalize_request_prefix(prefix)
    normalized_segment = segment.strip("/")
    if not normalized_prefix:
        return f"/{normalized_segment}" if normalized_segment else "/"
    return (
        f"{normalized_prefix}/{normalized_segment}"
        if normalized_segment
        else normalized_prefix
    )


def discover_base_package(module_root: Path) -> str | None:
    if not module_root.exists():
        return None

    for java_file in sorted(module_root.rglob("*.java")):
        try:
            content = java_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        match = re.search(r"^\s*package\s+([\w.]+);", content, re.MULTILINE)
        if not match:
            continue
        package_name = match.group(1)
        for suffix in KNOWN_PACKAGE_SUFFIXES:
            if package_name.endswith(suffix):
                return package_name[: -len(suffix)]
        return package_name
    return None
