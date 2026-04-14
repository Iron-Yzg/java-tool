from __future__ import annotations

from pathlib import Path

from codegen.models import GeneratorConfig, ProjectLayout
from codegen.utils import package_to_path


def resolve_project_layout(config: GeneratorConfig) -> ProjectLayout:
    module_root = config.project_module
    module_root.mkdir(parents=True, exist_ok=True)

    java_src_dir = (
        find_first_dir(module_root, "src/main/java")
        or module_root / "src" / "main" / "java"
    )

    java_src_dir.mkdir(parents=True, exist_ok=True)

    package_root_dir = java_src_dir / package_to_path(config.base_package)
    package_root_dir.mkdir(parents=True, exist_ok=True)

    return ProjectLayout(
        module_root=module_root,
        java_src_dir=java_src_dir,
        package_root_dir=package_root_dir,
    )


def find_first_dir(root: Path, relative_dir: str) -> Path | None:
    candidates = sorted(root.glob(f"**/{relative_dir}"))
    return candidates[0] if candidates else None
