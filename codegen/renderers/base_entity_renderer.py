from __future__ import annotations

from codegen.constants import DEFAULT_BASE_ENTITY_FIELDS, JAVA_TYPE_IMPORTS
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
    annotation = (
        f'@TableId(value = "{column.name}", type = IdType.{"AUTO" if column.auto_increment else "INPUT"})'
        if column.primary_key
        else f'@TableField("{column.name}")'
    )
    comment = (
        column.comment
        or DEFAULT_BASE_ENTITY_FIELDS.get(
            column.name, (None, snake_to_pascal(column.name))
        )[1]
    )
    return "\n".join(
        [
            f"    /** {comment} */",
            f"    {annotation}",
            f"    private {column.java_type} {column.field_name};",
        ]
    )
