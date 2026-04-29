from __future__ import annotations

from codegen.constants import (
    DEFAULT_BASE_ENTITY_FIELDS,
    JAVA_TYPE_IMPORTS,
    SQL_TYPE_TO_MYSQL,
)
from codegen.models import ColumnDefinition, GeneratorConfig
from codegen.utils import render_imports, snake_to_pascal


def render_base_entity(config: GeneratorConfig, columns: list[ColumnDefinition]) -> str:
    imports = {
        "com.baomidou.mybatisplus.annotation.IdType",
        "com.baomidou.mybatisplus.annotation.TableField",
        "com.baomidou.mybatisplus.annotation.TableId",
        "java.io.Serial",
        "java.io.Serializable",
        "lombok.Data",
        "org.dromara.autotable.annotation.mysql.MysqlTypeConstant",
        "org.dromara.mpe.autotable.annotation.Column",
    }
    for column in columns:
        java_import = JAVA_TYPE_IMPORTS.get(column.java_type)
        if java_import:
            imports.add(java_import)

    lines = [
        f"package {config.base_entity_full_package};",
        "",
        render_imports(imports),
        "",
        "/** 基础实体 */",
        "@Data",
        f"public class {config.base_entity_name} implements Serializable {{",
        "",
        "    @Serial",
        "    private static final long serialVersionUID = 1L;",
    ]

    for column in columns:
        lines.extend(["", render_field(column)])

    lines.extend(["", "}"])
    return "\n".join(lines)


def render_field(column: ColumnDefinition) -> str:
    comment = (
        column.comment
        or DEFAULT_BASE_ENTITY_FIELDS.get(
            column.name, (None, snake_to_pascal(column.name))
        )[1]
    )
    lines = [f"    /** {comment} */"]
    if column.primary_key:
        lines.append(
            f"    @TableId(type = IdType.{'AUTO' if column.auto_increment else 'ASSIGN_ID'})"
        )
    else:
        lines.append("    @TableField")
        lines.append(f"    {render_column_annotation(column)}")
    lines.append(f"    protected {column.java_type} {column.field_name};")
    return "\n".join(lines)


def render_column_annotation(column: ColumnDefinition) -> str:
    sql_type = column.sql_type.split("(", 1)[0].lower()
    mysql_type = SQL_TYPE_TO_MYSQL.get(sql_type, "VARCHAR")
    parts = [f"type = MysqlTypeConstant.{mysql_type}"]
    if column.length and sql_type in {"char", "varchar"}:
        parts.append(f"length = {column.length}")
    return f"@Column({', '.join(parts)})"
