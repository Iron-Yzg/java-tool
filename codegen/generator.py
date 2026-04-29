from __future__ import annotations

import argparse
from pathlib import Path

from codegen.config_loader import ConfigError, load_config
from codegen.constants import DEFAULT_BASE_ENTITY_FIELDS
from codegen.models import ColumnDefinition, TableDefinition
from codegen.path_resolver import resolve_project_layout
from codegen.renderers.base_entity_renderer import render_base_entity
from codegen.renderers.controller_renderer import render_controller
from codegen.renderers.dto_renderer import (
    render_create_dto,
    render_page_query_dto,
    render_update_dto,
)
from codegen.renderers.entity_renderer import render_entity
from codegen.renderers.mapper_renderer import render_mapper
from codegen.renderers.service_renderer import (
    render_service_impl,
    render_service_interface,
)
from codegen.renderers.vo_renderer import render_vo
from codegen.sql_parser import parse_sql_file
from codegen.utils import package_to_path


class JavaCodeGenerator:
    def __init__(
        self,
        config_path: Path,
        sql_dir: Path,
        overwrite_existing: bool | None = None,
    ) -> None:
        self.config = load_config(config_path)
        if overwrite_existing is not None:
            self.config.overwrite_existing = overwrite_existing
        self.sql_dir = resolve_sql_dir(config_path, sql_dir)
        self.layout = resolve_project_layout(self.config)

    def generate(self) -> list[Path]:
        sql_files = sorted(self.sql_dir.glob("*.sql"))
        if not sql_files:
            raise ConfigError(f"No SQL files found in {self.sql_dir}")

        tables: list[TableDefinition] = []
        for sql_file in sql_files:
            tables.extend(parse_sql_file(sql_file))
        if not tables:
            raise ConfigError("No CREATE TABLE statements were found in the SQL files")

        generated_files: list[Path] = []
        generated_files.extend(self.generate_base_entity(tables))
        for table in tables:
            generated_files.extend(self.generate_table_files(table))
        return generated_files

    def generate_base_entity(self, tables: list[TableDefinition]) -> list[Path]:
        if not self.config.should_generate_base_entity:
            return []

        base_entity_path = (
            self.layout.java_src_dir
            / package_to_path(self.config.base_entity_full_package)
            / f"{self.config.base_entity_name}.java"
        )
        if base_entity_path.exists():
            return []

        column_lookup: dict[str, ColumnDefinition] = {}
        for table in tables:
            for column in table.columns:
                column_lookup.setdefault(column.name, column)

        ordered_columns: list[ColumnDefinition] = []
        for field_name in self.config.ignore_fields:
            column = column_lookup.get(field_name)
            if column is None:
                java_type, comment = DEFAULT_BASE_ENTITY_FIELDS.get(
                    field_name, ("String", field_name)
                )
                column = ColumnDefinition(
                    name=field_name,
                    sql_type=default_sql_type(field_name, java_type),
                    java_type=java_type,
                    comment=comment,
                    nullable=True,
                    length=default_column_length(field_name),
                    primary_key=field_name == "id",
                    auto_increment=field_name == "id",
                )
            ordered_columns.append(column)

        written = self.write_file(
            base_entity_path,
            render_base_entity(self.config, ordered_columns),
            overwrite=False,
        )
        return [written] if written else []

    def generate_table_files(self, table: TableDefinition) -> list[Path]:
        generated: list[Path] = []
        package_root = self.layout.package_root_dir

        # Determine service impl output path and filename
        if self.config.should_merge_service:
            service_impl_dir = package_root / package_to_path(self.config.service_package)
            service_impl_filename = f"{table.class_name}Service.java"
        else:
            service_impl_dir = package_root / package_to_path(self.config.service_impl_package)
            service_impl_filename = f"{table.class_name}ServiceImpl.java"

        file_map: dict[Path, str] = {
            package_root
            / package_to_path(self.config.entity_package)
            / f"{table.class_name}.java": render_entity(self.config, table),
            package_root
            / package_to_path(self.config.mapper_package)
            / f"{table.class_name}Mapper.java": render_mapper(self.config, table),
            service_impl_dir
            / service_impl_filename: render_service_impl(
                self.config, table
            ),
            package_root
            / package_to_path(self.config.controller_package)
            / f"{table.class_name}Controller.java": render_controller(
                self.config, table
            ),
            package_root
            / package_to_path(self.config.dto_package)
            / f"{table.class_name}CreateDTO.java": render_create_dto(
                self.config, table
            ),
            package_root
            / package_to_path(self.config.dto_package)
            / f"{table.class_name}UpdateDTO.java": render_update_dto(
                self.config, table
            ),
            package_root
            / package_to_path(self.config.dto_package)
            / f"{table.class_name}PageQueryDTO.java": render_page_query_dto(
                self.config, table
            ),
            package_root
            / package_to_path(self.config.vo_package)
            / f"{table.class_name}VO.java": render_vo(self.config, table),
        }

        # Only generate service interface when not merged
        if not self.config.should_merge_service:
            file_map[
                package_root
                / package_to_path(self.config.service_package)
                / f"{table.class_name}Service.java"
            ] = render_service_interface(self.config, table)

        for path, content in file_map.items():
            written = self.write_file(
                path, content, overwrite=self.config.overwrite_existing
            )
            if written:
                generated.append(written)
        return generated

    def write_file(self, path: Path, content: str, overwrite: bool) -> Path | None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and not overwrite:
            return None
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        return path


def resolve_sql_dir(config_path: Path, sql_dir: Path) -> Path:
    if sql_dir.is_absolute():
        return sql_dir
    return (config_path.parent / sql_dir).resolve()


def default_sql_type(field_name: str, java_type: str) -> str:
    if field_name == "id":
        return "bigint"
    if java_type == "LocalDateTime":
        return "datetime"
    if java_type == "Long":
        return "bigint"
    return "varchar(32)" if field_name.endswith("_id") else "varchar(255)"


def default_column_length(field_name: str) -> int | None:
    if field_name.endswith("_id"):
        return 32
    if field_name == "remark":
        return 255
    return None


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Spring Boot and MyBatis-Plus boilerplate from SQL"
    )
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    parser.add_argument(
        "--sql-dir", default="sql", help="Directory that stores SQL files"
    )
    overwrite_group = parser.add_mutually_exclusive_group()
    overwrite_group.add_argument(
        "--keep-existing",
        dest="overwrite_existing",
        action="store_false",
        help="Do not overwrite existing generated files (default)",
    )
    overwrite_group.add_argument(
        "--overwrite-existing",
        dest="overwrite_existing",
        action="store_true",
        help="Overwrite existing generated files",
    )
    parser.set_defaults(overwrite_existing=None)
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    generator = JavaCodeGenerator(
        config_path=Path(args.config).resolve(),
        sql_dir=Path(args.sql_dir),
        overwrite_existing=args.overwrite_existing,
    )
    generated_files = generator.generate()
    print(f"Generated {len(generated_files)} files:")
    for path in generated_files:
        print(f"- {path}")
