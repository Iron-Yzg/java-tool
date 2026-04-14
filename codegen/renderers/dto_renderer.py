from __future__ import annotations

from codegen.constants import JAVA_TYPE_IMPORTS
from codegen.models import ColumnDefinition, GeneratorConfig, TableDefinition
from codegen.utils import render_imports, snake_to_pascal


def render_create_dto(config: GeneratorConfig, table: TableDefinition) -> str:
    return render_data_class(
        package_name=f"{config.base_package}.{config.dto_package}",
        class_name=f"{table.class_name}CreateDTO",
        class_comment=f"{table.comment or table.class_name}新增参数",
        columns=visible_columns(table, config),
    )


def render_update_dto(config: GeneratorConfig, table: TableDefinition) -> str:
    columns = list(visible_columns(table, config))
    primary_key = table.primary_key
    if primary_key and primary_key.name in config.ignore_field_set:
        columns = [primary_key, *columns]
    return render_data_class(
        package_name=f"{config.base_package}.{config.dto_package}",
        class_name=f"{table.class_name}UpdateDTO",
        class_comment=f"{table.comment or table.class_name}更新参数",
        columns=unique_columns(columns),
    )


def render_page_query_dto(config: GeneratorConfig, table: TableDefinition) -> str:
    columns = list(visible_columns(table, config))
    primary_key = table.primary_key
    if primary_key and primary_key.name in config.ignore_field_set:
        columns = [primary_key, *columns]

    imports = {"lombok.Data"}
    for column in unique_columns(columns):
        java_import = JAVA_TYPE_IMPORTS.get(column.java_type)
        if java_import:
            imports.add(java_import)

    lines = [
        f"package {config.base_package}.{config.dto_package};",
        "",
        render_imports(imports),
        "",
        f"/** {table.comment or table.class_name}分页查询参数 */",
        "@Data",
        f"public class {table.class_name}PageQueryDTO {{",
        "",
        "    /** 页码 */",
        "    private Long pageNum = 1L;",
        "",
        "    /** 每页条数 */",
        "    private Long pageSize = 10L;",
    ]

    for column in unique_columns(columns):
        lines.extend(["", render_dto_field(column)])

    lines.extend(["", "}"])
    return "\n".join(lines)


def render_data_class(
    package_name: str,
    class_name: str,
    class_comment: str,
    columns: list[ColumnDefinition],
) -> str:
    imports = {"lombok.Data"}
    for column in columns:
        java_import = JAVA_TYPE_IMPORTS.get(column.java_type)
        if java_import:
            imports.add(java_import)

    lines = [
        f"package {package_name};",
        "",
        render_imports(imports),
        "",
        f"/** {class_comment} */",
        "@Data",
        f"public class {class_name} {{",
    ]

    for column in columns:
        lines.extend(["", render_dto_field(column)])

    lines.extend(["", "}"])
    return "\n".join(lines)


def render_dto_field(column: ColumnDefinition) -> str:
    comment = column.comment or snake_to_pascal(column.name)
    return "\n".join(
        [
            f"    /** {comment} */",
            f"    private {column.java_type} {column.field_name};",
        ]
    )


def visible_columns(
    table: TableDefinition, config: GeneratorConfig
) -> list[ColumnDefinition]:
    return [
        column for column in table.columns if column.name not in config.ignore_field_set
    ]


def unique_columns(columns: list[ColumnDefinition]) -> list[ColumnDefinition]:
    seen: set[str] = set()
    result: list[ColumnDefinition] = []
    for column in columns:
        if column.name in seen:
            continue
        seen.add(column.name)
        result.append(column)
    return result
