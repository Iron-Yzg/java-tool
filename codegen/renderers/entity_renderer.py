from __future__ import annotations

from codegen.constants import JAVA_TYPE_IMPORTS, SQL_TYPE_TO_MYSQL
from codegen.models import ColumnDefinition, GeneratorConfig, TableDefinition
from codegen.utils import render_imports, snake_to_pascal


def render_entity(config: GeneratorConfig, table: TableDefinition) -> str:
    visible_columns = [
        column for column in table.columns if column.name not in config.ignore_field_set
    ]
    imports = {
        f"{config.base_entity_full_package}.{config.base_entity_name}",
        "lombok.Data",
        "lombok.EqualsAndHashCode",
        "org.dromara.autotable.annotation.mysql.MysqlTypeConstant",
        "org.dromara.mpe.autotable.annotation.Column",
        "org.dromara.mpe.autotable.annotation.Table",
    }
    for column in visible_columns:
        java_import = JAVA_TYPE_IMPORTS.get(column.java_type)
        if java_import:
            imports.add(java_import)

    lines = [
        f"package {config.base_package}.{config.entity_package};",
        "",
        render_imports(imports),
        "",
        f"/** {table.comment or f'{table.class_name} entity'} */",
        "@Data",
        "@EqualsAndHashCode(callSuper = true)",
        f'@Table(value = "{escape_java_string(table.name)}", comment = "{escape_java_string(table.comment)}")',
        f"public class {table.class_name} extends {config.base_entity_name} {{",
    ]

    for column in visible_columns:
        lines.extend(["", render_field(column)])

    lines.extend(["", "}"])
    return "\n".join(lines)


def render_field(column: ColumnDefinition) -> str:
    annotation = render_column_annotation(column)
    comment = column.comment or snake_to_pascal(column.name)
    return "\n".join(
        [
            f"    /** {comment} */",
            f"    {annotation}",
            f"    private {column.java_type} {column.field_name};",
        ]
    )


def render_column_annotation(column: ColumnDefinition) -> str:
    sql_type = column.sql_type.split("(", 1)[0].lower()
    mysql_type = SQL_TYPE_TO_MYSQL.get(sql_type, "VARCHAR")
    parts = [f"type = MysqlTypeConstant.{mysql_type}"]
    if column.length and sql_type in {"char", "varchar"}:
        parts.append(f"length = {column.length}")
    if not column.nullable:
        parts.append("notNull = true")
    if column.default_value is not None:
        parts.append(f'defaultValue = "{escape_java_string(column.default_value)}"')
    if column.comment:
        parts.append(f'comment = "{escape_java_string(column.comment)}"')
    return f"@Column({', '.join(parts)})"


def escape_java_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
