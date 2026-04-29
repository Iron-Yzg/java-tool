from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from codegen.utils import lower_first, snake_to_camel, snake_to_pascal


@dataclass
class GeneratorConfig:
    config_path: Path
    project_module: Path
    base_package: str
    base_entity_name: str = "BaseEntity"
    base_entity_package: str = "common.entity"
    base_entity_full_package_override: str = ""
    request_prefix: str = ""
    ignore_fields: list[str] = field(default_factory=list)
    entity_package: str = "entity"
    mapper_package: str = "mapper"
    service_package: str = "service"
    service_impl_package: str = "service.impl"
    controller_package: str = "controller"
    dto_package: str = "dto"
    vo_package: str = "vo"
    overwrite_existing: bool = False

    @property
    def ignore_field_set(self) -> set[str]:
        return set(self.ignore_fields)

    @property
    def base_entity_full_package(self) -> str:
        if self.base_entity_full_package_override:
            return self.base_entity_full_package_override
        return f"{self.base_package}.{self.base_entity_package}"

    @property
    def should_merge_service(self) -> bool:
        return self.service_impl_package == self.service_package

    @property
    def should_generate_base_entity(self) -> bool:
        return not self.base_entity_full_package_override


@dataclass
class ProjectLayout:
    module_root: Path
    java_src_dir: Path
    package_root_dir: Path


@dataclass
class ColumnDefinition:
    name: str
    sql_type: str
    java_type: str
    comment: str
    nullable: bool
    length: int | None = None
    default_value: str | None = None
    primary_key: bool = False
    auto_increment: bool = False

    @property
    def field_name(self) -> str:
        return snake_to_camel(self.name)


@dataclass
class TableDefinition:
    name: str
    comment: str
    columns: list[ColumnDefinition]

    @property
    def class_name(self) -> str:
        return snake_to_pascal(self.name)

    @property
    def entity_var_name(self) -> str:
        return lower_first(self.class_name)

    @property
    def primary_key(self) -> ColumnDefinition | None:
        return next((column for column in self.columns if column.primary_key), None)
